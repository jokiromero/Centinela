
from centinela.datos_persistentes import Lectura
from scrappers.scrapper import Scrapper
from collections import OrderedDict
from copy import copy
from faker import Faker


class ScrapperRandom(Scrapper):
    """
    Clase Scrapper que simula operaciones de scrapper desde una web o fuente
    de datos externa. Implementa la interfaz Scrapper.
    """
    def __init__(self, titulo: str, url: str):
        super().__init__(titulo, url)
        self._fake = Faker()
        self._ratio_valores_nuevos = 0.4

        self._lectura = Lectura(
            titulo = "Dats sintéticos",
            aportaciones = 0,
            objetivo = self._fake.random_int(1000, 100000),
            total = 0
        )
        self._lectura.set_fecha()
        self._primera_vez = True



    def leer_datos(self) -> Lectura | None:
        if self._primera_vez:
            self._primera_vez = False
            return self._lectura

        self._datos_nuevos = True if self._fake.ran

        lectura = Lectura(
            titulo=self.titulo,
            fecha=Scrapper._get_timestamp(),
            restante=valor_campo1,
            unidades=etiq_campo1,
            aportaciones=valor_campo2,
            objetivo=importe_objetivo,
            total=importe_recaudado,
        )

        return lectura
