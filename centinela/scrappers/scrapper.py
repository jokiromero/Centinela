from abc import ABCMeta, abstractmethod
from typing import Any
from datetime import datetime
from PIL.Image import Image


class Scrapper(metaclass=ABCMeta):
    """
    Clase abstracta Scrapper.
    Define el comportamiento genérico de un objeto Scrapper
    capaz de leer datos de cierta url y devolverlos mediante el método leer_datos

    """
    def __init__(self, url: str, nombre: str = "",
                 imagen: Image | None = None):
        self._url = url
        self._nombre = nombre
        self._imagen = imagen

    @abstractmethod
    def leer_datos(self) -> Any:
        pass

    @staticmethod
    def _get_timestamp() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def imagen(self) -> Image:
        return self._imagen

