from aiogram import types
from main_files.create_bot import bot
import emoji
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.first_lvl.main_kb import main_kb
from datetime import datetime, timedelta
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
    endless_doings_dict = dict()


async def error(message: types.Message, e):
    temp_text = text(bold(message.from_user.username))
    await message.answer(
        emoji.emojize(':warning: Произошла какая-то ошибка. Подробности узнавайте у владельца бота!'),
        reply_markup=main_kb)
    await MainStates.first_pg.set()
    await bot.send_message(chat_id='297850814', text=
    emoji.emojize(
        f':warning: В чате с пользователем @{temp_text} произошла '
        f'ошибка: \n' + str(e)), parse_mode=ParseMode.MARKDOWN)


def difference_time(time_time):
    time_obj = datetime.strptime(time_time, '%H:%M')

    time = datetime.today().time().strftime('%H:%M')  # string
    time_now = datetime.strptime(time, '%H:%M')  # date

    time_1 = timedelta(hours=time_obj.hour, minutes=time_obj.minute)
    time_2 = timedelta(hours=datetime.now().time().hour, minutes=datetime.now().time().minute)

    if time_obj > time_now:
        print(False)
        return False, time_1, time_2
    else:  # если время уже прошло
        print(True)
        return True, time_1, time_2
