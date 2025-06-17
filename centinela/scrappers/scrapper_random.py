import random

from centinela.datos_persistentes import Lectura
from scrappers.scrapper import Scrapper


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
                population=[10, 15, 20],
                weights=[10, 6, 3]
            )[0],
            unidades="Días",
            aportaciones=0,
            objetivo=random.randint(10, 100) * 1000,
            total=0
        )
        self._lectura.set_fecha()
        self._primera_vez = True

    def leer_datos(self) -> Lectura:
        if self._primera_vez:
            self._primera_vez = False
            return self._lectura

        hay_datos_nuevos = random.choices(
            population=[True, False],
            weights=[self._ratio_valores_nuevos, 1 - self._ratio_valores_nuevos]
        )[0]
        if hay_datos_nuevos:
            delta_restante = random.choices(population=[0, 1], weights=[8, 2])[0]
            delta_aportaciones = random.randint(5, 20)
            delta_total = random.randint(10, 100) * delta_aportaciones
            lectura = Lectura(
                titulo=self.titulo,
                fecha=Scrapper._get_timestamp(),
                restante=self._lectura.restante - delta_restante,
                unidades="Días",
                aportaciones=self._lectura.aportaciones + delta_aportaciones,
                objetivo=self._lectura.objetivo,
                total=self._lectura.total + delta_total
            )
            self._lectura = lectura

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

