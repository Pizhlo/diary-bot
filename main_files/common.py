from aiogram import types
from main_files.create_bot import bot
import emoji
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.first_lvl.main_kb import main_kb
from datetime import datetime
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


class MainStates(StatesGroup):
    first_pg = State()


class Doings(StatesGroup):
    record = State()
    date = State()
    time = State()
    number_doing = State()
    acception = State()

    edit_date = State()
    edit_record = State()

    send_mrng_msg = State()

    first_pg = State()

    mornings_doings_text = ''

    record_text = ''
    date_text = ''
    time_text = ''

    doings_dict = dict()


async def error(message: types.Message, e):
    temp_text = text(bold(message.from_user.username))
    await message.answer(
        emoji.emojize(':warning: Произошла какая-то ошибка. Подробности узнавайте у владельца бота!'),
        reply_markup=main_kb)
    await bot.send_message(chat_id='297850814', text=
    emoji.emojize(
        f':warning: В чате с пользователем @{temp_text} произошла '
        f'ошибка: \n' + str(e)), parse_mode=ParseMode.MARKDOWN)


async def send_morning_msg():
    date = datetime.today().date().strftime('%d.%m.%Y')
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM diary_db WHERE date=?', (date,))
    records = cursor.fetchall()

    i = 1
    if records:
        for row in records:
            if row[4]:
                Doings.mornings_doings_text += f'{i}. {row[2]} {row[1]} {row[4]}. \n'
            else:
                Doings.mornings_doings_text += f'{i}. {row[2]} {row[1]}. \n'
            i += 1
        await bot.send_message(records[0][0], f'Привет! На сегодня у тебя запланировано: \n'
                                              f'{Doings.mornings_doings_text}')
    cursor.close()
