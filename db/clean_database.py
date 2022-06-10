import sqlite3
from datetime import datetime, timedelta


def delete_doings_with_time():  # очистка БД; удаляет записи, у которых прошел срок выполнения
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()

    date = datetime.today().date().strftime('%d.%m.%Y')

    time = (datetime.now() - timedelta(minutes=1)).strftime("%H:%M")

    cursor.execute('DELETE FROM diary_db WHERE date=? and time=? and notification=?', (date, time, 0))

    connect.commit()
    cursor.close()


def delete_notification():
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()

    date = datetime.today().date().strftime('%d.%m.%Y')

    time = (datetime.now() - timedelta(minutes=1)).strftime("%H:%M")

    cursor.execute('DELETE FROM diary_db WHERE date=? and time=? and notification=?', (date, time, 1))

    connect.commit()
    cursor.close()


def clean_db():  # очистка БД каждую ночь; удаляет дела вчерашнего дня, для которых не установлено время
    date = datetime.today().date() - timedelta(days=1)
    connect = sqlite3.connect('..\\db\\main_db.db')
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM diary_db WHERE date=?', (date,))
    records = cursor.fetchall()
    if records:
        cursor.execute('DELETE FROM diary_db WHERE date=?', (date,))
    connect.commit()
    cursor.close()
