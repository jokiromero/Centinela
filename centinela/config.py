import os
import pathlib
import logging
import dotenv
import keyring

from dotenv import load_dotenv
from enum import IntEnum
from PIL import Image
from colorama import init, Fore, Style
from pathlib import Path


class Notificaciones(IntEnum):
    SOLO_CAMBIOS = 0
    TODOS_LOS_INTERVALOS = 1

def _get_clave(key: str) -> str | None:
    # Recupera el valor desde el gestor de credenciales de Windows
    valor = keyring.get_password(service_name="Centinela", username=key)
    if not valor:
        # Si no lo encuentra intenta leerlo del fichero de entorno .env
        load_dotenv()
        path = dotenv.find_dotenv()
        valor = dotenv.get_key(dotenv_path=path, key_to_get=key)
        if not valor:
            raise ValueError(f"No se encuentra el valor de '{key}' ni en el gestor de credenciales de Windows "
                             "ni en el fichero de entorno '.env'")
        else:
            # Si lo encuentra, lo almacena en el gestor de credenciales de Windows y borra
            # el valor de la clave de .env
            keyring.set_password(service_name="Centinela", username=key, password=valor)
            if keyring.get_password(service_name="Centinela", username=key):
                dotenv.set_key(dotenv_path=path, key_to_set=key, value_to_set="")

    return valor


INTERVALOS = {
    "Cada 5 minutos": 5,
    "Cada 15 minutos": 15,
    "Cada 20 minutos": 20,
    "Cada 45 minutos": 45,
    "Cada minuto": 1,
}

APP_NOMBRE = "Centinela"
APP_VERSION = "2.0"
URL_ISPHANYA = "https://www.verkami.com/projects/40960-isphanya"
URL_MORTADELO = ("https://www.verkami.com/projects/40554-mortadelo-multiverso-el-"
                 "juego-de-cartas-que-salvara-el-universo-a-mamporro-limpio")
FICHERO_EXCEL_DATOS = "Datos_Centinela.xlsx"
FICHERO_LOG = r"logs\centinela.log"


# Valores iniciales por defecto
app_activada = True
voz_activada = False
tipo_notificaciones_activo = Notificaciones.TODOS_LOS_INTERVALOS
tupla_intervalo_activo = list(INTERVALOS.items())[INTERVALOS.__len__() - 1]
# tupla_intervalo_activo = list(INTERVALOS.items())[0]

# carpeta = os.getcwd()
carpeta = pathlib.Path(__file__).parent
# print(f"{carpeta=}")
LOGO_ACTIVO = Image.open(os.path.join(carpeta, r"images\ojo_abierto.png"))
LOGO_INACTIVO = Image.open(os.path.join(carpeta, r"images\ojo_cerrado.png"))
ICONO_ACTIVO_FICH = os.path.join(carpeta, r"images\ojo_abierto.ico")
TOKEN_TELEGRAM = _get_clave("token")
print(TOKEN_TELEGRAM)
CENTINELA_LINK = "https://t.me/Centinela_autobot"


NIVEL_LOG = logging.DEBUG

class FormatoColoreado(logging.Formatter):
    COLOR_MAP = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLOR_MAP.get(record.levelno, "")
        reset = Style.RESET_ALL
        original = super().format(record)
        return f"{color}{original}{reset}"

def configurar_logging():
    logger = logging.getLogger()
    logger.setLevel(NIVEL_LOG)

    # Crea carpeta de logs si no existe
    Path(FICHERO_LOG).parent.mkdir(parents=True, exist_ok=True)

    # -------- Handler para consola con color --------
    consola = logging.StreamHandler()
    consola.setLevel(NIVEL_LOG)
    consola.setFormatter(FormatoColoreado(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    ))

    # -------- Handler para archivo sin color --------
    archivo = logging.FileHandler(Path(FICHERO_LOG), mode='a', encoding='utf-8')
    archivo.setLevel(NIVEL_LOG)
    archivo.setFormatter(logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    # Limpia handlers previos
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(consola)
    logger.addHandler(archivo)


