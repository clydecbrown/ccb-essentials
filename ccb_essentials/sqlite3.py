"""Connection to a sqlite3 database."""
import atexit
import logging
import sqlite3
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from io import TextIOWrapper
from os import linesep
from pathlib import Path
from sys import argv
from typing import Optional, Union, Text, Callable, List, Any, Tuple, Sequence, Mapping

from ccb_essentials.constant import UTF8

log = logging.getLogger(__name__)

Migration = Callable[[sqlite3.Connection, int], bool]  # a schema definition


class Sqlite3:
    """Connection to a sqlite3 database."""
    con: sqlite3.Connection

    # pylint: disable-next=too-many-positional-arguments
    def __init__(
        self,
        db_con: Union[bytes, Path, Text, sqlite3.Connection],  # Either a path to a file or an open Connection.
        migrations: Optional[List[Migration]] = None,  # Used by an application which defines its own schema.
        db_versions: Optional[Sequence[int]] = None,  # Application reads these versions, without defining migrations.
        application_id: Optional[int] = None,  # Unique ID for each application; the database file must match it.
        log_file: Optional[Path] = None,  # Output for trace logging.
        read_only: bool = False,  # Open a read-only connection, regardless of write locks held by other connections.
        check_db: bool = True,  # Run database optimizations on start.
    ):
        if read_only:
            check_db = False
        if isinstance(db_con, sqlite3.Connection):
            if read_only:
                raise ValueError("can't set read_only on an open connection")
            self.con = db_con
        else:
            database = db_con
            if isinstance(database, Path):
                database = str(database)
            if read_only:
                if isinstance(database, bytes):
                    database = database.decode(UTF8)
                self.con = sqlite3.connect(f'file:{database}?immutable=1', uri=True)
            else:
                self.con = sqlite3.connect(database)
        atexit.register(self.con.close)
        self.con.row_factory = sqlite3.Row

        self._log_file_handle: Optional[TextIOWrapper] = None
        if log_file:
            self.trace(log_file)

        if application_id:
            self._test_application_id(application_id)

        self._init_db()
        if check_db:
            self._check_db()

        if migrations:
            self._run_migrations(migrations)
            if self.db_version != len(migrations):
                raise DatabaseVersionError(
                    f"database {self.db_name} is at unknown version {self.db_version}"
                    f" (hint: try updating {argv[0]})"
                )
            self.con.commit()  # just in case… some pragmas update the database
        if db_versions:
            assert self.db_version in db_versions, f"unknown db_version {self.db_version} for {self.db_name}"

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.db_name})"

    def _pragma(self, cmd: str, expected: Optional[Any] = None) -> None:
        """Apply a pragma setting."""
        result = self.con.execute(cmd).fetchall()
        if expected is None:
            assert result == [], f"pragma {cmd} failed with result {result}"
        else:
            assert len(result) == 1 and result[0][0] == expected, f"pragma {cmd} failed with result {result}"

    def _init_db(self) -> None:
        """Apply a sensible set of default settings for the connection."""
        self._pragma(f"PRAGMA encoding = '{UTF8}'")
        self._pragma("PRAGMA ignore_check_constraints = FALSE")
        self._pragma("PRAGMA foreign_keys = TRUE")

    def _check_db(self) -> None:
        """Run expensive sanity checks."""
        # self._pragma("PRAGMA analysis_limit=1000")  # todo?
        # todo run on connection close https://www.sqlite.org/lang_analyze.html
        self._pragma("PRAGMA optimize")
        self._pragma("PRAGMA integrity_check", "ok")
        self._pragma("PRAGMA foreign_key_check")

    @property
    def db_name(self) -> Optional[str]:
        """Filesystem path to the database file."""
        cursor = self.con.execute("PRAGMA database_list")
        fetchall: List[Tuple[int, str, str]] = cursor.fetchall()
        names = list(map(lambda c: c[2], filter(lambda c: c[1] == 'main', fetchall)))
        return names[0] if len(names) > 0 else None

    @property
    def is_locked(self) -> bool:
        """Look for the external markers of a database lock, without attempting to write to the connection."""
        db_name = self.db_name
        if db_name is None:
            return False
        return Path(db_name + '.lock').exists() or Path(db_name + '-journal').exists()

    @property
    def application_id(self) -> int:
        """Application ID of the database schema.
        https://www.sqlite.org/pragma.html#pragma_application_id
        """
        cursor = self.con.execute("PRAGMA application_id")
        return int(cursor.fetchone()[0])

    def _test_application_id(self, application_id: int) -> None:
        """Verify that `application_id matches the database file.
        This value is expected to be set once, preferably when the database file is initialized."""
        previous = self.application_id
        if previous:
            if previous == application_id:
                return
            raise DatabaseApplicationIdError(
                f"application_id {previous} from {self.db_name} does not match"
                f" runtime application_id {application_id}"
            )

        log.debug("set application_id = %d", application_id)
        self._pragma(f"PRAGMA application_id = {application_id}")
        assert self.application_id == application_id
        self.con.commit()

    @property
    def db_version(self) -> int:
        """Version of the database schema.
        https://www.sqlite.org/pragma.html#pragma_user_version
        """
        cursor = self.con.execute("PRAGMA user_version")
        return int(cursor.fetchone()[0])

    def _set_version(self, version: int) -> None:
        """Setter for `user_version`."""
        log.debug("set user_version = %d", version)
        self._pragma(f"PRAGMA user_version = {version}")
        assert self.db_version == version
        self.con.commit()

    def _run_migrations(self, migrations: List[Migration]) -> None:
        """Roll the database schema forward to the latest version."""
        db_version = self.db_version
        while db_version < len(migrations):
            if db_version == 0:
                log.debug("initializing database %s", str(self.db_name))
            self.con.commit()
            try:
                migrated = migrations[db_version](self.con, db_version)
                self.con.commit()
            except IndexError as e:
                raise DatabaseMigrationError(f"database {self.db_name} is at unknown version {db_version}") from e
            except sqlite3.Error as e:
                self.con.rollback()
                raise DatabaseMigrationError() from e
            if migrated:
                db_version += 1
                self._set_version(db_version)
            else:
                raise DatabaseMigrationError(f"migration for {self.db_name} failed at version {db_version}")

    # todo test with StringIO (in memory)
    def trace(self, log_file: Optional[Path]) -> None:
        """Write SQL traces to a log file."""
        if not log_file:
            self.con.set_trace_callback(None)

        if self._log_file_handle:
            self._log_file_handle.close()
            self._log_file_handle = None

        if not log_file:
            return

        lf = log_file.open('a')
        self._log_file_handle = lf
        log.debug('writing SQL traces to %s', log_file)

        def trace(statement: str) -> None:
            lf.write(f'{datetime.now()} {statement}{linesep}')
        self.con.set_trace_callback(trace)

    def backup(self, backup_file: Path, name: str = 'main') -> bool:
        """Clone this database to the given file."""
        if backup_file.exists():
            log.warning('destination for backup already exists: %s', backup_file)
            return False
        if not backup_file.parent.is_dir():
            backup_file.parent.mkdir(parents=True)
        try:
            backup_db = sqlite3.connect(str(backup_file))
            with backup_db:
                self.con.backup(backup_db, name=name)
            backup_db.close()
        except sqlite3.Error as e:
            log.error(e)
            return False
        return True


