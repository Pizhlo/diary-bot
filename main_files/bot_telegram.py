from aiogram import executor
from create_bot import dp
from handlers.first_lvl.main_handlers import main_handlers_registration
from handlers.first_lvl.doings_handlers import doings_handlers_registration, send_morning_msg


async def on_startup(_):
    print('Бот онлайн')


main_handlers_registration(dp)
doings_handlers_registration(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
