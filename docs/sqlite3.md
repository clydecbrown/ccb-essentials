# sqlite3.py

SQLite3 database wrapper with features for database creation, schema evolution, and sanity checking. It supplies sensible defaults for common operations. It has tools to map query results to Python objects, but it is not an ORM. Database queries are handled directly by Python's `sqlite3`, available at `Sqlite3().con`.

## Example Usage

### Connect

#### Open a database connection, creating the database file if needed.

The only required argument is the database to open. It can be a filesystem path or an existing `sqlite3.Connection`.

*python*

```python
db = Sqlite3('/tmp/test.db')
print(db.db_name)  # /tmp/test.db
```

#### Open read-only.

Do this for safety's sake or to work around other applications which might hold a write lock on the database.

*python*

```python
db = Sqlite3('test.db', read_only=True)
```

#### Create a temporary database in memory.

*python*

```python
db_mem = Sqlite3(':memory:')
# or
db_mem = Sqlite3(sqlite3.connect(":memory:"))
```

#### Run sanity checks.

`Sqlite3` applies some sensible settings to all connections. See `Sqlite3()._init_db()`. Some more-expensive checks can be enabled or disabled with `check_db` (`True` by default). See `Sqlite3()._check_db()`.

*python*

```python
db = Sqlite3('test.db', check_db=False)
```

#### Extend Sqlite3.

Subclass `Sqlite3 ` to encapsulate further sanity checks and settings on the `sqlite3` connection. For example:

*python*

```python
class Database(Sqlite3):
    def __init__(self, database_file: Union[str, pathlib.Path]) -> None:
        # PARSE_DECLTYPES enables TIMESTAMP type conversion
        con = sqlite3.connect(str(database_file), detect_types=sqlite3.PARSE_DECLTYPES)
        super().__init__(con)
        self._pragma("PRAGMA journal_mode = WAL", 'wal')
        self._pragma("PRAGMA synchronous = NORMAL")
        self._pragma("PRAGMA fullfsync = TRUE")
        self._pragma("PRAGMA checkpoint_fullfsync = TRUE")
        self.con.commit()

db = Database('extended.db')
```

#### Make sure we aren't reading and writing someone else's database.

Best practice is to set [application_id](https://www.sqlite.org/pragma.html#pragma_application_id) early in the life of the project, and hard-code it in your application. A random integer works. `Sqlite3` will fail to open a database with a different `application_id`, reducing the chance of accidentally editing the wrong database file.

*python*

```python
db1 = Sqlite3('test_id.db', application_id=12345678)  # The ID is written into the headers of test_id.db.
print(db1.application_id)  # 12345678
db2 = Sqlite3('test_id.db', application_id=22446688)  # raises an exception
```

### Apply a schema.

#### Initialize the schema.

*python*

```python
def _migration_0to1(conn: sqlite3.Connection, db_version: int) -> bool:
    assert db_version == 0
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (test_id int NOT NULL)")
    return True

db = Sqlite3('test.db')
print(db.db_version)  # 0
db = Sqlite3('test.db', migrations=[_migration_0to1])
print(db.db_version)  # 1
```

#### Apply schema migrations.

Best practice is never to alter or to remove old migrations after your application has been distributed. Only add new migrations. Each migration will increment `db_version` by 1. When `Sqlite3` encounters a database file with an old schema it will automatically apply migrations to update it to the latest version.

*python*

```python
def _migration_1to2(conn: sqlite3.Connection, db_version: int) -> bool:
    assert db_version == 1
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test2 (test2_id int NOT NULL)")
    return True

db = Sqlite3('test.db', migrations=[_migration_0to1, _migration_1to2])
print(db.db_version)  # 2
```

#### Test schema versions without applying migrations.

A large application may be modular, with schema migrations defined by one instance of `Sqlite3` and other database-accessing code defined in another `Sqlite3`. In this case the latter `Sqlite3` can declare which schema migrations it is aware of without applying any migrations.

*python*

```python
db = Sqlite3('test.db', db_versions=[2])  # v2 is required; a v1 database will raise an exception
```

If the schema has been updated by a newer version of the application, older versions will fail to read the new database file.

*python*

```python
db = Sqlite3('test.db', db_versions=[1])  # Raises an exception if test.db is at version 2
```

### Query the database.

Queries go directly to the underlying `sqlite3` connection.

*python*

```python
db = Sqlite3('test.db')
cursor = db.con.execute("PRAGMA table_list")
for row in cursor.fetchall():
    print(row[0])  # main
                   # temp
```

### Data Modeling:

This is a minimal example to create a database, apply a schema, insert data, query data, and bind the results to a Python object.

*python*

```python
def _migration_0to1(conn: sqlite3.Connection, db_version: int) -> bool:
    assert db_version == 0
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (test_id int NOT NULL, my_field text NOT NULL, PRIMARY KEY (test_id))")
    return True

@dataclass(frozen=True)
class TestData(SqlObjectFrozen):  # SqlObjectMutable is also available
    test_id: int
    my_field: str

    @classmethod
    def from_mapping(cls, fields: Mapping[str, Any]) -> 'TestData':
        return TestData(
            test_id=fields['test_id'],
            my_field=fields['my_field'],
        )

db = Sqlite3('sql_object_test.db', migrations=[_migration_0to1])
with db.con:  # `with` generates a transaction, ensuring that the new row is committed
    result = db.con.execute("INSERT INTO test (test_id, my_field) VALUES (?, ?)", (1, 'hello'))
    assert result.rowcount == 1
row = db.con.execute("SELECT * FROM test").fetchone()
data = TestData.from_mapping(row)
print(data)  # TestData(test_id=1, my_field='hello')
```

### Helper methods.

#### Watch for a locked database.

This is a pre-emptive test for whether another application has locked the database file.

*python*

```python
db = Sqlite3('test.db')
print(db.is_locked)  # False
```

#### Enable trace logging.

*python*

```python
db = Sqlite3('test.db')
db.trace(pathlib.Path('/tmp/test_trace.txt'))
# Subsequent queries are logged to the file.
```

#### Back up the database file.

Take a snapshot of the database and clone it to a new file.

*python*

```python
db = Sqlite3('test.db')
print(db.backup(pathlib.Path('backup.db')))  # True
```
