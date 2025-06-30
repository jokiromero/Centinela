import random
import logging

from centinela.data_box import DataBox, DataBoxVerkami
from centinela.scrappers.scrapper import Scrapper

logger = logging.getLogger(__name__)


class ScrapperRandom(Scrapper):
    """
    Clase Scrapper que simula operaciones de scrapper desde una web o fuente
    de datos externa. Implementa la interfaz Scrapper.
    """

    def __init__(self, url: str, titulo: str):
        super().__init__(url=url)

        # Probabilidad de que la nueva solicitud de datos devuelva valores diferentes
        # a los generados anteriormente
        self._ratio_valores_nuevos = 0.14

        # Valores iniciales - Primera lectura
        self._data_box = DataBoxVerkami()
        self._data_box.datos.titulo = titulo
        self._data_box.datos.restante = random.choices(
                population=[2, 8, 10],  weights=[100, 1, 1]            )[0]
        self._data_box.datos.unidades = "Dias"
        self._data_box.datos.aportaciones = 0
        self._data_box.datos.objetivo = random.randint(10, 100) * 1000
        self._data_box.datos.total = 0
        self._data_box.datos.set_fecha()


    def hemos_terminado(self) -> bool:
        return self._data_box.datos.restante < 1


    def leer_datos(self) -> DataBoxVerkami:
        if not self.hemos_terminado():
            # Determina si ha de simularse que los datos de origen han cambiado
            if self._data_box.datos.total == 0:
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
                lectura.datos.restante = self._data_box.datos.restante - delta_restante
                lectura.datos.unidades = "Dias"
                lectura.datos.aportaciones = self._data_box.datos.aportaciones + delta_aportaciones
                lectura.datos.objetivo = self._data_box.datos.objetivo
                lectura.datos.total = self._data_box.datos.total + delta_total
                self._data_box = lectura

                if self.hemos_terminado():
                    self._data_box.datos.titulo = self.titulo + "(TERMINADO)"
                    self._data_box.datos.restante = 0   # para evitar que sea < 0

        return self._data_box



if __name__ == "__main__":
     # pruebas del módulo
    def run(scr: Scrapper) -> DataBoxVerkami:
        return scr.leer_datos()
    ant = 0
    s = ScrapperRandom(url="ninguna", titulo="Prueba de Random Scrapper")
    for i in range(30):
        databox = run(s)
        nuevos = "Datos nuevos -- " if databox.datos.total != ant else "--------------- "
        print(f"{nuevos}  {i:02} -- {databox.datos}")
        ant = databox.datos.total