class DatabaseApplicationIdError(RuntimeError):
    """Error for mismatched application_id."""


class DatabaseMigrationError(RuntimeError):
    """Error for failed schema migration."""


class DatabaseVersionError(RuntimeError):
    """Error for a schema version which is ahead of the current application."""


@dataclass(frozen=False)
class SqlObjectMutable:
    """Data class representing a row of data in a SQL database, with minimal support for building queries.
    https://docs.python.org/3/library/sqlite3.html#sqlite3-converters
    """

    @property
    def values(self) -> List[Any]:
        """Used in sqlite3.execute() to bind the instance's values to a SQL query."""
        return list(self.__dict__.values())

    @classmethod
    def fields_list(cls) -> List[str]:
        """Helper method."""
        return list(cls.__dict__['__annotations__'].keys())

    @classmethod
    def fields_bindings(cls) -> str:
        """Used to construct a SQL query like "INSERT INTO <table> (<fields_str>) VALUES (<fields_bindings>)"."""
        return ", ".join(map(lambda _: '?', cls.fields_list()))

    @classmethod
    def fields_str(cls) -> str:
        """Used to construct a SQL query like "INSERT INTO <table> (<fields_str>) VALUES (<fields_bindings>)"
        or "SELECT <fields_str> FROM <table>"."""
        return ", ".join(cls.fields_list())

    @classmethod
    @abstractmethod
    def from_mapping(cls, fields: Mapping[str, Any]):  # type: ignore[no-untyped-def]
        """Convert a sqlite3.Row to a concrete instance of this class."""


@dataclass(frozen=True)
class SqlObjectFrozen:
    """Data class representing a row of data in a SQL database, with minimal support for building queries.
    https://docs.python.org/3/library/sqlite3.html#sqlite3-converters
    """

    @property
    def values(self) -> List[Any]:
        """Used in sqlite3.execute() to bind the instance's values to a SQL query."""
        return list(self.__dict__.values())

    @classmethod
    def fields_list(cls) -> List[str]:
        """Helper method."""
        return list(cls.__dict__['__annotations__'].keys())

    @classmethod
    def fields_bindings(cls) -> str:
        """Used to construct a SQL query like "INSERT INTO <table> (<fields_str>) VALUES (<fields_bindings>)"."""
        return ", ".join(map(lambda _: '?', cls.fields_list()))

    @classmethod
    def fields_str(cls) -> str:
        """Used to construct a SQL query like "INSERT INTO <table> (<fields_str>) VALUES (<fields_bindings>)"
        or "SELECT <fields_str> FROM <table>"."""
        return ", ".join(cls.fields_list())

    @classmethod
    @abstractmethod
    def from_mapping(cls, fields: Mapping[str, Any]):  # type: ignore[no-untyped-def]
        """Convert a sqlite3.Row to a concrete instance of this class."""
