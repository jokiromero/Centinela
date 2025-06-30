import requests
import logging

from bs4 import BeautifulSoup
from centinela.persistencia import Lectura
from centinela.scrappers.scrapper import Scrapper


logger = logging.getLogger(__name__)


class ScrapperVerkami(Scrapper):
    """
    Clase responsable de realizar las operaciones de scrapper desde
    la Web de Verkami.  Implementa la interfaz Scrapper que permite
    diversificar los tipos Webs a leer en cada caso.
    """
    def __init__(self, titulo: str, url: str):
        super().__init__(titulo, url)

        # Valores iniciales - Primera lectura
        self._lectura = Lectura(
            titulo=self.titulo,
            restante=0,
            unidades="",
            aportaciones=0,
            objetivo=0,
            total=0
        )
        self._lectura.set_fecha()

    def hemos_terminado(self) -> bool:
        return self._lectura.restante < 1


    def leer_datos(self) -> Lectura | None:
        # Enviar solicitud GET a la página
        response = requests.get(self._url)

        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            print(f"Error {response.status_code} al obtener la página")
            return None

        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar los nodos "div" con clase "counter_value"
        counter_unit = soup.find_all('div', class_='counter__unit')

        # Verificar si se encontraron los nodos
        if len(counter_unit) < 3:
            print("No se encontraron los nodos con clase 'counter__unit'")
            return None

        # Extraer los valores y convertirlos a numéricos
        #   La etiqueta etiq_campo2 no se usa, pero se mantienen porque se podrían utilizar igual que se hace con
        #   etiq_campo1 para identificar el nombre de las unidades a que se reifere la variabla 'valor_campo1'
        etiq_campo1 = counter_unit[0].text.strip().split()[0].replace('í', 'i').capitalize()
        etiq_campo2 = counter_unit[1].text.strip().capitalize()
        importe_objetivo = float(counter_unit[2].text.strip().replace('€', '')
                                 .replace('.', '').replace(',', '.')
                                 .replace('De ', ''))

        # Buscar los nodos "div" con clase "counter_value"
        counter_values = soup.find_all('div', class_='counter__value')

        # Verificar si se encontraron los nodos
        if len(counter_values) < 3:
            print("No se encontraron los nodos con clase 'counter__value'")
            return None

        # Extraer los valores y convertirlos a numéricos
        valor_campo1 = int(counter_values[0].text.strip().split()[0])
        valor_campo2 = int(counter_values[1].text.strip().replace('.', ''))
        importe_recaudado = float(counter_values[2].text.strip().replace('€', '')
                                  .replace('.', '').replace(',', '.'))

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
