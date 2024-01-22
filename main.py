import telebot
import openai
import os
import logging
from telebot import types

from yookassa_integration import SubscriptionBot
from apscheduler.schedulers.background import BackgroundScheduler

from db import DataBase
from subscription_handlers import process_some_command
from wildberries_api import fetch_reviews, send_feedback
from markups import sub_keyboard

from dotenv import load_dotenv, find_dotenv


# Загружаем переменные окружения
load_dotenv(find_dotenv())

# Создаем экземпляр бота с использованием токена из переменных окружения
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# Настройка базового логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Запуск приложения")

# Создаем экземпляр базы данных
db = DataBase()

sub = SubscriptionBot()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def bot_start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Проверка, существует ли имя и фамилия пользователя
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    if_message = f'Добро пожаловать {first_name} {last_name}! \n\n Для оформления подписки пожалуйста выберите удобный вам период.'
    else_message = f'Мы рады вас видеть снова {first_name} {last_name}! \n\n Для оформления подписки пожалуйста выберите удобный вам период.'

    if not db.user_exists(user_id):
        # Если пользователь не существует, добавляем его с chat_id
        db.add_user(message.from_user.id, message.chat.id)
        bot.send_message(chat_id, if_message, reply_markup=sub_keyboard)
    else:
        # Если пользователь существует, обновляем его chat_id
        db.update_user_chat_id(user_id, chat_id)
        bot.send_message(chat_id, else_message, reply_markup=sub_keyboard)

# Добавим обработчик для предварительного запроса перед оплатой.
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    sub.process_pre_checkout_query(pre_checkout_query)

# Добавим обработчик для успешной оплаты.
@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    sub.handle_successful_payment(message)

@bot.message_handler(commands=['some_command'])
def handle_some_command(message):
    process_some_command(bot, message)

# Обработчик для добавления API токена
def process_api_token(message):
    api_token_wb = message.text
    # Обновляем API токен пользователя в базе данных
    db.update_api_wb(message.chat.id, api_token_wb)
    # Отправляем сообщение об успешном обновлении
    bot.send_message(message.chat.id, 'API токен успешно добавлен!')

# Функция для генерации ответов на отзывы с помощью ChatGPT
def generate_response_with_chatgpt(review_text):
    # Логирование входного текста отзыва
    logger.info(f"generate_response_with_chatgpt called with review_text: {review_text}")

    try:
        # Формирование сообщения для ChatGPT
        message = [
            {"role": "system", "content": "Вы менеджер компании, который отвечает на отзывы покупателей в маркетплейсе Вайлбериз только на русском языке. Ваша задача — предоставлять вежливые и короткие ответы, без предложения контактной информации или задавания дополнительных вопросов."},
            {"role": "user", "content": review_text},     
        ]
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Запрос к ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",  # Измените название модели здесь
            messages=message
        )

        # Получение сгенерированного ответа
        generated_response = response.choices[0].message['content']
        # Логирование сгенерированного ответа
        logger.info(f"Generated response from ChatGPT: {generated_response}")

        return generated_response
    
    except Exception as e:
        # Логирование ошибок при генерации ответа
        logger.error(f"Ошибка при генерации ответа: {e}")
        return None


# Функция для регулярного получения отзывов
# Функция для регулярного получения отзывов
def periodic_fetch_reviews():
    user_data = db.get_all_users()  # Получение данных всех пользователей

    for user in user_data:
        user_id, chat_id, api_key = user

        if not api_key:
            continue

        reviews = fetch_reviews(api_key, chat_id)

        if not reviews:
            continue

        for review in reviews:
            logger.info(f"Обработка отзыва: {review['text'][:30]}... для пользователя {user_id}")

            # Генерация ответа с использованием ChatGPT
            response_text = generate_response_with_chatgpt(review['text'])

            if response_text:
                # Создание клавиатуры с кнопкой "Ответить"
                markup = types.InlineKeyboardMarkup()
                btn = types.InlineKeyboardButton('Ответить', callback_data=f'send {review["id"]}')
                markup.add(btn)

                # Отправка сообщения с отзывом и кнопкой
                bot.send_message(chat_id, f"Отзыв: \n{review['text']}")
                bot.send_message(chat_id, f"{response_text}", reply_markup=markup)


            else:
                logger.error(f"Не удалось сгенерировать ответ для отзыва {review['text'][:30]}...")

@bot.callback_query_handler(func=lambda call: True)
def hendle_query_call(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    api_key = db.get_api_token_wb(user_id)

    split_call = call.data.split()

    if call.data == 'add_api':
        # Отправляем сообщение о необходимости добавить API токен
        bot.send_message(call.message.chat.id, 'Добавьте API токен')
        # Регистрируем обработчик следующего сообщения пользователя
        bot.register_next_step_handler(call.message, process_api_token)

    elif split_call[0] == 'send' and len(split_call) > 1:
        review_id = split_call[1]  # Идентификатор отзыва

        response_text = generate_response_with_chatgpt(call.message.text)  # Генерация ответа на основе текста сообщения

        if response_text:
            send_result = send_feedback(review_id, response_text, api_key)  # Отправка сгенерированного ответа в Wildberries

            if send_result:
                bot.send_message(chat_id, "Ваш ответ был успешно отправлен")
            else:
                bot.send_message(chat_id, "Произошла ошибка. Попробуйте ещё раз.")
        else:
            bot.send_message(chat_id, "Не удалось сгенерировать ответ.")

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        logger.info(f"Сообщение с ID {call.message.message_id} удалено из чата {chat_id}")

    else:
        sub.sub_query(call)

# Настройка планировщика
scheduler = BackgroundScheduler()
scheduler.add_job(periodic_fetch_reviews, 'interval', minutes=1)  # Например, каждые 10 минут
scheduler.start()

if __name__ == '__main__':
    bot.polling(none_stop=True)