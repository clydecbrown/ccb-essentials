"""Unit tests"""
import sqlite3
from typing import Optional

import pytest

from ccb_essentials.filesystem import temporary_path, real_path
from ccb_essentials.sqlite3 import Sqlite3, DatabaseMigrationError, DatabaseApplicationIdError, DatabaseVersionError


def _migration_0to1(conn: sqlite3.Connection, db_version: int) -> bool:
    """Test migration."""
    assert db_version == 0
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (test_id int NOT NULL)")
    cursor.execute("INSERT INTO test values (123)")
    return True


def _migration_1to2(conn: sqlite3.Connection, db_version: int) -> bool:
    """Test migration."""
    assert db_version == 1
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test2 (test2_id int NOT NULL)")
    return True


def _test_id(conn: sqlite3.Connection, test_id: int) -> Optional[int]:
    """Select a record from _migration_0to1()."""
    cursor = conn.cursor()
    cursor.execute("select test_id from test where test_id = ?", [test_id])
    result = cursor.fetchone()
    if result and isinstance(result[0], int):
        return result[0]
    return None


def _bad_migration(_conn: sqlite3.Connection, _db_version: int) -> bool:
    """Test migration."""
    return False


class TestSqlite3:
    """Unit tests"""

    @staticmethod
    def test_init() -> None:
        """It should initialize a Sqlite3 class and file on the filesystem."""
        with temporary_path() as path:
            assert not path.is_file()
            db = Sqlite3(path, [])
            assert path.is_file()
            assert db.db_name == str(real_path(path))
            assert db.db_version == 0

    # todo test in :memory: database
    #   sqlite3.connect(":memory:")
    @staticmethod
    def test_migration() -> None:
        """It should initialize a schema."""
        with temporary_path() as path:
            db = Sqlite3(path, [_migration_0to1])
            assert db.db_version == 1
            result = _test_id(db.con, 123)
            assert isinstance(result, int)
            assert result == 123

    @staticmethod
    def test_migration_failed() -> None:
        """It should not advance the schema version if a migration fails."""
        with temporary_path() as path:
            with pytest.raises(DatabaseMigrationError):
                db = Sqlite3(path, [_bad_migration])
                assert db.db_version == 0

    @staticmethod
    def test_future_database() -> None:
        """It should fail when the schema version is greater than the application's version."""
        with temporary_path() as path:
            db = Sqlite3(path, [_migration_0to1, _migration_1to2])
            assert db.db_version == 2
            with pytest.raises(DatabaseVersionError):
                Sqlite3(path, [_migration_0to1])  # implies application version==1

    # todo test db_versions

    @staticmethod
    def test_application_id() -> None:
        """It should set a unique application_id for the database."""
        with temporary_path() as path:
            db = Sqlite3(path, [_migration_0to1])
            assert db.application_id == 0
        with temporary_path() as path:
            application_id = 12345678
            db = Sqlite3(path, [_migration_0to1], application_id=application_id)
            assert db.application_id == application_id

    @staticmethod
    def test_application_id_mismatch() -> None:
        """It should fail if the application_id does not match the database file."""
        with temporary_path() as path:
            application_id = 12345678
            Sqlite3(path, [], application_id=application_id)
            with pytest.raises(DatabaseApplicationIdError):
                Sqlite3(path, [], application_id=application_id + 1)
