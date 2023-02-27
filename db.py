import sqlite3
import os


async def db_start():
    global db, cursor
    db = sqlite3.connect(os.path.join("db", "finance.db"))
    cursor = db.cursor()

    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='budget'")
    table_exists = cursor.fetchone()

    if table_exists:
        return

    with open("createdb.sql", "r", encoding="utf8") as f:
        sql = f.read()
    cursor.executescript(sql)
    db.commit()


async def create_finance():
    budget = cursor.execute("SELECT 1 FROM budget").fetchone()
    if not budget:
        cursor.execute("INSERT INTO budget VALUES(?,?)", ('base', ''))
        db.commit()


async def edit_finance(state, month_limit):
    async with state.proxy() as data:
        cursor.execute(f"UPDATE budget SET month_limit = {month_limit}")
        db.commit()


def insert(table, column_values):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    db.commit()


# Возвращает список словарей (столбец 1 : значение 1, столбец 2 : значение)
def fetchall(table, columns):
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result
