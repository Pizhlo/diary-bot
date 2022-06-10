from main_files.create_bot import bot
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
import emoji


async def send_notif(**kwargs):
    id = kwargs.get('id')
    record = kwargs.get('record')

    if kwargs.get('month') != 'everyday':

        month = kwargs.get('month')
        day = kwargs.get('day')
        hour = kwargs.get('hour')
        min = kwargs.get('min')

        text = emoji.emojize(':double_exclamation_mark: Напоминание! '
                             f'{(bold(record))} {day}.{month} {hour}:{min}')
        await bot.send_message(id, text, parse_mode=ParseMode.MARKDOWN)

    else:
        time = kwargs.get('time')

        text = 'Напоминание! ' \
               f'{(bold(record))} {time}.'
        await bot.send_message(id, text, parse_mode=ParseMode.MARKDOWN)


async def send_morning_msg(**kwargs):
    id = kwargs.get('id')
    record = kwargs.get('record')
    date = kwargs.get('date')
