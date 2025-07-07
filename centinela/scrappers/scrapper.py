# Sirve para poder usar "forward reference" que son declaraciones
# y usos de anotaciones sobre tipos o clases que se definen más
# adelante en el código (future)
from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from centinela.data_box import Databox


logger = logging.getLogger(__name__)


class Scrapper(ABC):
    """
    Clase abstracta Scrapper. Define el comportamiento genérico de
    un objeto Scrapper capaz de leer datos de cierta url y devolverlos
    mediante 'leer_datos()'
    """
    def __init__(self, url: str, titulo: str, *args, **kwargs):
        self._datos: Databox._Datos | None = None
        self._url = url
        self._titulo = titulo

    @abstractmethod
    def hemos_terminado(self) -> bool:
        """
        Devuelve True si el proceso de scrapping tiene un final y si este final
        ha sido alcanzado ya.
        """
        pass

    @abstractmethod
    def leer_datos(self) -> Databox._Datos:
        """
        Cada subclase deberá definir aquí los pasos a realizar para llevar a cabo
        la operación de scrapping y devolver los datos leídos

        :return: Una instancia de una subclase de Databox conteniendo los datos leídos
        """
        pass

    # noinspection PyProtectedMember
    @property
    def datos(self) -> Databox._Datos:
        return self._datos

    @property
    def url(self):
        return self._url
