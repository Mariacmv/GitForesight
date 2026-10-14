from backend.database.connection import DB_PATH, get_connection

print("Caminho:", DB_PATH.resolve())
print("Existe:", DB_PATH.exists())
print("É arquivo:", DB_PATH.is_file())
print("É pasta:", DB_PATH.is_dir())

with get_connection() as con:
    tabelas = con.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """).fetchall()

    print("\nTabelas encontradas:")
    for tabela in tabelas:
        print(tabela["name"])