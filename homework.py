import logging
import os
import sys
import time

import requests
import telegram.error
from dotenv import load_dotenv
from telegram import Bot

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

logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    filemode='a',
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    encoding='utf-8',
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Bot отправляет сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Bot отправил новое сообщение в Telegram.')
    except telegram.error.BadRequest as error:
        message = (
            'При попытке отправки сообщения в Telegram '
            f'произошла ошибка: {error}'
        )
        raise telegram.error.BadRequest(message)
    except telegram.error.Unauthorized:
        message = (
            'У Bot недостаточно прав для выполнения запроса. '
            'Возможно неправильно задан TELEGRAM_TOKEN.\n'
            'Программа принудительно остановлена.'
        )
        logger.critical(message, exc_info=True)
        sys.exit()


def get_api_answer(current_timestamp):
    """Отправляет запрос к API."""
    params = {'from_date': current_timestamp}
    response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params,
    )
    try:
        if response.status_code != requests.codes.ok:
            raise requests.RequestException
        return response.json()
    except requests.RequestException:
        message = (
            f'Эндпоинт {ENDPOINT} недоступен.\n'
            f'Код ответа API: {response.status_code}'
        )
        raise requests.RequestException(message)


def check_response(response):
    """Проверяет ответ от API."""
    if not isinstance(response, dict):
        raise TypeError('response не является словарем.')
    for key in ('homeworks', 'current_date'):
        if key not in response:
            raise KeyError(f'В response отсутствует ключ: {key}')
    homeworks = response.get('homeworks')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('homeworks не является списком.')
    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    for key in ('homework_name', 'status'):
        if key not in homework:
            raise KeyError(f'В homework отсутствует ключ: {key}.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        raise AssertionError('Недокументированный статус домашней работы.')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет обязательные переменные окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    try:
        if not check_tokens():
            raise KeyError
    except KeyError:
        logger.critical(
            'Отсутствует обязательная переменная окружения.\n'
            'Программа принудительно остановлена.'
        )
        sys.exit()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_homework = 0
    previous_homeworks = dict()
    previous_error = Exception()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logger.info(
                    'В настоящее время на проверке нет домашней работы или '
                    'ревьюер еще не начал проверку.'
                )
            elif previous_homeworks != homeworks:
                status = parse_status(homeworks[last_homework])
                send_message(bot, status)
                logger.info(status)
                previous_homeworks = homeworks
            else:
                logger.debug('Статус домашней работы не поменялся.')
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)
        except KeyboardInterrupt:
            logger.info('Программа остановлена.')
            sys.exit()
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            try:
                if previous_error.args != error.args:
                    send_message(bot, message)
                    previous_error = error
                    return previous_error
            except telegram.error.BadRequest:
                logger.error(
                    'Bot не смог отправить сообщение об ошибке в Telegram.'
                )
            logger.error(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
