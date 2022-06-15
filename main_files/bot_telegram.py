from aiogram import executor
from create_bot import dp
from handlers.first_lvl.main_handlers import main_handlers_registration
from handlers.first_lvl.doings_handlers import doings_handlers_registration
from db.clean_database import clean_db
from handlers.first_lvl.notifications_handlers import notif_handlers_registration
from main_files.common import scheduler
from handlers.first_lvl.send_msg import send_morning_msg


async def on_startup(_):
    print('Бот онлайн')
    scheduler.add_job(send_morning_msg, 'cron', hour='0', minute='2', second='35')
    scheduler.add_job(clean_db, 'cron', hour='0', minute='0', second='0')
    scheduler.start()


main_handlers_registration(dp)
doings_handlers_registration(dp)
notif_handlers_registration(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
