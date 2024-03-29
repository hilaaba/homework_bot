## Проект homework_bot

### Описание
Это Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус домашней работы.

### Технологии
Python

### Что он умеет?
- раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы
- при обновлении статуса анализировать ответ API и отправлять соответствующее уведомление в Telegram
- логировать свою работу и сообщать о важных проблемах сообщением в Telegram

### Запуск проекта в dev-режиме


+ Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/hilaaba/homework_bot.git
```

```
cd homework_bot
```
+ Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

+ Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
