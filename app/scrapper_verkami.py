from typing import Any

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from app.datos_persistentes import Lectura


class ScrapperVerkami:
    """
    Clase reponsable de realizar las operaciones de scrapper
    """

    def __init__(self):
        self._url = "https://www.verkami.com/projects/40960-isphanya"
        self._datos_web = Lectura()
        self._timestamp = None

    def leer_datos(self):
        # Enviar solicitud GET a la página
        response = requests.get(self._url)
        self._timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
        importe_recaudado = float(counter_values[2].text.strip().replace('€', '').replace('.', '').replace(',', '.'))

        self._datos_web = Lectura(
            dias=valor_campo1,
            aportaciones=valor_campo2,
            objetivo=importe_objetivo,
            total=importe_recaudado
        )

        return self.datos_web

    @property
    def datos_web(self) -> Lectura:
        return self._datos_web

