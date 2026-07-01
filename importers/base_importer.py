from abc import ABC, abstractmethod

from models.deck import Deck


class BaseImporter(ABC):
    """
    Базовый класс для всех импортеров колод.
    """

    @abstractmethod
    def load(self, source) -> Deck:
        """
        Загрузить колоду из источника.
        """
        pass
