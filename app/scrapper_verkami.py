from typing import Any

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def _formato1(datos: list) -> str:
    formato = ""
    formato += f"{datos[0][0]:18} = {datos[0][1]:8d}\n"
    formato += f"{datos[1][0]:18} = {datos[1][1]:8d}\n"
    formato += f"{datos[2][0]:18} = {datos[2][1]:11,.2f} €\n"
    formato += f"{datos[3][0]:18} = {datos[3][1]:11,.2f} €"
    return formato


def _formato2(datos: list) -> str:
    formato = ""
    formato += f"{datos[0][1]:4d} {datos[0][0]:11} // {datos[2][1]:10,.0f} € {datos[2][0]:6}\n"
    formato += f"{datos[1][1]:4d} {datos[1][0]:11} // {datos[3][1]:10,.0f} € {datos[3][0]:6}"
    return formato


class ScrapperVerkami:
    """
    Clase reponsable de realizar las operaciones de scrapper
    """
    def __init__(self):
        self._url = "https://www.verkami.com/projects/40960-isphanya"
        self._datos = dict()
        self._timestamp = None

    def actualizar_datos(self):
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
        etiq_campo1 = counter_unit[0].text.strip().split()[0].replace('í', 'i')
        etiq_campo2 = counter_unit[1].text.strip()
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

        self._datos = dict()
        self._datos[etiq_campo1] = valor_campo1
        self._datos[etiq_campo2] = valor_campo2
        self._datos["Inicio"] = importe_objetivo
        self._datos["Actual"] = importe_recaudado

    def get_salida_tabulada(self) -> str:
        datos = list(self._datos.items())
        # salida = _formato1(datos)
        salida = _formato2(datos)
        return salida

    @property
    def datos(self) -> dict[str, Any]:
        return self._datos

    @property
    def timestamp(self) -> str:
        return self._timestamp

