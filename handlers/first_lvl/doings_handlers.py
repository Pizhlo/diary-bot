from operator import itemgetter
import emoji
import time
from aiogram.types import InlineKeyboardButton
from aiogram import types
from aiogram_calendar import simple_cal_callback, SimpleCalendar
import sqlite3
from main_files.common import MainStates, error, Doings, scheduler
from main_files.create_bot import bot
from aiogram.dispatcher import FSMContext
from keyboards.first_lvl.doings_kb import acception_kb, add_doings_kb, edit_kb, change_kb, add_time_kb
from keyboards.first_lvl.notifications_kb import dell_all_kb
from keyboards.first_lvl.main_kb import main_kb
from aiogram.types import CallbackQuery
from datetime import datetime
from aiogram.utils.markdown import text, bold
from aiogram.dispatcher.filters import Text
from db.clean_database import delete_doings_with_time
from aiogram.types import ParseMode


# @dp.message_handler(lambda message: 'Список дел' in message.text)
async def list_of_doings(message: types.Message):
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM diary_db WHERE user=? and notification=?', (message.from_user.id, 0))
    records = cursor.fetchall()

    if not records:
        await message.answer('У вас нет запланированных дел.')
        await message.answer('Хотите добавить дело?', reply_markup=add_doings_kb)
    else:
        result = list({})
        endless = False
        text = ''
        text_2 = '              \n' \
                 'Бессрочные дела:\n' \
                 '                \n'
        j = 1
        k = 1
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
                if value['date'] == 'Бессрочно':
                    endless = True
                    text_2 += f'{k}. {value["record"]}\n'
                    k += 1
                else:
                    if value['time'] == 0:
                        text += f'{j}. {value["record"]} - {value["date"]}\n'
                        j += 1
                    else:
                        text += f'{j}. {value["record"]} - {value["date"]} {value["time"]}\n'
                        j += 1

        await message.answer('Вот ваши дела: ')
        if endless:
            await message.answer(text + text_2, reply_markup=edit_kb)
        else:
            await message.answer(text, reply_markup=edit_kb)
    cursor.close()


