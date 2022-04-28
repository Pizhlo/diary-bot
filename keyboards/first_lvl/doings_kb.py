from aiogram.types import InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import emoji

btn_1 = KeyboardButton(emoji.emojize('Назад'))
btn_2 = KeyboardButton(emoji.emojize('Добавить дело'))
btn_3 = KeyboardButton(emoji.emojize('Удалить дело'))

edit_kb = ReplyKeyboardMarkup(resize_keyboard=True)
edit_kb.row(btn_1, btn_2).add(btn_3)

add_doings = InlineKeyboardButton('Да', callback_data='add_doings')
dont_add_doings = InlineKeyboardButton('Нет', callback_data='dont_add_doings')

add_doings_kb = InlineKeyboardMarkup(row_width=2).row(add_doings, dont_add_doings)

acception_yes = InlineKeyboardButton('Да', callback_data='accept')
acception_no = InlineKeyboardButton('Нет', callback_data='dont_accept')

acception_kb = InlineKeyboardMarkup(row_width=2).row(acception_yes, acception_no)

change_time = InlineKeyboardButton('Дату', callback_data='time')
change_doing = InlineKeyboardButton('Название дела', callback_data='doing')

change_kb = InlineKeyboardMarkup(row_width=2).row(change_time, change_doing)


