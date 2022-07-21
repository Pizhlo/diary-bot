import emoji
from operator import itemgetter
from aiogram import types
from aiogram_calendar import simple_cal_callback, SimpleCalendar
import sqlite3
from main_files.common import MainStates, error, scheduler, difference_time
from aiogram.dispatcher.filters.state import State, StatesGroup
from main_files.create_bot import bot
from aiogram.dispatcher import FSMContext
from keyboards.first_lvl.notifications_kb import add_notif_kb, edit_kb, acception_kb, dell_all_kb
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta
import time
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Text
from keyboards.first_lvl.main_kb import main_kb
from db.clean_database import delete_notification
from handlers.first_lvl.send_msg import send_notif


class Notifications(StatesGroup):
    record = State()
    date = State()
    time = State()
    number_doing = State()

    first_pg = State()

    edit_date = State()
    edit_record = State()

    record_text = ''
    date_text = ''
    time_text = ''

    notif_dict = dict()


# @dp.message_handler(lambda message: 'Список напоминаний' in message.text)
async def list_of_notif(message: types.Message):
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()

    await Notifications.first_pg.set()

    cursor.execute('SELECT * FROM diary_db WHERE user=? and notification=?', (message.from_user.id, 1))
    records = cursor.fetchall()

    if not records:
        await message.answer('У вас нет напоминаний.')
        await message.answer('Хотите создать напоминание?', reply_markup=add_notif_kb)
    else:
        result = list({})
        endless = False
        text = ''
        text_2 = '              \n' \
                 'Бессрочные дела:\n' \
                 '                \n'
        j = 1
        for row in records:
            result.append({'id': row[0], 'record': row[2], 'time': row[4],
                           'date': row[1]})
        res = {}

        for i in result:
            if i['id'] not in res:
                res[i['id']] = []
            new_data = i.copy()
            new_data.pop('id')
            res[i['id']].append(new_data)

        for id in res:
            sorted_list = sorted(res[id], key=itemgetter("date", "time"))
            for value in sorted_list:
                text += f'{j}. {value["record"]} - {value["date"]} {value["time"]}\n'
                j += 1

        await message.answer('Вот ваши напоминания: ')
        await message.answer(text, reply_markup=edit_kb)
    cursor.close()


def make_text(records):
    text = ''
    i = 1

    for row in records:
        text += f'{i}. {row[2]} - {row[1]} {row[4]}\n'
        i += 1
    return text


