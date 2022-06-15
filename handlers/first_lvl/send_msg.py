from operator import itemgetter
from main_files.create_bot import bot
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
import sqlite3
import datetime
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
                             f'{(bold(record))} {day}.{month} в {hour}:{min}')
        await bot.send_message(id, text, parse_mode=ParseMode.MARKDOWN)

    else:
        time = kwargs.get('time')

        text = emoji.emojize(':double_exclamation_mark: Напоминание! '
                             f'{(bold(record))} в {time}.')
        await bot.send_message(id, text, parse_mode=ParseMode.MARKDOWN)


async def send_morning_msg():
    result = check_db()

    res = {}

    for i in result:
        if i['id'] not in res:
            res[i['id']] = []
        new_data = i.copy()
        new_data.pop('id')
        res[i['id']].append(new_data)

    await make_message(res)


def check_db():
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()

    date = datetime.datetime.today().strftime("%d.%m.%Y")

    cursor.execute('SELECT * FROM diary_db WHERE date=? or date=? and notification=?', (date, 'Бессрочно', 0))
    records = cursor.fetchall()

    result = list({})

    if records:
        for row in records:
            result.append({'id': row[0], 'record': row[2], 'time': row[4],
                           'date': row[1]})

            cursor.close()

        return result
    else:
        cursor.close()
        return None


async def make_message(dict):
    text = emoji.emojize(':sun: Доброе утро! Вот ваши дела на сегодня: \n'
                         '                                   \n')
    text_2 = '              \n' \
             'Бессрочные дела:\n' \
             '                \n'

    j = 1
    k = 1

    for id in dict:
        sorted_list = sorted(dict[id], key=itemgetter("date", "time"))
        for value in sorted_list:
            if value['date'] == 'Бессрочно':
                text_2 += f'{k}. {value["record"]}\n'
                k += 1
            else:
                if value['time'] == 0:
                    text += f'{j}. {value["record"]} - {value["date"]}\n'
                    j += 1
                else:
                    text += f'{j}. {value["record"]} - {value["date"]} {value["time"]}\n'
                    j += 1

        print(f'id = {id}, msg = {text + text_2}')

        await bot.send_message(id, text + text_2)
