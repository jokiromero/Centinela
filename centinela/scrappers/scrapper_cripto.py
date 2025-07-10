# Sirve para poder usar "forward reference" que son declaraciones
# y usos de anotaciones sobre tipos o clases que se definen más
# adelante en el código (future)
from __future__ import annotations

import requests
import logging

import config
import tools

from bs4 import BeautifulSoup, ResultSet

from typing import Tuple
from centinela.scrappers.scrapper import Scrapper
from centinela.data_box import DataboxCripto

logger = logging.getLogger(__name__)


class ScrapperCripto(Scrapper):
    """
    Clase responsable de realizar las operaciones de scrapper desde
    una Web de cotizaciones de criptomonedas.
    Implementa la interfaz Scrapper que permite diversificar los tipos de
    Webs a leer en cada caso.
    En este caso concreto, se utiliza un servidor de datos CoinGecko que no permite
    realizar scrapping devolviendo un 403 en cada acceso a su página. Por este motivo
    se ha tenido que implementar esta clase accediendo a los datos mediante una
    API pública gratuita servida por el propio CoinGecko:
        "https://api.coingecko.com/api/v3/simple/price"

    La propiedad privada self._data_box mantiene una referencia a un objeto
    que implemente la clase base Databox (en este caso sería 'DataboxCripto._Datos')
    y que consiste en un dataclass con los campos específicos que se van a
    obtener en la operación de scrapping.
    """

    def __init__(self, url: str, titulo: str) -> None:
        super().__init__(url=url, titulo=titulo)

        # Valores iniciales - Primera lectura
        self._datos = DataboxCripto.new_datos(
            titulo=titulo,
            moneda="",
            importe=0.0,
            delta=0.0,
        )

    def hemos_terminado(self) -> bool:
        """
        Indica si se ha terminado el tiempo restante disponible para el proyecto de
        financiación de Verkami.

        :return: True si las operaciones de scrapping tienen un final y si
        este final ha sido alcanzado. En el caso concreto de Verkami, cuando se
        ha alcanzado el límite de tiempo para el proyecto de financiación
        """
        return False


        # """
        # Realiza la operación de Scrapping específica para el caso de
        # cotizaciones de criptomonedas
        #
        # :return: Un objeto DataoxBitcoin._Datos con los datos leídos
        # mediante scrapping
        # """

    def leer_datos(self) -> DataboxCripto._Datos | None:
        moneda = "bitcoin"
        params = {
            "ids": f"{moneda}",
            "vs_currencies": "eur",
            "include_24hr_change": "true"
        }

        resp = requests.get(url=self.url, params=params)
        data = resp.json()

        importe = data[moneda]['eur']
        delta = data[moneda]['eur_24h_change']

        self._datos = DataboxCripto.new_datos(
            titulo=self._titulo,
            moneda=moneda,
            importe=importe,
            delta=delta,
        )

        return self._datos



if __name__ == "__main__":
    # Pruebs del módulo
    print(config.URL_SCRAPPING)
    sc = ScrapperCripto(config.URL_SCRAPPING, config.URL_TITULO)
    data = sc.leer_datos()
    print(data)
