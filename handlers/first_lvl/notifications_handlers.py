import emoji
from aiogram import types
from aiogram_calendar import simple_cal_callback, SimpleCalendar
import sqlite3
from main_files.common import MainStates, error, scheduler
from aiogram.dispatcher.filters.state import State, StatesGroup
from main_files.create_bot import bot
from aiogram.dispatcher import FSMContext
from keyboards.first_lvl.notifications_kb import add_notif_kb, edit_kb, acception_kb
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Text
from keyboards.first_lvl.main_kb import main_kb


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

    for item in records:
        print("item = ", item)

    if not records:
        await message.answer('У вас нет напоминаний.')
        await message.answer('Хотите создать напоминание?', reply_markup=add_notif_kb)
    else:
        await message.answer('Вот ваши напоминания: ')
        for row in records:
            if row[4] == 0:
                await message.answer(f'Название: {row[2]}\n'
                                     f'Дата напоминания: {row[1]}', reply_markup=edit_kb)
            else:
                await message.answer(f'Название: {row[2]}\n'
                                     f'Дата напоминания: {row[1]} {row[4]}', reply_markup=edit_kb)
    cursor.close()


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
        'Выберите дату, когда Вам нужно напомнить (если ежедневно - просто напишите мне "ежедневно"): ',
        reply_markup=await SimpleCalendar().start_calendar())
    await Notifications.date.set()


# @dp.message_handler(Text(equals='ежедневно', ignore_case=True), state = Notifications.date)
async def everyday_notif(message: types.Message):
    Notifications.date_text = 'ежедневно'
    await message.answer('Напишите время, когда нужно присылать вам напоминания')
    await Notifications.time.set()


# @dp.callback_query_handler(text='dont_make_notif')
async def dont_make_record(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await callback_query.message.answer(emoji.emojize(':check_mark_button: ОК'))


# @dp.callback_query_handler(simple_cal_callback.filter())
async def notif_calender(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    await bot.answer_callback_query(callback_query.id)
    if selected:
        if date < datetime.today():
            await callback_query.message.answer(
                'Вы выбрали дату, которая уже прошла. Пожалуйста, выберите другую дату:',
                reply_markup=await SimpleCalendar().start_calendar()
            )
        if date >= datetime.today():
            Notifications.date_text = date.strftime('%d.%m.%Y')
            await bot.send_message(callback_query.from_user.id, f'Вы выбрали: {date.strftime("%d.%m.%Y")}')
            await bot.send_message(callback_query.from_user.id, 'Напишите время, когда нужно присылать вам напоминания')
            await Notifications.time.set()


# @dp.message_handler(state = Notifications.time)
async def get_time(message: types.Message, state: FSMContext):
    Notifications.time_text = message.text
    await acception(message, state)


# @dp.message_handler(state = Notifications.date)
async def acception(message: types.Message, state: FSMContext):
    await message.answer(f'Итак, вы ввели:\n'
                         f'Напоминание: {Notifications.record_text}\n'
                         f'Дата: {Notifications.date_text} {Notifications.time_text}\n')
    await message.answer('Все верно?', reply_markup=acception_kb)
    await state.finish()


# @dp.callback_query_handler(text='accept_notif')
async def accept_yes(callback_query: CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

        await callback_query.message.answer(
            emoji.emojize(
                f':check_mark_button: Отлично! Напоминание {text(bold(Notifications.record_text))} записано!'),
            parse_mode=ParseMode.MARKDOWN, reply_markup=main_kb)
        await MainStates.first_pg.set()

        connect = sqlite3.connect('..\\db\\main_db.db')
        cursor = connect.cursor()
        cursor.execute('INSERT INTO diary_db (user, date, record, notification, time) VALUES (?, ?, ?, ?, ?)', (
            callback_query.from_user.id, Notifications.date_text, Notifications.record_text, 1,
            Notifications.time_text))

        if Notifications.date_text != 'ежедневно':
            scheduler.add_job(send_notif, 'date', run_date=(Notifications.date_text + Notifications.time_text))

        if Notifications.date_text == 'ежедневно':

            time_obj = datetime.strptime(Notifications.time_text, '%H:%M')

            time = datetime.today().time().strftime('%H:%M')  # string
            time_now = datetime.strptime(time, '%H:%M')  # date

            time_1 = timedelta(hours=time_obj.hour, minutes=time_obj.minute)
            time_2 = timedelta(hours=datetime.now().time().hour, minutes=datetime.now().time().minute)

            difference_hours: timedelta

            if time_obj > time_now:  # если время уже прошло
                # 2019 - 12 - 25 11: 00:00

                difference_hours = time_1 - time_2

            else:

                difference_hours = time_2 - time_1

            scheduler.add_job(send_notif, 'interval', hours=24, start_date=(
                    datetime.today().date() + timedelta(days=1, hours=difference_hours.seconds)).strftime(
                '%Y-%m-%d %H:%M:%S'))

            print(
                f"Напоминание сработает {(datetime.today().date() + timedelta(days=1, hours=difference_hours.seconds)).strftime('%Y - %m - %d %H:%M:%S')}")

        connect.commit()
        cursor.close()

    except Exception as e:

        await error(callback_query.message, e)


async def send_notif():
    pass


def notif_handlers_registration(dp):
    dp.register_message_handler(list_of_notif, lambda message: 'Список напоминаний' in message.text,
                                state=MainStates.first_pg)
    dp.register_message_handler(add_new_notif, lambda message: 'Добавить напоминание' in message.text,
                                state="*")
    dp.register_message_handler(get_time, state=Notifications.time)

    dp.register_message_handler(get_date, state=Notifications.record)
    dp.register_message_handler(everyday_notif, Text(equals='ежедневно', ignore_case=True), state=Notifications.date)

    dp.register_callback_query_handler(accept_yes, text='accept_notif', state="*")

    dp.register_message_handler(acception, state=Notifications.date)

    dp.register_callback_query_handler(make_record, text='make_notif', state="*")
    dp.register_callback_query_handler(dont_make_record, text='dont_make_notif', state="*")

    dp.register_callback_query_handler(notif_calender, simple_cal_callback.filter(), state=Notifications.date)
