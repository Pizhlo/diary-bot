from aiogram import types
from main_files.create_bot import bot
import emoji
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.first_lvl.main_kb import main_kb


class MainStates(StatesGroup):
    first_pg = State()


async def error(message: types.Message, e):
    temp_text = text(bold(message.from_user.username))
    await message.answer(
        emoji.emojize(':warning: Произошла какая-то ошибка. Подробности узнавайте у владельца бота!'),
        reply_markup=main_kb)
    await bot.send_message(chat_id='297850814', text=
    emoji.emojize(
        f':warning: В чате с пользователем @{temp_text} произошла '
        f'ошибка: \n' + str(e)), parse_mode=ParseMode.MARKDOWN)
