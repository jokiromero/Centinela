# Sirve para poder usar "forward reference" que son declaraciones
# y usos de anotaciones sobre tipos o clases que se definen más
# adelante en el código (future)
from __future__ import annotations

from typing import Tuple

import requests
import logging

from copy import copy
from bs4 import BeautifulSoup, ResultSet

import tools
from centinela.scrappers.scrapper import Scrapper
from centinela.data_box import DataboxVerkami

logger = logging.getLogger(__name__)


class ScrapperVerkami(Scrapper):
    """
    Clase responsable de realizar las operaciones de scrapper desde
    la Web de Verkami.  Implementa la interfaz Scrapper que permite
    diversificar los tipos Webs a leer en cada caso.

    La propiedad privada self._data_box mantiene una referencia a un objeto
    que implemente la clase base Databox (en este caso sería 'DataboxVerkami._Datos')
    y que consiste en un dataclass con los campos específicos que se van a
    obtener en la operación de scrapping.
    """

    def __init__(self, url: str, titulo: str) -> None:
        super().__init__(url=url, titulo=titulo)

        # Valores iniciales - Primera lectura
        self._datos = DataboxVerkami.new_datos(
            titulo=titulo,
            resto_valor=0,
            resto_etiq="",
            aporta_valor=0,
            aporta_etiq="",
            objetivo=0,
            total=0
        )

    def hemos_terminado(self) -> bool:
        """
        Indica si se ha terminado el tiempo restante disponible para el proyecto de
        financiación de Verkami.

        :return: True si las operaciones de scrapping tienen un final y si
        este final ha sido alcanzado. En el caso concreto de Verkami, cuando se
        ha alcanzado el límite de tiempo para el proyecto de financiación
        """
        return (self._datos.resto_valor < 1
                and self._datos.resto_etiq.capitalize() == "Segundos")

    def leer_datos(self) -> DataboxVerkami._Datos | None:
        """
        Realiza la operación de Scrapping específica para el caso de
        un proyecto en el site de Verkami

        :return: Un objeto DataoxVerkami._Datos con los datos leídos
        mediante scrapping
        """
        logger.debug("Accediendo a la página Web de Verkami mediante Scrapping")
        # Enviar solicitud GET a la página
        response = requests.get(self._url)

        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            msg = f"Error {response.status_code} al obtener la página"
            raise ValueError(msg)

        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # --------------------------------------------------------------------------------------
        # Buscar los nodos "div" con clase "counter__unit"
        # son unidades o etiquetas de los campos de contadores del proyecto Verkami
        # --------------------------------------------------------------------------------------
        etiqueta_1 = etiqueta_2 = etiqueta_3 = ""
        counter_unit = soup.find_all('div', class_='counter__unit')
        etiquetas = self._get_3nodos(nodos=counter_unit)
        if etiquetas:
            etiqueta_1, etiqueta_2, etiqueta_3 = etiquetas
        else:
            msg = "No se encontraron los nodos con la clase 'counter__unit'"
            logger.warning(msg)

        # --------------------------------------------------------------------------------------
        # Buscar el nodo "div" con clase "feedback__inner"
        # --------------------------------------------------------------------------------------
        # counter_values = soup.find_all('div', class_='feedback__inner')
        # # Verificar si se encontraron los nodos
        # if len(counter_values) < 1:
        #     msg = "No se encontraron los nodos con la clase 'feedback__inner'"
        #     logger.warning(msg)
        #     feedback = ""
        # else:
        #     feedback = (counter_values[0].text.strip().replace('</', '')
        #                 .replace('>', '').replace('<', ''))
        #
        # print(f"\n>>{feedback=}\n")

        # --------------------------------------------------------------------------------------
        # Buscar los nodos "div" con clase "counter__value"
        # son los valores de los campos de contadores del proyecto Verkami
        # --------------------------------------------------------------------------------------
        valor_1 = valor_2 = valor_3 = ""
        counter_values = soup.find_all('div', class_='counter__value')
        valores = self._get_3nodos(nodos=counter_values)
        if valores:
            valor_1, valor_2, valor_3 = valores
        else:
            msg = "No se encontraron los nodos con la clase 'counter__value'"
            raise ValueError(msg)

        resto_valor = 0
        resto_etiq = ""
        if etiqueta_1.capitalize() in ["Dias", "Horas", "Minutos", "Segundos"]:
            resto_valor = int(valor_1)
            resto_etiq = etiqueta_1
        elif etiqueta_2.capitalize() in ["Dias", "Horas", "Minutos", "Segundos"]:
            resto_valor = int(valor_2)
            resto_etiq = etiqueta_2
        elif etiqueta_3.capitalize() in ["Dias", "Horas", "Minutos", "Segundos"]:
            resto_valor = int(valor_3)
            resto_etiq = etiqueta_3

        aporta_valor = 0
        aporta_etiq = ""
        if etiqueta_1.capitalize() == "Aportaciones":
            aporta_valor = int(valor_1)
            aporta_etiq = etiqueta_1
        elif etiqueta_2.capitalize() == "Aportaciones":
            aporta_valor = int(valor_2)
            aporta_etiq = etiqueta_2
        elif etiqueta_3.capitalize() == "Aportaciones":
            aporta_valor = int(valor_3)
            aporta_etiq = etiqueta_3

        total_str = ""
        obj_str = ""
        if etiqueta_1.strip().split()[0].capitalize() == "De":
            total_str = valor_1
            obj_str = etiqueta_1.strip().split()[1]
        elif etiqueta_2.strip().split()[0].capitalize() == "De":
            total_str = valor_2
            obj_str = etiqueta_2.strip().split()[1]
        elif etiqueta_3.strip().split()[0].capitalize() == "De":
            total_str = valor_3
            obj_str = etiqueta_3.strip().split()[1]

        total = float(total_str.strip().replace('€', '')
                      .replace('.', '')
                      .replace(',', '.'))
        objetivo = float(obj_str.strip().replace('€', '')
                         .replace('.', '')
                         .replace(',', '.'))

        self._datos = DataboxVerkami.new_datos(
            titulo=self._titulo,
            # feedback=feedback,
            resto_valor=resto_valor,
            resto_etiq=resto_etiq,
            aporta_valor=aporta_valor,
            aporta_etiq=aporta_etiq,
            objetivo=objetivo,
            total=total
        )

        return self._datos

    @staticmethod
    def _get_3nodos(nodos: ResultSet) -> Tuple[str, str, str] | None:
        """
        Obtiene 3 nodos con etiquetas de datos (unidades)
        o con valores de datos (valores)
        :param nodos:
        :return: tupla con 3 cadenas str
        """
        n1 = n2 = n3 = ""
        resultado = None

        if len(nodos) == 0:
            resultado = None

        elif len(nodos) > 0:
            n1 = nodos[0].text.strip().capitalize()
            if len(nodos) > 1:
                n2 = nodos[1].text.strip().capitalize()
                if len(nodos) > 2:
                    n3 = nodos[2].text.strip().capitalize()

            items = tools.reemplazar_en_lista(
                items=[n1, n2, n3],
                buscar=["\n", "<b>", "</b>", "<i>", "</i>"],
                sustituir=["", "", "", "", ""]
            )
            resultado = (items[0], items[1], items[2])

        return resultado