# @dp.callback_query_handler(text='add_doings')
async def make_record(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await add_new_doing(callback_query.message)


# @dp.message_handler(lambda message: 'Добавить дело' in message.text)
async def add_new_doing(message: types.Message):
    await message.answer('Введите название вашего дела: ')
    await Doings.record.set()


# @dp.callback_query_handler(text='dont_add_doings')
async def dont_make_record(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await MainStates.first_pg.set()


# @dp.message_handler(state = Doings.record)
async def get_date(message: types.Message):
    Doings.record_text = message.text
    await message.answer('Выберите дату, когда Вам нужно сделать дело (если это бессрочно, '
                         'просто напишите мне "бессрочно", если сегодня - напишите "сегодня"): ',
                         reply_markup=await SimpleCalendar().start_calendar())
    await Doings.date.set()


# @dp.message_handler(state = Doings.date)
async def date_without_calendar(message: types.Message):
    Doings.date_text = message.text
    await message.answer(f'Вы выбрали: {Doings.date_text}')
    await message.answer('Хотите добавить время?', reply_markup=add_time_kb)


# @dp.message_handler(Text(equals='бессрочно', ignore_case=True))
async def endless_doings(message: types.Message, state: FSMContext):
    Doings.date_text = 'Бессрочно'
    await message.answer(f'Вы выбрали: {Doings.date_text}')
    await acception(message, state)


# @dp.message_handler(Text(equals='сегодня', ignore_case=True))
async def today_doings(message: types.Message):
    Doings.date_text = datetime.today().date().strftime('%d.%m.%Y')
    await message.answer(f'Вы выбрали: {Doings.date_text}')
    await message.answer('Хотите добавить время?', reply_markup=add_time_kb)


# @dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    await bot.answer_callback_query(callback_query.id)
    if selected:
        if date.date() < datetime.today().date():
            await callback_query.message.answer(
                'Вы выбрали дату, которая уже прошла. Пожалуйста, выберите другую дату:',
                reply_markup=await SimpleCalendar().start_calendar()
            )
        if date.date() >= datetime.today().date():
            Doings.date_text = date.strftime("%d.%m.%Y")
            await bot.send_message(callback_query.from_user.id, f'Вы выбрали: {date.strftime("%d.%m.%Y")}')
            await bot.send_message(callback_query.from_user.id, 'Хотите добавить время?', reply_markup=add_time_kb)


# @dp.callback_query_handler(text='add_time')
async def add_time(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, 'Введите время: ')
    await Doings.time.set()


# @dp.message_handler(state = Doings.time)
async def get_time(message: types.Message, state: FSMContext):
    date = datetime.strptime(Doings.date_text, '%d.%m.%Y')

    time_user = time.strptime(message.text, '%H:%M')
    time_now = time.strptime(datetime.today().time().strftime('%H:%M'), '%H:%M')

    if date.date() == datetime.today().date():
        if time_user < time_now:
            await message.answer('Вы ввели время, которое уже прошло. Пожалуйста, выберите другое время:')
        else:
            Doings.time_text = message.text
            await acception(message, state)
    else:
        Doings.time_text = message.text
        await acception(message, state)


# @dp.callback_query_handler(text='dont_add_time')
async def dont_add_time(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await Doings.acception.set()
    await acception(callback_query.message, state)


# @dp.message_handler(state = Doings.acception)
async def acception(message: types.Message, state: FSMContext):
    if not Doings.time_text:
        await message.answer(f'Итак, вы ввели:\n'
                             f'Название дела: {Doings.record_text}\n'
                             f'Дата выполнения: {Doings.date_text}\n')
    else:
        await message.answer(f'Итак, вы ввели:\n'
                             f'Название дела: {Doings.record_text}\n'
                             f'Дата выполнения: {Doings.date_text} {Doings.time_text}\n')
    await message.answer('Все верно?', reply_markup=acception_kb)
    await state.finish()


def make_text(records):
    text = ''
    text_2 = '              \n' \
             'Бессрочные дела:\n' \
             '                \n'
    i = 1
    k = 1
    endless = False

    for row in records:
        if row[1] != 'Бессрочно':
            if row[4] == 0:  # если время не указано
                text += f'{i}. {row[2]} - {row[1]}\n'
            else:
                text += f'{i}. {row[2]} - {row[1]} {row[4]}\n'
            i += 1
        if row[1] == 'Бессрочно':
            endless = True
            text_2 += f'{k}. {row[2]}\n'
            k += 1
    return endless, text, text_2


# @dp.message_handler(lambda message: 'Удалить' in message.text, state="*")
async def choose_doings(message: types.Message):
    try:

        connect = sqlite3.connect('..\\db\\main_db.db')
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM diary_db WHERE user=? and notification=?', (message.from_user.id, 0))
        records = cursor.fetchall()
        await message.answer(
            'Выберите, какую запись хотите удалить (отправьте одну или несколько цифр). '
            'Если вы хотите удалить запись из списка '
            'бессрочных дел, '
            'сообщение должно содержать слово "бессрочно"')

        i = 1
        k = 1

        for row in records:
            if row[1] != 'Бессрочно':
                Doings.doings_dict[i] = row[2]
                i += 1
            else:
                Doings.endless_doings_dict[k] = row[2]
                k += 1

        endless, text, text_2 = make_text(records)

        if endless:
            await message.answer(text + text_2, reply_markup=dell_all_kb)
        else:
            await message.answer(text, reply_markup=dell_all_kb)
        await Doings.number_doing.set()
        connect.close()

    except Exception as e:

        await error(message, e)


# @dp.message_handler(lambda message: 'Удалить все' in message.text, state=Doings.number_doing)
async def del_all_doings(message: types.Message):
    try:
        connect = sqlite3.connect('..\\db\\main_db.db')
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM diary_db WHERE user=? and notification=?', (message.from_user.id, 0))
        records = cursor.fetchall()

        temp_list = list()

        for item in records:
            temp_list.append(item[2])

        cursor.execute('DELETE FROM diary_db WHERE user=? and notification=?', (message.from_user.id, 0))

        for item in temp_list:
            await message.answer(
                emoji.emojize(
                    f':check_mark_button: Дело {text(bold(item))} '
                    f'было успешно удалено!'),
                reply_markup=main_kb, parse_mode=ParseMode.MARKDOWN)

        await MainStates.first_pg.set()

        connect.commit()
        cursor.close()

    except Exception as e:

        await error(message, e)


# @dp.message_handler(state=number_doing)
async def del_doing(message: types.Message):  # когда пользователь хочет вручную удалить дело
    try:

        if 'Удалить все' in message.text:
            await del_all_doings(message)

            return
        connect = sqlite3.connect('..\\db\\main_db.db')
        cursor = connect.cursor()

        if 'бессрочно' not in message.text:
            if ',' not in message.text:
                number_list = message.text.split()
            else:
                number_list = message.text.split(',')
            for number in number_list:
                cursor.execute('DELETE FROM diary_db WHERE record=?', (Doings.doings_dict[int(number)],))
                await message.answer(
                    emoji.emojize(
                        f':check_mark_button: Дело {text(bold(Doings.doings_dict[int(number)]))} было успешно удалено!'),
                    reply_markup=main_kb, parse_mode=ParseMode.MARKDOWN)
        else:
            new_msg = message.text.replace('бессрочно', '')
            if ',' not in message.text:
                number_list = new_msg.split()
            else:
                number_list = new_msg.split(',')
            for number in number_list:
                cursor.execute('DELETE FROM diary_db WHERE record=?', (Doings.endless_doings_dict[int(number)],))

                await message.answer(
                    emoji.emojize(
                        f':check_mark_button: Дело {text(bold(Doings.endless_doings_dict[int(number)]))} было успешно удалено!'),
                    reply_markup=main_kb, parse_mode=ParseMode.MARKDOWN)

        await MainStates.first_pg.set()

        connect.commit()
        cursor.close()
    except Exception as e:

        await error(message, e)


# @dp.message_handler(lambda message: 'Назад' in message.text, state="*")
async def come_back(message: types.Message):
    await message.answer("Привет!"
                         "\nВыбери, что хочешь сделать",
                         reply_markup=main_kb)
    await MainStates.first_pg.set()


# @dp.callback_query_handler(text='accept')
async def accept_yes(callback_query: CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await callback_query.message.answer(
            emoji.emojize(f':check_mark_button: Отлично! Дело {text(bold(Doings.record_text))} записано!'),
            parse_mode=ParseMode.MARKDOWN, reply_markup=main_kb)
        await MainStates.first_pg.set()
        connect = sqlite3.connect('..\\db\\main_db.db')
        cursor = connect.cursor()
        day = str()
        month = str()
        year = str()
        hour = str()
        min = str()

        if Doings.date_text != 'Бессрочно':

            for i in range(0, 2):
                day += Doings.date_text[i]

            for i in range(3, 5):
                month += Doings.date_text[i]

            for i in range(6, 10):
                year += Doings.date_text[i]

            if Doings.time_text:

                for i in range(0, 2):
                    hour += Doings.time_text[i]

                for i in range(3, 5):
                    min += Doings.time_text[i]

        if Doings.date_text == 'Бессрочно':
            cursor.execute('INSERT INTO diary_db (user, date, record, notification, time) VALUES (?, ?, ?, ?, ?)', (
                callback_query.from_user.id, 'Бессрочно', Doings.record_text, 0, 0))

        elif Doings.date_text != 'Бессрочно' and not Doings.time_text:
            cursor.execute('INSERT INTO diary_db (user, date, record, notification, time) VALUES (?, ?, ?, ?, ?)', (
                callback_query.from_user.id, Doings.date_text, Doings.record_text, 0, 0))

            # scheduler.add_job(send_morning_msg, 'cron', year=year, month=month, day=day, hour=hour,
            #  minute=str(int(min) + 1), kwargs={'id': callback_query.from_user.id,
            # 'record': Doings.record_text,
            #  'date': Doings.date_text})

        elif Doings.date_text != 'Бессрочно' and Doings.time_text:
            cursor.execute('INSERT INTO diary_db (user, date, record, notification, time) VALUES (?, ?, ?, ?, ?)', (
                callback_query.from_user.id, Doings.date_text, Doings.record_text, 0, Doings.time_text))

            scheduler.add_job(delete_doings_with_time, 'cron', year=year, month=month, day=day, hour=hour,
                              minute=str(int(min) + 1))

        Doings.time_text = ''
        connect.commit()
        cursor.close()

    except Exception as e:

        await error(callback_query.message, e)


# @dp.callback_query_handler(text='dont_accept')
async def accept_no(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    if Doings.time_text:
        change_time = InlineKeyboardButton('Время', callback_data='edit_time')
        change_kb.row(change_time)
    await Doings.editing.set()
    await callback_query.message.answer('Выберите, что нужно исправить:', reply_markup=change_kb)


# @dp.callback_query_handler(text='date')
async def change_date(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await Doings.edit_date.set()
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await callback_query.message.answer('Выберите дату, когда Вам нужно сделать дело: ',
                                        reply_markup=await SimpleCalendar().start_calendar())


# @dp.callback_query_handler(text='time')
async def edit_time(callback_query: CallbackQuery, message: types.Message, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    print('edit_time')
    await Doings.edit_time.set()
    date = datetime.strptime(Doings.date_text, '%d.%m.%Y')

    time_user = time.strptime(message.text, '%H:%M')
    time_now = time.strptime(datetime.today().time().strftime('%H:%M'), '%H:%M')

    if date.date() == datetime.today().date():
        if time_user < time_now:
            await message.answer('Вы ввели время, которое уже прошло. Пожалуйста, выберите другое время:')
        else:
            Doings.time_text = message.text
            await acception(message, state)
    else:
        Doings.time_text = message.text
        await acception(message, state)


# @dp.callback_query_handler(text='doing')
async def change_record(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer('Введите новое значение: ')
    await Doings.edit_record.set()


# dp.register_message_handler(state=Doings.edit_record)
async def got_new_record(message: types.Message, state: FSMContext):
    Doings.record_text = message.text
    await message.answer(f'Итак, вы ввели:\n'
                         f'Название дела: {Doings.record_text}\n'
                         f'Дата выполнения: {Doings.date_text}\n')
    await message.answer('Все верно?', reply_markup=acception_kb)
    await state.finish()


def doings_handlers_registration(dp):
    dp.register_message_handler(list_of_doings, lambda message: 'Список дел' in message.text,
                                state=MainStates.first_pg)
    dp.register_message_handler(come_back, lambda message: 'Назад' in message.text, state="*")
    dp.register_message_handler(choose_doings, lambda message: 'Удалить дело' in message.text, state="*")
    dp.register_message_handler(add_new_doing, lambda message: 'Добавить дело' in message.text, state='*')

    dp.register_message_handler(del_doing, state=Doings.number_doing)
    dp.register_message_handler(del_all_doings, lambda message: 'Удалить все' in message.text,
                                state=Doings.number_doing)

    dp.register_message_handler(endless_doings, Text(equals='бессрочно', ignore_case=True), state=Doings.date)
    dp.register_message_handler(today_doings, Text(equals='сегодня', ignore_case=True), state=Doings.date)

    dp.register_message_handler(get_time, state=Doings.time)
    dp.register_callback_query_handler(add_time, text='add_time', state="*")
    dp.register_callback_query_handler(dont_add_time, text='dont_add_time', state="*")

    dp.callback_query_handler(edit_time, text='edit_time', state=Doings.editing)
    dp.register_message_handler(got_new_record, state=Doings.edit_record)

    dp.register_message_handler(get_date, state=Doings.record)
    dp.register_message_handler(acception, state=Doings.acception)

    # test

    # dp.register_message_handler(date_without_calendar, state=Doings.date)

    #

    dp.register_callback_query_handler(make_record, text='add_doings', state="*")
    dp.register_callback_query_handler(dont_make_record, text='dont_add_doings', state="*")

    dp.register_callback_query_handler(accept_yes, text='accept', state="*")
    dp.register_callback_query_handler(accept_no, text='dont_accept', state="*")

    dp.register_callback_query_handler(change_date, text='date', state="*")
    dp.register_callback_query_handler(change_record, text='doing', state="*")

    dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter(), state=Doings.date)
    dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter(), state=Doings.edit_date)