# @dp.callback_query_handler(text='add_doings')
async def make_record(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await add_new_notif(callback_query.message)


# @dp.message_handler(lambda message: 'Добавить напоминание' in message.text)
async def add_new_notif(message: types.Message):
    await message.answer('Введите название напоминания: ')
    await Notifications.record.set()


# @dp.message_handler(state = Notifications.record)
async def get_date(message: types.Message):
    Notifications.record_text = message.text
    await message.answer(
        'Выберите дату, когда Вам нужно напомнить (если каждый день, '
        'просто напишите мне "ежедневно"): ',
        reply_markup=await SimpleCalendar().start_calendar())
    await Notifications.date.set()


# @dp.message_handler(Text(equals='сегодня', ignore_case=True))
async def today_notif(message: types.Message, state: FSMContext):
    Notifications.date_text = datetime.today().date().strftime('%d.%m.%Y')
    await message.answer(f'Вы выбрали: {Notifications.date_text}')
    await message.answer('Напишите время, когда нужно присылать вам напоминания')
    await Notifications.time.set()


# @dp.message_handler(Text(equals='ежедневно', ignore_case=True), state = Notifications.date)
async def everyday_notif(message: types.Message):
    Notifications.date_text = 'ежедневно'
    await message.answer('Напишите время, когда нужно присылать вам напоминания')
    await Notifications.time.set()


# @dp.callback_query_handler(text='dont_make_notif')
async def dont_make_record(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await MainStates.first_pg.set()


# @dp.callback_query_handler(simple_cal_callback.filter())
async def notif_calender(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    await bot.answer_callback_query(callback_query.id)
    if selected:
        if date.date() < datetime.today().date():
            await callback_query.message.answer(
                'Вы выбрали дату, которая уже прошла. Пожалуйста, выберите другую дату:',
                reply_markup=await SimpleCalendar().start_calendar()
            )
        if date.date() >= datetime.today().date():
            Notifications.date_text = date.strftime('%d.%m.%Y')
            await bot.send_message(callback_query.from_user.id, f'Вы выбрали: {date.strftime("%d.%m.%Y")}')
            await bot.send_message(callback_query.from_user.id,
                                   'Напишите время, когда нужно присылать вам напоминания (в формате ЧЧ:ММ)')
            await Notifications.time.set()


# @dp.message_handler(state = Notifications.time)
async def get_time(message: types.Message, state: FSMContext):
    date = datetime.strptime(Notifications.date_text, '%d.%m.%Y')

    time_user = time.strptime(message.text, '%H:%M')
    time_now = time.strptime(datetime.today().time().strftime('%H:%M'), '%H:%M')

    if date.date() == datetime.today().date():
        if time_user < time_now:
            await message.answer('Вы ввели время, которое уже прошло. Пожалуйста, выберите другое время:')
        else:
            Notifications.time_text = message.text
            await acception(message, state)
    else:
        Notifications.time_text = message.text
        await acception(message, state)


# @dp.message_handler(state = Notifications.date)
async def acception(message: types.Message, state: FSMContext):
    await message.answer(f'Итак, вы ввели:\n'
                         f'Напоминание: {Notifications.record_text}\n'
                         f'Дата: {Notifications.date_text} {Notifications.time_text}\n')
    await message.answer('Все верно?', reply_markup=acception_kb)
    await state.finish()


# @dp.message_handler(lambda message: 'Удалить напоминание' in message.text, state="*")
async def choose_notif(message: types.Message):
    try:
        connect = sqlite3.connect('..\\db\\main_db.db')
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM diary_db WHERE user=? and notification=?', (message.from_user.id, 1))
        records = cursor.fetchall()
        await message.answer(
            'Выберите, какую запись хотите удалить (отправьте одну или несколько цифр). ')

        i = 1

        for row in records:
            Notifications.notif_dict[i] = row[2]
            i += 1

        text = make_text(records)

        await message.answer(text, reply_markup=dell_all_kb)
        await Notifications.number_doing.set()
        connect.close()

    except Exception as e:

        await error(message, e)


# @dp.message_handler(lambda message: 'Удалить все' in message.text, state=Notifications.number_doing)
async def del_all(message: types.Message):
    try:
        connect = sqlite3.connect('..\\db\\main_db.db')
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM diary_db WHERE user=? and notification=?', (message.from_user.id, 1))
        records = cursor.fetchall()

        temp_list = list()

        for item in records:
            temp_list.append(item[2])

        cursor.execute('DELETE FROM diary_db WHERE user=? and notification=?', (message.from_user.id, 1))

        for item in temp_list:
            await message.answer(
                emoji.emojize(
                    f':check_mark_button: Напоминание {text(bold(item))} '
                    f'было успешно удалено!'),
                reply_markup=main_kb, parse_mode=ParseMode.MARKDOWN)

        await MainStates.first_pg.set()

        connect.commit()
        cursor.close()

    except Exception as e:

        await error(message, e)


async def del_notif(message: types.Message):  # когда пользователь хочет вручную удалить напоминание
    try:

        if 'Удалить все' in message.text:
            await del_all(message)

            return

        else:

            connect = sqlite3.connect('..\\db\\main_db.db')
            cursor = connect.cursor()

            if len(message.text) == 1:
                cursor.execute('DELETE FROM diary_db WHERE record=?', (Notifications.notif_dict[int(message.text)],))
            else:
                if ',' not in message.text:
                    number_list = message.text.split()
                else:
                    number_list = message.text.split(',')
                for number in number_list:
                    cursor.execute('DELETE FROM diary_db WHERE record=?', (Notifications.notif_dict[int(number)],))
                    await message.answer(
                        emoji.emojize(
                            f':check_mark_button: Дело {text(bold(Notifications.notif_dict[int(number)]))} '
                            f'было успешно удалено!'),
                        reply_markup=main_kb, parse_mode=ParseMode.MARKDOWN)

            await MainStates.first_pg.set()

            connect.commit()
            cursor.close()
    except Exception as e:

        await error(message, e)


# @dp.callback_query_handler(text='accept_notif')
async def accept_yes(callback_query: CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

        await callback_query.message.answer(
            emoji.emojize(
                f':check_mark_button: Отлично! Напоминание {text(bold(Notifications.record_text))} сработает '
                f'{Notifications.date_text} в {Notifications.time_text}!'),
            parse_mode=ParseMode.MARKDOWN, reply_markup=main_kb)
        await MainStates.first_pg.set()

        connect = sqlite3.connect('..\\db\\main_db.db')
        cursor = connect.cursor()
        cursor.execute('INSERT INTO diary_db (user, date, record, notification, time) VALUES (?, ?, ?, ?, ?)', (
            callback_query.from_user.id, Notifications.date_text, Notifications.record_text, 1,
            Notifications.time_text))

        if Notifications.date_text != 'ежедневно':

            day = str()
            month = str()
            year = str()
            hour = str()
            min = str()

            for i in range(0, 2):
                day += Notifications.date_text[i]

            for i in range(3, 5):
                month += Notifications.date_text[i]

            for i in range(6, 10):
                year += Notifications.date_text[i]

            for i in range(0, 2):
                hour += Notifications.time_text[i]

            for i in range(3, 5):
                min += Notifications.time_text[i]

            scheduler.add_job(send_notif, 'date',
                              run_date=datetime(int(year), int(month), int(day), int(hour), int(min), 0),
                              kwargs={'id': callback_query.from_user.id, 'record': Notifications.record_text,
                                      'month': month, 'day': day, 'hour': hour, 'min': min})

            scheduler.add_job(delete_notification, 'cron', year=year, month=month, day=day, hour=hour,
                              minute=str(int(min) + 1))

        if Notifications.date_text == 'ежедневно':

            difference, time1, time2 = difference_time(Notifications.time_text)

            if difference:  # если время уже прошло
                day = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

                start_date = datetime.strptime(day + ' ' + Notifications.time_text, '%Y-%m-%d %H:%M')

                scheduler.add_job(send_notif, 'interval', hours=24, start_date=start_date,
                                  kwargs={'id': callback_query.from_user.id, 'record': Notifications.record_text,
                                          'month': 'everyday', 'time': Notifications.time_text})

            else:
                day = (datetime.today()).strftime('%Y-%m-%d')

                start_date = datetime.strptime(day + ' ' + Notifications.time_text, '%Y-%m-%d %H:%M')

                scheduler.add_job(send_notif, 'interval', hours=24, start_date=start_date,
                                  kwargs={'id': callback_query.from_user.id, 'record': Notifications.record_text,
                                          'month': 'everyday', 'time': Notifications.time_text})

        connect.commit()
        cursor.close()

    except Exception as e:

        await error(callback_query.message, e)


def notif_handlers_registration(dp):
    dp.register_message_handler(list_of_notif, lambda message: 'Список напоминаний' in message.text,
                                state=MainStates.first_pg)
    dp.register_message_handler(add_new_notif, lambda message: 'Добавить напоминание' in message.text,
                                state="*")
    dp.register_message_handler(get_time, state=Notifications.time)

    dp.register_message_handler(del_notif, state=Notifications.number_doing)
    dp.register_message_handler(choose_notif, lambda message: 'Удалить напоминание' in message.text,
                                state="*")
    dp.register_message_handler(del_all, lambda message: 'Удалить все' in message.text,
                                state=Notifications.number_doing)

    dp.register_message_handler(get_date, state=Notifications.record)
    dp.register_message_handler(everyday_notif, Text(equals='ежедневно', ignore_case=True), state=Notifications.date)
    dp.register_message_handler(today_notif, Text(equals='сегодня', ignore_case=True), state=Notifications.date)

    dp.register_callback_query_handler(accept_yes, text='accept_notif', state="*")

    dp.register_message_handler(acception, state=Notifications.date)

    dp.register_callback_query_handler(make_record, text='make_notif', state="*")
    dp.register_callback_query_handler(dont_make_record, text='dont_make_notif', state="*")

    dp.register_callback_query_handler(notif_calender, simple_cal_callback.filter(), state=Notifications.date)
