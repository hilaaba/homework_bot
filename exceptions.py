class DontSendException(Exception):
    """Исключения, которые не требуют отправки сообщения в Телеграм."""

    pass


class SendMessageError(DontSendException):
    """Возникает, когда бот не может отправить сообщение в Телеграм."""

    pass


class BotUnauthorizedError(DontSendException):
    """Возникает, когда у бота недостаточно прав для выполнения запроса."""

    pass


class SendException(Exception):
    """Исключения, которые требуют отправки сообщения в Телеграм."""

    pass


class EndpointAPIError(SendException):
    """Возникает, когда код ответа HTTP отличный от 200."""

    pass


class RequestAPIError(SendException):
    """Возникает, когда не удалось выполнить запрос к API."""

    pass


class AnotherStatusError(SendException):
    """Возникает, когда недокументированный статус домашней работы."""

    pass
