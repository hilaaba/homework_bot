class ExceptionDontRequireSendingToTelegram(Exception):
    """Исключения, которые не требуют отправки сообщения в Телеграм"""
    pass


class SendMessageError(ExceptionDontRequireSendingToTelegram):
    """Возникает, когда бот не может отправить сообщение в Телеграм."""
    pass


class UnauthorizedError(ExceptionDontRequireSendingToTelegram):
    """Возникает, когда у бота недостаточно прав для выполнения запроса."""
    pass


class ExceptionRequireSendingToTelegram(Exception):
    """Исключения, которые требуют отправки сообщения в Телеграм"""
    pass


class AnotherStatusError(ExceptionRequireSendingToTelegram):
    pass


class EndpointAPIError(ExceptionRequireSendingToTelegram):
    pass


class TokenError(ExceptionRequireSendingToTelegram):
    """Возникает, когда отсутствует обязательная переменная окружения."""
    pass


class HomeworkNameError(ExceptionRequireSendingToTelegram):
    pass
