# __future__.annotations sirve para poder usar "forward reference"
# que son declaraciones y usos de anotaciones sobre tipos o clases
# que se definen más adelante en el código (future)
from __future__ import annotations

import random
import logging

from centinela.data_box import DataboxVerkami
from centinela.scrappers.scrapper import Scrapper

logger = logging.getLogger(__name__)


class ScrapperRandom(Scrapper):
    """
    Clase Scrapper que simula operaciones de scrapper desde una web o fuente
    de datos externa. Implementa la interfaz Scrapper.
    """

    def __init__(self, url: str, titulo: str):
        super().__init__(url=url, titulo=titulo)

        # Probabilidad simulada de que la nueva solicitud de datos devuelva
        # valores diferentes a los recibidos anteriormente
        self._ratio_valores_nuevos = 0.50

        # Valores iniciales - Primera lectura
        self._datos = DataboxVerkami.new_datos(
            titulo=self._titulo,
            feedback="",
            resto_valor=random.choices(
                    population=[5, 16, 30],  weights=[100, 1, 1]
            )[0],
            resto_etiq="Dias",
            aporta_valor=0,
            aporta_etiq="Aportaciones",
            objetivo=random.randint(10, 100) * 1000,
            total=0
        )

    def hemos_terminado(self) -> bool:
        return (self._datos.resto_valor < 1
                and self._datos.resto_etiq.capitalize() == "Segundos")

    def leer_datos(self) -> DataboxVerkami._Datos:
        hay_datos_nuevos = False
        if self._ratio_valores_nuevos < 0 or self._ratio_valores_nuevos > 1:
            raise ValueError(f"Valor de self._ratio_valores_nuevos incorrecto: "
                             f"'{self._ratio_valores_nuevos}'. Debería estar "
                             f"entre 0.0 y 1.0")
        if not self.hemos_terminado():
            logger.debug("Simulador de scrapper generando datos aleatorios...")
            # Determina si ha de simularse que los datos de origen han cambiado
            if self._datos.total == 0:
                # Fuerza a que la primera vez siempre lea datos nuevos
                hay_datos_nuevos = True
            else:
                hay_datos_nuevos = random.random() < self._ratio_valores_nuevos

            # Si estamos simulando que hay datos nuevos, se generan 'deltas' para
            # representar los incrementos de valor que traen los nuevos datos leídos
            if hay_datos_nuevos:
                delta_restante = random.choices(population=[0, 1], weights=[30, 70])[0]
                delta_aportaciones = random.randint(5, 20)
                delta_total = sum([random.randint(10, 100) for _ in range(delta_aportaciones)])
                nuevo_restante = self._datos.resto_valor - delta_restante
                nuevo_titulo = self._titulo
                if nuevo_restante < 1:
                    nuevo_restante = 0
                    nuevo_titulo += " (TERMINADO) "
                self._datos = DataboxVerkami.new_datos(
                    titulo=nuevo_titulo,
                    feedback="Aquí se dice si este proyecto está en PREVENTA!!",
                    resto_valor=nuevo_restante,
                    resto_etiq="Días",
                    aporta_valor=self._datos.aporta_valor + delta_aportaciones,
                    aporta_etiq="Aportaciones",
                    objetivo=self._datos.objetivo,
                    total=self._datos.total + delta_total
                )

        return self._datos



if __name__ == "__main__":
     # pruebas del módulo
    def run(scr: ScrapperRandom) -> DataboxVerkami._Datos:
        return scr.leer_datos()

    ant = 0
    tot = 150
    s = ScrapperRandom(url="ninguna", titulo="Prueba de Random Scrapper")
    t1 = 0
    for i in range(tot):
        if s.hemos_terminado():
            break

        datos = run(s)
        if datos.total != ant:
            nuevos = "Datos nuevos -- "
            t1 += 1
        else:
            nuevos = "--------------- "
        print(f"{nuevos}  ({datos.resto_etiq:5s}) -- {i:02} -- {datos}")
        ant = datos.total

    print(f"{t1:3d} >> tot: {t1/tot:3.2f}")
