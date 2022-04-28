from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

btn_1 = KeyboardButton(emoji.emojize('Список дел :notebook:'))
btn_2 = KeyboardButton(emoji.emojize('Список напоминаний :alarm_clock:'))

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row(btn_1, btn_2)