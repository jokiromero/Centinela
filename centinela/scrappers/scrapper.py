import logging

from abc import ABC, abstractmethod
from centinela.data_box import DataBox


logger = logging.getLogger(__name__)


class Scrapper(ABC):
    """
    Clase abstracta Scrapper. Define el comportamiento genérico de
    un objeto Scrapper capaz de leer datos de cierta url y devolverlos
    mediante 'leer_datos()'
    """
    def __init__(self, url: str, *args, **kwargs):
        self._lectura_nueva: DataBox | None = None
        self._url = url

    @abstractmethod
    def hemos_terminado(self) -> bool:
        """
        Devuelve True si el proceso de scrapping tiene un final y si este final
        ha sido alcanzado ya.
        """
        pass

    @abstractmethod
    def leer_datos(self) -> DataBox:
        """
        Cada subclase deberá definir aquí los pasos a realizar para llevar a cabo
        la operación de scrapping y devolver los datos leídos

        :return: Una instancia de una subclase de DataBox conteniendo los datos leídos
        """
        pass

    # noinspection PyProtectedMember
    @property
    def datos(self) -> DataBox._Datos:
        return self._lectura_nueva.datos


    @abstractmethod
    def datos_cambiados(self) -> bool:
        pass