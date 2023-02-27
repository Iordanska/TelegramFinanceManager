from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup

import exceptions
import expenses
from categories import Categories
from config import TOKEN
from db import db_start, create_finance, edit_finance

API_TOKEN = TOKEN


async def on_startup(_):
    await db_start()


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class FGroup(StatesGroup):
    month_limit = State()


def auth(func):
    async def wrapper(message):
        if message['from']['id'] != 5487330376:
            return await message.reply("Access Denied.", reply=False)
        return await func(message)

    return wrapper


@auth
@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    await message.answer(
        "Бот для учёта финансов.\n\n"
        "Введите месячный лимит (минимальный 100).")
    await create_finance()
    await FGroup.month_limit.set()


@dp.message_handler(commands=['month_limit'])
async def update_month_limit(message: types.Message):
    await message.answer(
        "Введите месячный лимит для изменения (минимальный 100).")
    await create_finance()
    await FGroup.month_limit.set()


@dp.message_handler(lambda message: not message.text.isdigit() or int(message.text) < 100, state=FGroup.month_limit)
async def month_limit_invalid(message: types.Message):
    return await message.reply("Неверный ввод, лимит минимум 100.")


@dp.message_handler(state=FGroup.month_limit)
async def set_month_limit(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['month_limit'] = int(message.text)

    await edit_finance(state, data['month_limit'])
    await message.answer(
        f"Добавлен месячный лимит: {data['month_limit']}.\n\n"
        "Добавить расход: 2 метро.\n"
        "Сегодняшняя статистика: /today\n"
        "За текущий месяц: /month\n"
        "Категории трат: /categories"
    )
    await state.finish()


@dp.message_handler(commands=['help'])
async def show_help(message: types.Message):
    await message.answer(
        "Бот для учёта финансов.\n\n"
        "Добавить расход: 2 метро\n"
        "Сегодняшняя статистика: /today\n"
        "За текущий месяц: /month\n"
        "Категории трат: /categories\n"
        "Изменить месячный лимит /month_limit\n"
    )


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n* " + \
                     ("\n* ".join([c.name
                                   + ' (' + ", ".join(c.aliases) + ')'
                                   + (', (обязательный).' if c.is_base_expense else '.') for c in categories]))
    await message.answer(answer_message)


@dp.message_handler()
async def new_expense(message: types.Message):
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return

    answer_message = (
        "Добавлены траты:\n"
        f"{expense.amount} лари на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}"
    )
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup)
