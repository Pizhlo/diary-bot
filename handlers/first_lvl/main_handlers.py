from aiogram import types
from main_files.common import MainStates
from keyboards.first_lvl.main_kb import main_kb


# @dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer("Привет!"
                         "\nВыбери, что хочешь сделать",
                         reply_markup=main_kb)
    await MainStates.first_pg.set()


def main_handlers_registration(dp):
    dp.register_message_handler(process_start_command, commands=['start'])
