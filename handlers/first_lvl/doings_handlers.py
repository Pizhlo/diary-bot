from aiogram import types
import sqlite3
from main_files.common import MainStates, error
from aiogram.dispatcher.filters.state import State, StatesGroup
from main_files.create_bot import bot
from aiogram.dispatcher import FSMContext
from keyboards.first_lvl.doings_kb import acception_kb, add_doings_kb, edit_kb, change_kb
from keyboards.first_lvl.main_kb import main_kb
from aiogram.types import CallbackQuery
import datetime, schedule


class Doings(StatesGroup):
    record = State()
    date = State()
    number_doing = State()

    edit_date = State()
    edit_record = State()

    send_mrng_msg = State()

    mornings_doings_text = ''

    record_text = ''
    date_text = ''

    doings_dict = dict()


# @dp.message_handler(lambda message: 'Список дел' in message.text)
async def list_of_doings(message: types.Message):
    connect = sqlite3.connect('C:\\Users\\pizhlo21\\Desktop\\Folder\\python\\diary_bot\\db\\main_db.db')
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM diary_db WHERE user=?', (message.from_user.id,))
    records = cursor.fetchall()

    for item in records:
        print("item = ", item)

    if not records:
        await message.answer('У вас нет запланированных дел. Хотите добавить дело?', reply_markup=add_doings_kb)
    else:
        await message.answer('Вот ваши дела: ')
        for row in records:
            await message.answer(f'Название дела: {row[2]}\n'
                                 f'Дата выполнения: {row[1]}', reply_markup=edit_kb)
    cursor.close()


# @dp.callback_query_handler(text='add_doings')
async def make_record(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer('Введите название вашего дела: ')
    await Doings.record.set()


# @dp.callback_query_handler(text='dont_add_doings')
async def dont_make_record(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer('ОК')


# @dp.message_handler(state = Doings.record)
async def get_date(message: types.Message):
    Doings.record_text = message.text
    await message.answer('Введите дату, когда Вам нужно сделать дело (в формате ДД.ММ.ГГГГ): ')
    await Doings.date.set()


# @dp.message_handler(state = Doings.date)
async def acception(message: types.Message, state: FSMContext):
    Doings.date_text = message.text
    await message.answer(f'Итак, вы ввели:\n'
                         f'Название дела: {Doings.record_text}\n'
                         f'Дата выполнения: {Doings.date_text}\n')
    await message.answer('Все верно?', reply_markup=acception_kb)
    await state.finish()


# @dp.message_handler(lambda message: 'Удалить' in message.text, state="*")
async def choose_doings(message: types.Message):
    connect = sqlite3.connect('C:\\Users\\pizhlo21\\Desktop\\Folder\\python\\diary_bot\\db\\main_db.db')
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
        connect = sqlite3.connect('C:\\Users\\pizhlo21\\Desktop\\Folder\\python\\diary_bot\\db\\main_db.db')
        cursor = connect.cursor()
        cursor.execute('DELETE FROM diary_db WHERE record=?', (Doings.doings_dict[number],))
        connect.commit()
        cursor.close()
        await message.answer(f'Дело {Doings.doings_dict[number]} было успешно удалено!', reply_markup=main_kb)
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
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer('Отлично! Дело записано!')
    await MainStates.first_pg.set()
    connect = sqlite3.connect('C:\\Users\\pizhlo21\\Desktop\\Folder\\python\\diary_bot\\db\\main_db.db')
    cursor = connect.cursor()
    cursor.execute('INSERT INTO diary_db (user, date, record, notification) VALUES (?, ?, ?, ?)', (
        callback_query.from_user.id, Doings.date_text, Doings.record_text, 0))
    print('==========================')
    check_2 = cursor.execute('SELECT * FROM diary_db WHERE user=?', (callback_query.from_user.id,))
    for item in check_2:
        print(item)
    connect.commit()
    cursor.close()


# @dp.callback_query_handler(text='dont_accept')
async def accept_no(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer('Выберите, что нужно исправить:', reply_markup=change_kb)


# @dp.callback_query_handler(text='time')
async def change_time(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await Doings.edit_date.set()
    await callback_query.message.answer('Введите новое значение (в формате ДД.ММ.ГГГГ): ')


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


def send_morning_msg():
    date = datetime.datetime.today().date().strftime('%d.%m.%Y')
    print("date = ", date)
    connect = sqlite3.connect('C:\\Users\\pizhlo21\\Desktop\\Folder\\python\\diary_bot\\db\\main_db.db')
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM diary_db WHERE date=?', (date,))
    records = cursor.fetchall()

    if records:
        for row in records:
            Doings.mornings_doings_text += f'{row[2]}. \n'


def doings_handlers_registration(dp):
    dp.register_message_handler(list_of_doings, lambda message: 'Список дел' in message.text, state=MainStates.first_pg)
    dp.register_message_handler(come_back, lambda message: 'Назад' in message.text, state="*")
    dp.register_message_handler(choose_doings, lambda message: 'Удалить' in message.text, state="*")
    dp.register_message_handler(del_doing, state=Doings.number_doing)

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
