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
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/dfgdfg/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    filemode='a',
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        message = f'Сообщение отправлено в чат: {TELEGRAM_CHAT_ID}'
        logging.info(message)
    except Exception as error:
        message = f'При попытке отправки сообщения произошла ошибка: {error}'
        logging.error(message)


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    timestamp = 0
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        ).json()
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError:
        status_code = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        ).status_code
        message = (
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {status_code}'
        )
        logging.error(message)


def check_response(response):
    try:
        if response.status_code == requests.codes.ok:
            return response.get('homeworks')[0]
        raise requests.HTTPError
    except requests.HTTPError as error:
        ...


def parse_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    try:
        if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            return True
        raise ValueError
    except ValueError:
        tokens = {
            'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
            'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
            'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
        }
        for name_token, token in tokens.items():
            if not token:
                message = (
                    f'Отсутствует обязательная '
                    f'переменная окружения: {name_token}.'
                )
                logging.critical(message)
        logging.critical('Программа принудительно остановлена.')
        sys.exit()


def main():
    """Основная логика работы бота."""

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
