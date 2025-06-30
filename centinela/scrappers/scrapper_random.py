import random
import logging

import centinela.data_box
from centinela.data_box import DataBox, DataBoxVerkami
from centinela.scrappers.scrapper import Scrapper

logger = logging.getLogger(__name__)

class ScrapperRandom(Scrapper):
    """
    Clase Scrapper que simula operaciones de scrapper desde una web o fuente
    de datos externa. Implementa la interfaz Scrapper.
    """

    def __init__(self, titulo: str, url: str | None = None):
        super().__init__(titulo, url)

        # Probabilidad de que la nueva solicitud de datos devuelva valores diferentes
        # a los generados anteriormente
        self._ratio_valores_nuevos = 0.14

        # Valores iniciales - Primera lectura
        self._lectura = DataBoxVerkami()
        self._lectura.datos.titulo = titulo
        self._lectura.datos.restante = random.choices(
                population=[2, 8, 10],  weights=[100, 1, 1]            )[0]
        self._lectura.datos.unidades = "Dias"
        self._lectura.datos.aportaciones = 0
        self._lectura.datos.objetivo = random.randint(10, 100) * 1000
        self._lectura.datos.total = 0
        self._lectura.datos.set_fecha()

    def hemos_terminado(self) -> bool:
        return self._lectura.datos.restante < 1


    def leer_datos(self) -> DataBox:
        if not self.hemos_terminado():
            # Determina si ha de simularse que los datos de origen han cambiado
            if self._lectura.datos.total == 0:
                # Fuerza a que la primera vez siempre lea datos nuevos
                hay_datos_nuevos = True
            else:
                hay_datos_nuevos = random.choices(
                    population=[True, False],
                    weights=[self._ratio_valores_nuevos, 1 - self._ratio_valores_nuevos]
                )[0]

            # Si los datos han cambiado calcula los "delta" de cada dato para
            # calcular con ellos los nuevos datos que van a simular a los datos leídos
            if hay_datos_nuevos:
                delta_restante = random.choices(population=[0, 1], weights=[25, 75])[0]
                delta_aportaciones = random.randint(5, 20)
                delta_total = sum([random.randint(10, 100) for _ in range(delta_aportaciones)])
                lectura = DataBoxVerkami()
                lectura.datos.titulo = self._titulo
                lectura.datos.set_fecha()
                lectura.datos.restante = self._lectura.datos.restante - delta_restante
                lectura.datos.unidades = "Dias"
                lectura.datos.aportaciones = self._lectura.datos.aportaciones + delta_aportaciones
                lectura.datos.objetivo = self._lectura.datos.objetivo
                lectura.datos.total = self._lectura.datos.total + delta_total
                self._lectura = lectura

                if self.hemos_terminado():
                    self._lectura.datos.titulo = self.titulo + "(TERMINADO)"
                    self._lectura.datos.restante = 0   # para evitar que sea < 0

        return self._lectura


if __name__ == "__main__":
     # pruebas del módulo
    def run(scr: Scrapper) -> centinela.data_box.DataBoxVerkami:
        return scr.leer_datos()
    ant = 0
    s = ScrapperRandom(titulo="Prueba de Random Scrapper", url="none")
    for i in range(30):
        databox = run(s)
        nuevos = "Datos nuevos -- " if databox.datos.total != ant else "--------------- "
        print(f"{nuevos}  {i:02} -- {databox.datos}")
        ant = databox.datos.total

