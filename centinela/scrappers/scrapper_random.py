import random
import logging

from centinela.datos_persistentes import Lectura
from scrappers.scrapper import Scrapper

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
        self._lectura = Lectura(
            titulo=self.titulo,
            restante=random.choices(
                population=[2, 8, 10],
                weights=[100, 1, 1]
            )[0],
            unidades="Dias",
            aportaciones=0,
            objetivo=random.randint(10, 100) * 1000,
            total=0
        )
        self._lectura.set_fecha()

    def hemos_terminado(self) -> bool:
        return self._lectura.restante < 1


    def leer_datos(self) -> Lectura:
        if not self.hemos_terminado():
            # Determina si ha de simularse que los datos de origen han cambiado
            if self._lectura.total == 0:
                # Fuerza a que la primera vez siempre lea datos nuevos
                hay_datos_nuevos = True
            else:
                hay_datos_nuevos = random.choices(
                    population=[True, False],
                    weights=[self._ratio_valores_nuevos, 1 - self._ratio_valores_nuevos]
                )[0]

            # Si los datos han cambiado calacula los "delta" de cada dato para
            # calcular con ellos los nuevos datos que van a simular a los datos leídos
            if hay_datos_nuevos:
                delta_restante = random.choices(population=[0, 1], weights=[25, 75])[0]
                delta_aportaciones = random.randint(5, 20)
                delta_total = sum([random.randint(10, 100) for _ in range(delta_aportaciones)])
                lectura = Lectura(
                    titulo=self.titulo,
                    fecha=Scrapper._get_timestamp(),
                    restante=self._lectura.restante - delta_restante,
                    unidades="Dias",
                    aportaciones=self._lectura.aportaciones + delta_aportaciones,
                    objetivo=self._lectura.objetivo,
                    total=self._lectura.total + delta_total
                )
                self._lectura = lectura

                if self.hemos_terminado():
                    self._lectura.titulo = self.titulo + "(TERMINADO)"
                    self._lectura.restante = 0

            self._lectura.set_fecha()

        return self._lectura


if __name__ == "__main__":
    def run(scr: Scrapper) -> Lectura:
        return scr.leer_datos()
    ant = 0
    s = ScrapperRandom(titulo="Prueba de Random Scrapper", url="none")
    for i in range(30):
        datos = run(s)
        nuevos = "Datos nuevos -- " if datos.total != ant else "--------------- "
        print(f"{nuevos}  {i:02} -- {datos}")
        ant = datos.total

