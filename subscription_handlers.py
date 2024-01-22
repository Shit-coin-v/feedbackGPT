from subscription_utils import has_valid_subscription

from db import DataBase
from markups import sub_keyboard

db = DataBase()

def process_some_command(bot, message):
    if has_valid_subscription(message.from_user.id, db):

        do_some_action(bot, message)
    else:
        bot.send_message(message.chat.id, "Ваша подписка истекла или не была активирована. Пожалуйста, продлите ее.", reply_markup=sub_keyboard)

def do_some_action(bot, message):
    bot.send_message(message.chat.id, "Выполняю команду, так как у вас активная подписка!")


