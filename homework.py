import logging
import os
import sys

import requests
from dotenv import load_dotenv

from telegram import Bot
import time


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params,
    ).json()
    return response


def check_response(response):
    if response.status_code == requests.codes.ok:
        return response.get('homeworks')[0]


def parse_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    try:
        if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            return True
    except Exception as err:
        logging.error(f'Отсутствует обязательная переменная окружения')
        logging.error('Программа принудительно остановлена.')
        sys.exit()


def main():
    """Основная логика работы бота."""

    logging.basicConfig(
        level=logging.DEBUG,
        filename='program.log',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    check_tokens()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            response = check_response(response)
            status = parse_status(response)
            send_message(bot, status)
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
