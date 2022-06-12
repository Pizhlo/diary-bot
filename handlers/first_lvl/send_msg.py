from main_files.create_bot import bot
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
import emoji
import sqlite3
import datetime
from operator import itemgetter
from itertools import groupby


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

    temp_list = dict()  # для отправки в функцию отправления сообщения
    count_dict = dict()  # для хранения количества уникальных id

    # TODO: нужно отсортировать result по id, чтобы потом передавать в функцию, которая
    # TODO: составляет текст вида: "Ваши дела: 1. .. 2. .. 3. .. Бессрочные: ...

    if result:
        sorted_list = sorted(result, key=itemgetter("id"))  # сортировать по id
        r = groupby(sorted(sorted_list, key=lambda x: x['id']), lambda x: x['id'])  # для подсчета кол-ва id
        for i in range(len(result)):
            print(f"sorted_list[{i}] = {sorted_list[i]}")
        for k, g in r:
            count_dict[k] = len(list(g))
        keys = list(count_dict.keys())

        for key in keys:  # key = id
            for j in range(len(sorted_list)):
                if 'usual_records' in sorted_list[j].keys():
                    temp_list[key] = {sorted_list[j]['usual_records']: {'date': sorted_list[j]['date'],
                                                                        'time': sorted_list[j]['time']}}
                elif 'endless_records' in sorted_list[j].keys():
                    temp_list[key] = {sorted_list[j]['endless_records']: {'date': sorted_list[j]['date'],
                                                                          'time': sorted_list[j]['time']}}
                print("temp list = ", temp_list)




def check_db():
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()

    date = datetime.datetime.today().strftime("%d.%m.%Y")

    cursor.execute('SELECT * FROM diary_db WHERE date=? or date=? and notification=?', (date, 'Бессрочно', 0))
    records = cursor.fetchall()

    result = list({})

    if records:
        for row in records:
            result.append({'id': row[0], 'usual_records': row[2], 'time': row[4],
                           'date': row[1]})

        cursor.close()

        return result
    else:
        cursor.close()
        return None


def make_message(**kwargs):
    text = 'Доброе утро! Вот ваши дела на сегодня: '
    text_2 = '              \n' \
             'Бессрочные дела:\n' \
             '                \n'

    i = 1
    k = 1

    # if 'last' == True:

    return text, text_2
