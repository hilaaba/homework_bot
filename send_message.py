import os
import logging
import sys
from telegram import Bot

from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    filemode='a',
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',

)


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


def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        message = f'Сообщение отправлено в чат: {TELEGRAM_CHAT_ID}'
        logging.info(message)
    except Exception as error:
        message = f'При попытке отправки сообщения произошла ошибка: {error}'
        logging.exception(message)


def main():
    check_tokens()
    bot = Bot(token=TELEGRAM_TOKEN)
    message = 'Первое сообщение!'
    send_message(bot, message)


main()
