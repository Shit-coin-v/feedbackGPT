import telebot
from telebot import types

import time
import os

from db import DataBase
from subscription_utils import days_to_seconds
from markups import custom_keyboard, sub_keyboard

from dotenv import load_dotenv, find_dotenv


class SubscriptionBot:
    """
    Бот для управления подписками.

    Этот класс предназначен для управления подписками пользователей в Telegram.
    Он предоставляет функциональность по отправке счетов, обработке платежей 
    и управлению статусами подписок в базе данных.

    Attributes:
        _SUBSCRIPTION_PLANS: Словарь, содержащий доступные планы подписки и их параметры.
    """
    
    # Словарь, содержащий планы подписки и их параметры
    _SUBSCRIPTION_PLANS = {
    'sub_1_month': {
        'description': 'Подписка на 1 месяц',
        'duration': 30,
        'price': 15000,
        'label': 'Руб'
    },
    'sub_3_month': {
        'description': 'Подписка на 3 месяца',
        'duration': 90,
        'price': 30000,
        'label': 'Руб'
    },
    'sub_6_month': {
        'description': 'Подписка на 6 месяцев',
        'duration': 180,
        'price': 45000,
        'label': 'Руб'
    },
    'sub_1_year': {
        'description': 'Подписка на 1 год',
        'duration': 365,
        'price': 60000,
        'label': 'Руб'
    }
}
    def __init__(self):
        """Инициализатор класса."""
        # Загрузка переменных окружения
        self._load_env_variables()
        
        # Инициализация базы данных
        self.db = DataBase()
        
        # Инициализация бота Telegram с загруженным токеном
        self.bot = telebot.TeleBot(self.TELEGRAM_BOT_TOKEN)

    def _load_env_variables(self):
        """Метод для загрузки переменных окружения."""
        load_dotenv(find_dotenv())
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.API_KEY = os.getenv("YOO_TOKEN")


    def sub_query(self, call):
        """Метод обрабатывает запросы на покупку подписки."""
        plan = SubscriptionBot._SUBSCRIPTION_PLANS.get(call.data)
        if plan:
            self.bot.send_invoice(
                chat_id=call.from_user.id, 
                title='Оформление подписки', 
                description=plan['description'], 
                invoice_payload=call.data, 
                provider_token=self.API_KEY,
                currency='RUB',
                start_parameter='test',
                prices=[types.LabeledPrice(label=plan['label'], amount=plan['price'])]
            )
        elif call.data == 'subscription':
            self.bot.send_message(call.from_user.id, "Пожалуйста выберите тариф", reply_markup=sub_keyboard)
        else:
            # Ошибка: неизвестный тариф
            self.bot.send_message(call.from_user.id, "Произошла ошибка. Попробуйте ещё раз.УУУУУУУУУУУ")

    def process_pre_checkout_query(self, pre_checkout_query: types.PreCheckoutQuery):
        """Обработка предварительного запроса перед осуществлением платежа."""
        self.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    def handle_successful_payment(self, message):
        """Обработка успешного платежа."""
        # Устанавливаем статус подписки пользователя как "done"
        self.db.set_signup(message.from_user.id, 'done')
        
        plan = SubscriptionBot._SUBSCRIPTION_PLANS.get(message.successful_payment.invoice_payload)
        if plan:
            # Установка времени истечения подписки в базе данных
            time_sub = int(time.time()) + days_to_seconds(plan['duration'])
            self.db.set_time_sub(message.from_user.id, time_sub)
            # Отправка сообщения об успешной оплате
            self.bot.send_message(message.chat.id, f'Вы оформили {plan["description"].lower()}', reply_markup=custom_keyboard)
        else:
            # Ошибка при неизвестном плане подписки
            self.bot.send_message(message.chat.id, "Произошла ошибка при обработке вашего платежа. Пожалуйста, свяжитесь со службой поддержки.")


# eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjMxMDI1djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcxODk5MTc4OSwiaWQiOiJiY2Y5ZDUyMC02MmYxLTQyOGMtYjE4YS01MDc1M2FlZmM2NDMiLCJpaWQiOjUzNDM0OTQ0LCJvaWQiOjY2Njk2LCJzIjoxMjgsInNpZCI6ImNiMzA5Y2M1LTE1MjktNWRiNS05OWM3LWMwMDJjMTczNTRiNCIsInQiOmZhbHNlLCJ1aWQiOjUzNDM0OTQ0fQ.5Amb83EYlAu477WC74lu1W_Jjz_-qQi-ckIdvg6DSYuulGeYblpl4wZTxhitw_-O4VEtxLnVI4IIuUZJpW9Fxw