from main_files.create_bot import bot
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
import emoji
import sqlite3
import datetime


async def send_notif(**kwargs):
    id = kwargs.get('id')
    record = kwargs.get('record')

    if kwargs.get('month') != 'everyday':

        month = kwargs.get('month')
        day = kwargs.get('day')
        hour = kwargs.get('hour')
        min = kwargs.get('min')

        text = emoji.emojize(':double_exclamation_mark: Напоминание! '
                             f'{(bold(record))} {day}.{month} в {hour}:{min}')
        await bot.send_message(id, text, parse_mode=ParseMode.MARKDOWN)

    else:
        time = kwargs.get('time')

        text = emoji.emojize(':double_exclamation_mark: Напоминание! '
                             f'{(bold(record))} в {time}.')
        await bot.send_message(id, text, parse_mode=ParseMode.MARKDOWN)


async def send_morning_msg():
    variable, result = check_db()

    sorted_dict = list({})
    sorted_keys = list()

    # TODO: нужно отсортировать result по id, чтобы потом передавать в функцию, которая
    # TODO: составляет текст вида: "Ваши дела: 1. .. 2. .. 3. .. Бессрочные: ...

    for i in range(1, len(result)):
        sorted_keys = sorted(result, key=result[i].get)

    for w in sorted_keys:
        sorted_dict[w] = result[w]

    print(sorted_dict)

    # for i in range(1, len(result)):
    # print(result[i]['id'].sort)


def check_db():
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()

    date = datetime.datetime.today().strftime("%d.%m.%Y")

    cursor.execute('SELECT * FROM diary_db WHERE date=? or date=? and notification=?', (date, 'Бессрочно', 0))
    records = cursor.fetchall()

    result = list()
    x = {'id': int(), 'usual_records': str(), 'endless_records': str(), 'time': str(),
         'date': str()}
    result.append(x)

    if records:
        for row in records:
            if row[1] != 'Бессрочно':
                if row[4] == 0:  # time
                    result.append({'id': row[0], 'usual_records': row[2], 'date': row[1]})
                else:
                    result.append({'id': row[0], 'usual_records': row[2], 'time': row[4],
                                   'date': row[1]})
            else:
                result.append({'id': row[0], 'endless_records': row[2], 'date': row[1]})

        cursor.close()

        return True, result
    else:
        cursor.close()
        return 0, 0


def make_message():
    text = 'Доброе утро! Вот ваши дела на сегодня: '
    text_2 = '              \n' \
             'Бессрочные дела:\n' \
             '                \n'

    i = 1
    k = 1

    return text, text_2
