import emoji
from aiogram import types
from aiogram_calendar import simple_cal_callback, SimpleCalendar
import sqlite3
from main_files.common import MainStates, error
from aiogram.dispatcher.filters.state import State, StatesGroup
from main_files.create_bot import bot
from aiogram.dispatcher import FSMContext
from keyboards.first_lvl.doings_kb import acception_kb, add_doings_kb, edit_kb, change_kb, add_time_kb
from keyboards.first_lvl.main_kb import main_kb
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta
import asyncio
import aioschedule


class Doings(StatesGroup):
    record = State()
    date = State()
    time = State()
    number_doing = State()

    edit_date = State()
    edit_record = State()

    send_mrng_msg = State()

    mornings_doings_text = ''

    record_text = ''
    date_text = ''
    time_text = ''

    doings_dict = dict()


# @dp.message_handler(lambda message: 'Список дел' in message.text)
async def list_of_doings(message: types.Message):
    connect = sqlite3.connect('C:\\Users\\1\\Desktop\\diary-bot\\db\\main_db.db')
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM diary_db WHERE user=?', (message.from_user.id,))
    records = cursor.fetchall()

    for item in records:
        print("item = ", item)

    if not records:
        await message.answer('У вас нет запланированных дел.')
        await message.answer('Хотите добавить дело?', reply_markup=add_doings_kb)
    else:
        await message.answer('Вот ваши дела: ')
        for row in records:
            if row[4] == 0:
                await message.answer(f'Название дела: {row[2]}\n'
                                     f'Дата выполнения: {row[1]}', reply_markup=edit_kb)
            else:
                await message.answer(f'Название дела: {row[2]}\n'
                                     f'Дата выполнения: {row[1]} {row[4]}', reply_markup=edit_kb)
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
    await callback_query.message.answer(emoji.emojize(':check_mark_button: ОК'))


# @dp.message_handler(state = Doings.record)
async def get_date(message: types.Message):
    Doings.record_text = message.text
    await message.answer('Выберите дату, когда Вам нужно сделать дело: ',
                         reply_markup=await SimpleCalendar().start_calendar())
    await Doings.date.set()


# @dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    await bot.answer_callback_query(callback_query.id)
    if selected:
        if date < datetime.today():
            await callback_query.message.answer(
                'Вы выбрали дату, которая уже прошла. Пожалуйста, выберите другую дату:',
                reply_markup=await SimpleCalendar().start_calendar()
            )
        if date >= datetime.today():
            Doings.date_text = date.strftime('%d.%m.%Y')
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
    Doings.time_text = message.text
    await acception(message, state)


