from abc import ABC


class BaseProvider(ABC):
    """
    Базовый класс для всех внешних источников данных.
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        """
        Проверка доступности сервиса.
        """
        return True
