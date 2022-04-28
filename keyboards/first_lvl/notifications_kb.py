from aiogram.types import InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import emoji

add_notif = InlineKeyboardButton('Да', callback_data='make_notif')
dont_add_notif = InlineKeyboardButton('Нет', callback_data='dont_make_notif')
add_notif_kb = InlineKeyboardMarkup(row_width=2).row(add_notif, dont_add_notif)

btn_1 = KeyboardButton(emoji.emojize(':left_arrow: Назад'))
btn_2 = KeyboardButton(emoji.emojize('Добавить напоминание :memo:'))
btn_3 = KeyboardButton(emoji.emojize('Удалить напоминание :cross_mark:'))
edit_kb = ReplyKeyboardMarkup(resize_keyboard=True)
edit_kb.row(btn_2, btn_3).add(btn_1)

acception_yes = InlineKeyboardButton('Да', callback_data='accept_notif')
acception_no = InlineKeyboardButton('Нет', callback_data='dont_accept_notif')
acception_kb = InlineKeyboardMarkup(row_width=2).row(acception_yes, acception_no)