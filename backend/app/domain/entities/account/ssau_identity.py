from app.domain.entities.base import TimestampedEntity


class SsauIdentityEntity(TimestampedEntity):
    """SSAU-идентичность аккаунта: учётные данные lk.ssau.ru.

    Привязывается на ``/auth``; наличие сущности = аккаунт авторизован в СНИУ.
    ``password`` в домене — открытый текст; шифрование на границе мапера репозитория.
    """

    account_id: int
    login: str
    password: str
