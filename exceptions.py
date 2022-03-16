class ExceptionDontRequireSendingToTelegram(Exception):
    """Исключения, которые не требуют отправки сообщения в Телеграм."""
    pass


class SendMessageError(ExceptionDontRequireSendingToTelegram):
    """Возникает, когда бот не может отправить сообщение в Телеграм."""
    pass


class UnauthorizedError(ExceptionDontRequireSendingToTelegram):
    """Возникает, когда у бота недостаточно прав для выполнения запроса."""
    pass


class ExceptionRequireSendingToTelegram(Exception):
    """Исключения, которые требуют отправки сообщения в Телеграм."""
    pass


class EndpointAPIError(ExceptionRequireSendingToTelegram):
    """Возникает, когда код ответа HTTP отличный от 200."""
    pass


class RequestAPIError(ExceptionRequireSendingToTelegram):
    """Возникает, когда не удалось выполнить запрос к API."""


class TokenError(ExceptionRequireSendingToTelegram):
    """Возникает, когда отсутствует обязательная переменная окружения."""
    pass
