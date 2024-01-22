import telebot

import os

from db import DataBase

from dotenv import load_dotenv, find_dotenv


db = DataBase()

# Загружаем переменные окружения
load_dotenv(find_dotenv())

# Создаем экземпляр бота с использованием токена из переменных окружения
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

def has_valid_subscription(user_id, db):
    return db.get_sub_status(user_id)

def notify_users_about_expiration():
    # Получаем список пользователей, чья подписка истекает через 3 дня
    users_to_notify = db.get_users_with_expiring_subscriptions(days=3)
    for user in users_to_notify:
        bot.send_message(user.id, "Ваша подписка истекает через 3 дня! Пожалуйста, продлите ее, чтобы продолжить пользоваться нашим ботом.")

def handle_some_command(message):
    if not has_valid_subscription(message.from_user.id):
        bot.send_message(message.chat.id, "Ваша подписка истекла или не была активирована. Пожалуйста, продлите ее.")
        return
    
    # Ваш код для выполнения действия, если подписка активна
    bot.send_message(message.chat.id, "Выполняю команду, так как у вас активная подписка!")

def days_to_seconds(days):
    return days * 24 * 60 * 60

