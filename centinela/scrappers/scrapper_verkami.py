import requests

from bs4 import BeautifulSoup
from PIL.Image import Image

from centinela.datos_persistentes import Lectura
from scrappers.scrapper import Scrapper


class ScrapperVerkami(Scrapper):
    """
    Clase responsable de realizar las operaciones de scrapper desde
    la Web de Verkami.  Implementa la interfaz Scrapper que permite
    diversificar los tipos Webs a leer en cada caso.
    """
    def __init__(self, url: str, nombre: str = "",
                 imagen: Image | None = None):
        super().__init__(url, nombre, imagen)

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

        datos_web = Lectura(
            fecha=Scrapper._get_timestamp(),
            restante_valor=valor_campo1,
            restante_unidades=etiq_campo1,
            aportaciones=valor_campo2,
            objetivo=importe_objetivo,
            total=importe_recaudado,
        )

        return datos_web
