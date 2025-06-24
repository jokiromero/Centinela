import logging

from abc import ABCMeta, abstractmethod
from typing import Any
from datetime import datetime

logger = logging.getLogger(__name__)

class Scrapper(metaclass=ABCMeta):
    """
    Clase abstracta Scrapper.
    Define el comportamiento genérico de un objeto Scrapper
    capaz de leer datos de cierta url y devolverlos mediante el método leer_datos

    """
    def __init__(self, titulo: str, url: str):
        self._titulo = titulo
        self._url = url

    @abstractmethod
    def hemos_terminado(self) -> bool:
        return False

    @abstractmethod
    def leer_datos(self) -> Any:
        pass

    @staticmethod
    def _get_timestamp() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def titulo(self) -> str:
        return self._titulo

