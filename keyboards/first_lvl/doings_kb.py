from aiogram.types import InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import emoji

btn_1 = KeyboardButton(emoji.emojize(':left_arrow: Назад'))
btn_2 = KeyboardButton(emoji.emojize('Добавить дело :memo:'))
btn_3 = KeyboardButton(emoji.emojize('Удалить дело :cross_mark:'))
edit_kb = ReplyKeyboardMarkup(resize_keyboard=True)
edit_kb.row(btn_2, btn_3).add(btn_1)

add_doings = InlineKeyboardButton('Да', callback_data='add_doings')
dont_add_doings = InlineKeyboardButton('Нет', callback_data='dont_add_doings')
add_doings_kb = InlineKeyboardMarkup(row_width=2).row(add_doings, dont_add_doings)

acception_yes = InlineKeyboardButton('Да', callback_data='accept')
acception_no = InlineKeyboardButton('Нет', callback_data='dont_accept')
acception_kb = InlineKeyboardMarkup(row_width=2).row(acception_yes, acception_no)

change_date = InlineKeyboardButton('Дату', callback_data='date')
change_doing = InlineKeyboardButton('Название дела', callback_data='doing')
change_kb = InlineKeyboardMarkup(row_width=2).row(change_date, change_doing)

add_time_yes = InlineKeyboardButton('Да', callback_data='add_time')
add_time_no = InlineKeyboardButton('Нет', callback_data='dont_add_time')
add_time_kb = InlineKeyboardMarkup(row_width=2).row(add_time_yes, add_time_no)




