from copy import copy
from datetime import datetime

import requests
import logging

from bs4 import BeautifulSoup
from centinela.scrappers.scrapper import Scrapper
from data_box import DataBoxVerkami

logger = logging.getLogger(__name__)


class ScrapperVerkami(Scrapper):
    """
    Clase responsable de realizar las operaciones de scrapper desde
    la Web de Verkami.  Implementa la interfaz Scrapper que permite
    diversificar los tipos Webs a leer en cada caso.

    La propiedad privada self._data_box mantiene una referencia a un objeto
    que implemente la clase base DataBox (en este caso sería 'DataBoxVerkami') y
    que consiste en un dataclass con los campos específicos que se van a
    obtener en la operación de scrapping.
    """
    def __init__(self, url: str, titulo: str) -> None:
        super().__init__(url=url)
        # Valores iniciales - Primera lectura
        self._lectura_nueva = DataBoxVerkami()
        self._lectura_nueva.datos.titulo = titulo
        self._lectura_nueva.datos.restante = 0
        self._lectura_nueva.datos.unidades = ""
        self._lectura_nueva.datos.aportaciones = 0
        self._lectura_nueva.datos.objetivo = 0
        self._lectura_nueva.datos.total = 0
        # self._lectura_nueva.datos.set_fecha()

        self._lectura_anterior = copy(self._lectura_nueva)


    def hemos_terminado(self) -> bool:
        """
        Indica si se ha terminado el tiempo restante disponible para el proyecto de
        financiación de Verkami.

        :return: True si las operaciones de scrapping tienen un final y si
        este final ha sido alcanzado. En el caso concreto de Verkami, cuando se
        ha alcanzado el límite de tiempo para el proyecto de financiación
        """
        return self._lectura_nueva.datos.restante < 1


    def leer_datos(self) -> DataBoxVerkami | None:
        """
        Realiza la operación de Scrapping específica para el caso de
        un proyecto en el site de Verkami

        :return: Un objeto DataBoxVerkami con los datos leídos mediante scrapping
        """
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

        self._lectura_nueva.datos.restante = valor_campo1
        self._lectura_nueva.datos.unidades = etiq_campo1
        self._lectura_nueva.datos.aportaciones = valor_campo2
        self._lectura_nueva.datos.objetivo = importe_objetivo
        self._lectura_nueva.datos.total = importe_recaudado
        self._lectura_nueva.datos.set_fecha()

        return self._lectura_nueva