# @dp.callback_query_handler(text='dont_add_time')
async def dont_add_time(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await acception(callback_query.message, state)


# @dp.message_handler(state = Doings.date)
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


# @dp.message_handler(lambda message: 'Удалить' in message.text, state="*")
async def choose_doings(message: types.Message):
    connect = sqlite3.connect('C:\\Users\\1\\Desktop\\diary-bot\\db\\main_db.db')
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM diary_db WHERE user=?', (message.from_user.id,))
    records = cursor.fetchall()
    await message.answer('Выберите, какое дело хотите удалить (отправьте цифру)')
    n = 1
    text = ''
    for row in records:
        text += f'{n}. {row[2]}\n'
        Doings.doings_dict[n] = row[2]
        n += 1
    await message.answer(text)
    await Doings.number_doing.set()
    connect.close()


# @dp.message_handler(state=number_doing)
async def del_doing(message: types.Message):
    try:
        number = int(message.text)
        connect = sqlite3.connect('C:\\Users\\1\\Desktop\\diary-bot\\db\\main_db.db')
        cursor = connect.cursor()
        cursor.execute('DELETE FROM diary_db WHERE record=?', (Doings.doings_dict[number],))
        connect.commit()
        cursor.close()
        await message.answer(
            emoji.emojize(f':check_mark_button: Дело {Doings.doings_dict[number]} было успешно удалено!'),
            reply_markup=main_kb)
        await MainStates.first_pg.set()
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
        await callback_query.message.answer(emoji.emojize(':check_mark_button: Отлично! Дело записано!'))
        await MainStates.first_pg.set()
        connect = sqlite3.connect('C:\\Users\\1\\Desktop\\diary-bot\\db\\main_db.db')
        cursor = connect.cursor()
        if Doings.time_text:
            cursor.execute('INSERT INTO diary_db (user, date, record, notification, time) VALUES (?, ?, ?, ?, ?)', (
                callback_query.from_user.id, Doings.date_text, Doings.record_text, 0, Doings.time_text))
        else:
            cursor.execute('INSERT INTO diary_db (user, date, record, notification, time) VALUES (?, ?, ?, ?, ?)', (
                callback_query.from_user.id, Doings.date_text, Doings.record_text, 0, 0))
        print('==========================')
        check_2 = cursor.execute('SELECT * FROM diary_db WHERE user=?', (callback_query.from_user.id,))
        for item in check_2:
            print(item)
        connect.commit()
        cursor.close()

    except Exception as e:

        await error(callback_query.message, e)


# @dp.callback_query_handler(text='dont_accept')
async def accept_no(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await callback_query.message.answer('Выберите, что нужно исправить:', reply_markup=change_kb)


# @dp.callback_query_handler(text='time')
async def change_time(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await Doings.edit_date.set()
    await callback_query.message.answer('Выберите дату, когда Вам нужно сделать дело: ',
                                        reply_markup=await SimpleCalendar().start_calendar())


# dp.register_message_handler(state=Doings.edit_date)
async def edit_time(message: types.Message, state: FSMContext):
    await Doings.date.set()
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


async def send_morning_msg():
    date = datetime.today().date().strftime('%d.%m.%Y')
    print("date = ", date)
    connect = sqlite3.connect('C:\\Users\\1\\Desktop\\diary-bot\\db\\main_db.db')
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


async def scheduler():
    aioschedule.every().day.at("08:30").do(send_morning_msg)
    aioschedule.every().day.at('00:01').do(clean_db)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


def clean_db():
    date = datetime.today().date() - timedelta(days=1)

    connect = sqlite3.connect('C:\\Users\\1\\Desktop\\diary-bot\\db\\main_db.db')
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM diary_db WHERE date=?', (date,))
    records = cursor.fetchall()
    if records:
        cursor.execute('DELETE * FROM diary_db WHERE date=?', (date,))
    connect.commit()
    cursor.close()


def doings_handlers_registration(dp):
    dp.register_message_handler(list_of_doings, lambda message: 'Список дел' in message.text, state=MainStates.first_pg)
    dp.register_message_handler(come_back, lambda message: 'Назад' in message.text, state="*")
    dp.register_message_handler(choose_doings, lambda message: 'Удалить' in message.text, state="*")
    dp.register_message_handler(add_new_doing, lambda message: 'Добавить дело' in message.text, state='*')

    dp.register_message_handler(del_doing, state=Doings.number_doing)

    dp.register_message_handler(get_time, state=Doings.time)
    dp.register_callback_query_handler(add_time, text='add_time', state="*")
    dp.register_callback_query_handler(dont_add_time, text='dont_add_time', state="*")

    dp.register_message_handler(edit_time, state=Doings.edit_date)
    dp.register_message_handler(got_new_record, state=Doings.edit_record)

    dp.register_message_handler(get_date, state=Doings.record)
    dp.register_message_handler(acception, state=Doings.date)

    dp.register_callback_query_handler(make_record, text='add_doings', state="*")
    dp.register_callback_query_handler(dont_make_record, text='dont_add_doings', state="*")

    dp.register_callback_query_handler(accept_yes, text='accept', state="*")
    dp.register_callback_query_handler(accept_no, text='dont_accept', state="*")

    dp.register_callback_query_handler(change_time, text='time', state="*")
    dp.register_callback_query_handler(change_record, text='doing', state="*")

    dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter(), state="*")
