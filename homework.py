import logging
import os
import sys
import time

import requests
import telegram.error
from dotenv import load_dotenv
from telegram import Bot

from exceptions import (
    BotUnauthorizedError, SendMessageError, EndpointAPIError, RequestAPIError,
    AnotherStatusError,
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Bot отправляет сообщение в Telegram."""
    logger.info('Bot начал отправку сообщения в Telegram.')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.Unauthorized as error:
        raise BotUnauthorizedError from error
    except telegram.error.TelegramError as error:
        error_message = (
            f'При попытке отправки сообщения произошла ошибка: {error}'
        )
        raise SendMessageError(error_message) from error
    else:
        logger.info(f'Bot отправил новое сообщение: "{message}"')


def get_api_answer(current_timestamp):
    """Отправляет запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
        if response.status_code != requests.codes.ok:
            message = (
                f'Эндпоинт {ENDPOINT} недоступен.\n'
                f'Код ответа API: {response.status_code}'
            )
            raise EndpointAPIError(message)
        return response.json()
    except Exception as error:
        message = (
            f'Произошёл сбой при запросе к эндпоинту {ENDPOINT}\n'
            f'Ошибка: {error}'
        )
        raise RequestAPIError(message)


def check_response(response):
    """Проверяет ответ от API."""
    if not isinstance(response, dict):
        raise TypeError('response не является словарем.')
    for key in ('homeworks', 'current_date'):
        if key not in response:
            raise KeyError(f'В response отсутствует ключ: {key}.')
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
    if homework_status not in HOMEWORK_VERDICTS:
        raise AnotherStatusError('Недокументированный статус домашней работы.')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет обязательные переменные окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def check_program_starting():
    """Проверяет запуск программы."""
    if not check_tokens():
        logger.critical(
            'Отсутствует обязательная переменная окружения.\n'
            'Программа принудительно остановлена.'
        )
        sys.exit()
    logger.info('Программа запущена.')


def main():
    """Основная логика работы бота."""
    check_program_starting()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_homework = 0
    previous_homeworks = list()
    previous_error = Exception()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logger.debug(
                    'В настоящее время на проверке нет домашней работы или '
                    'ревьюер еще не начал проверку.'
                )
            elif previous_homeworks != homeworks:
                status = parse_status(homeworks[last_homework])
                send_message(bot, status)
                logger.info(status)
                previous_homeworks = homeworks
            else:
                logger.debug('Статус домашней работы не изменился.')
            current_timestamp = response.get('current_date')
        except BotUnauthorizedError:
            logger.critical(
                'У Bot недостаточно прав для выполнения запроса. '
                'Возможно неправильно задан TELEGRAM_TOKEN.\n'
                'Программа принудительно остановлена.'
            )
            sys.exit()
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            try:
                if previous_error.args != error.args:
                    send_message(bot, message)
                    previous_error = error
            except SendMessageError as error:
                logger.error(
                    'Bot не смог отправить сообщение об ошибке в Telegram.'
                    f'{error}'
                )
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename='app.log',
        filemode='a',
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
        encoding='utf-8',
    )
    main()
