import telebot
import requests
import os
import logging
import json

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from db import DataBase

from dotenv import load_dotenv, find_dotenv

# Загружаем переменные окружения
load_dotenv(find_dotenv())

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

db = DataBase()

def update_review_status(api_key, review_id, was_viewed):
    """
    Обновляет статус отзыва на маркетплейсе Вайлдбериз.

    Args:
        api_key (str): API-ключ продавца.
        review_id (str): Идентификатор отзыва.
        was_viewed (bool): Просмотрен (True) или не просмотрен (False).

    Returns:
        bool: True, если обновление статуса прошло успешно, иначе False.
    """
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "id": review_id,
        "wasViewed": was_viewed
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return True
    else:
        return False
    

# Функция для получения отзывов
def fetch_reviews(api_key, chat_id):
    logger.info(f"Попытка получения отзывов для chat_id: {chat_id} с использованием API-ключа Wildberries")

    # Тело функции остается прежним, за исключением отправки сообщений
    api_url = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks'
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {'isAnswered': False, 'take': 10, 'skip': 0}

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        reviews_data = response.json()['data']['feedbacks']
        logger.info(f"Получено {len(reviews_data)} отзывов")
        return reviews_data
    else:
        logger.error(f"Ошибка при получении списка отзывов: {response.status_code}")
        logger.error(response.text)
        return []  # Возвращаем пустой список в случае ошибки
    
def send_feedback(review_id, text, api_key):
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    url = 'https://feedbacks-api.wb.ru/api/v1/feedbacks'

    data = {
        'id': review_id,  # Используется идентификатор отзыва
        'text': text
    }
    json_data = json.dumps(data)

    res = requests.patch(url=url, headers=headers, data=json_data)

    if res.status_code == 200:
        return True
    else:
        logger.error(f"Ошибка при отправке ответа: {res.status_code} {res.text}")
        return False
