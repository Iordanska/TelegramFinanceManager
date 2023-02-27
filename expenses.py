import db
import re

import exceptions
from categories import Categories
import datetime


class Expense:
    def __init__(self, amount, category_name):
        self.amount = amount
        self.category_name = category_name


class Message:
    def __init__(self, amount, category_name):
        self.amount = amount
        self.category_name = category_name


def _parse_message(raw_message):
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(1) or not regexp_result.group(2) or regexp_result.group(
            2).isspace():
        raise exceptions.NotCorrectMessage(
            "Напишите сообщение в формате, "
            "например:\n2 метро.")

    amount = regexp_result.group(1)
    category_name = regexp_result.group(2).strip().lower()

    return Message(amount=amount,
                   category_name=category_name)


def add_expense(raw_message):
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_name)

    # добавление расхода в базу данных
    inserted_row_id = db.insert("expense", {
        "amount": parsed_message.amount,
        "created": _get_now_datetime(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })

    return Expense(amount=parsed_message.amount,
                   category_name=category.name)


def delete_expense(row_id):
    row_id = int(row_id)
    db.delete("expense", row_id)


def _get_now_datetime():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return now


def get_today_statistics():
    cursor = db.cursor
    cursor.execute("SELECT SUM(amount)"
                   "FROM expense WHERE DATE(created) = DATE('now')")
    result = cursor.fetchone()

    if not result[0]:
        return "Сегодня ещё нет расходов."

    all_today_expenses = result[0]

    cursor.execute("SELECT SUM(amount) "
                   "FROM expense WHERE date(created)=date('now', 'localtime') "
                   "AND category_codename IN (select codename "
                   "FROM category WHERE is_base_expense=true)")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0

    return (f"Расходы сегодня:\n"
            f"Потрачено — {all_today_expenses} лари.\n"
            f"На обязательные траты — {base_today_expenses} лари.\n\n"
            f"За текущий месяц: /month")


def get_month_statistics():
    cursor = db.cursor
    month = _get_now_datetime()[5:7]
    cursor.execute("SELECT SUM(amount)"
                   "FROM expense WHERE date(created) >= date('now','start of month');")

    result = cursor.fetchone()
    if not result[0]:
        return "За текущий месяц ещё нет расходов."

    month_expenses = result[0]

    cursor.execute("SELECT SUM(amount) "
                   "FROM expense WHERE date(created)=date('now', 'localtime') "
                   "AND category_codename IN (select codename "
                   "FROM category WHERE is_base_expense=true)")
    result = cursor.fetchone()
    base_month_expenses = result[0] if result[0] else 0

    return (f"Расходы за текущий месяц ({month}):\n"
            f"Всего — {month_expenses} лари из "
            f"{_get_budget_limit()} лари.\n"
            f"На обязательные траты — {base_month_expenses} лари из "
            f"{_get_budget_limit()} лари.")


def _get_budget_limit():
    return db.fetchall("budget", ["month_limit"])[0]["month_limit"]
