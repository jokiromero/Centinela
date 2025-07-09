import enum
import os
import pathlib
import logging
import dotenv
import keyring

from dotenv import load_dotenv
from enum import IntEnum
from PIL import Image
from colorama import Fore, Style
from pathlib import Path

# --------------------------------------------------------------------------
# Ruta del fichero de parámetros de entorno '.env'
# --------------------------------------------------------------------------
DOTENV_PATH = dotenv.find_dotenv()
# load_dotenv(dotenv_path=DOTENV_PATH, encoding="utf-8", verbose=False)


# --------------------------------------------------------------------------
# Obtener la carpeta RAÍZ de la aplicación
# --------------------------------------------------------------------------
CARPETA_RAIZ = pathlib.Path(__file__).parent.parent


class Notificaciones(IntEnum):
    SOLO_CAMBIOS = 0
    TODOS_LOS_INTERVALOS = 1


class Param(enum.Enum):
    """
    Clase enum para contener los nombres validos de parámetros
    de la aplicación
    """
    APP_NOMBRE = "APP_NOMBRE"
    APP_VERSION = "APP_VERSION"
    FICHERO_EXCEL_DATOS = "FICHERO_EXCEL_DATOS"
    FICHERO_EXCEL_TEST = "FICHERO_EXCEL_TEST"
    FICHERO_LOG = "FICHERO_LOG"
    NIVEL_LOG = "NIVEL_LOG"
    TOKEN_TELEGRAM = "TOKEN"
    URL_SCRAPPING = "URL_SCRAPPING"
    URL_TITULO = "URL_TITULO"

# --------------------------------------------------------------------------
# Función para acceder a los parámetros de entorno en fichero '.env'
# --------------------------------------------------------------------------
def get(param: Param, parametro_secreto=False,
        por_defecto: str | None = None) -> str | None:
    # TO-DO: implementar los valores por defecto
    if not isinstance(param, Param):
        raise TypeError("El argumento 'param' debe ser de tipo 'centinela.config.Param")

    valor_dotenv = dotenv.get_key(dotenv_path=DOTENV_PATH, key_to_get=param.value, encoding="utf-8")
    if parametro_secreto:
        valor_secreto = keyring.get_password(service_name="Centinela",
                                             username=param.value)
        if valor_secreto:
            return valor_secreto

        else:
            # Si no lo encuentra intenta usar el ya leído del fichero '.env'
            if valor_dotenv:
                # Si lo había encontrado en .env, lo almacena en el gestor
                # de credenciales de Windows y luego borra de .env
                keyring.set_password(service_name="Centinela",
                                     username=param.value, password=valor_dotenv)
                if keyring.get_password(service_name="Centinela",
                                        username=param.value):
                    dotenv.set_key(dotenv_path=DOTENV_PATH, key_to_set=param.value,
                                   value_to_set="")
                else:
                    logging.warning("No se pudo crear el nuevo registro en "
                                    "el Administrador de Credenciales de Windows")
                return valor_dotenv

            else:
                msg = (f"No se encuentra el valor de '{param.value}' ni en el gestor de "
                       f"credenciales de Windows ni en el fichero de configuración '{DOTENV_PATH}'")
                if por_defecto:
                    logging.warning(msg + f"\nSe tomará el valor por defecto: "
                                          f"'{por_defecto}'")
                    return por_defecto
                raise ValueError(msg)
    else:
        if valor_dotenv:
            return valor_dotenv

        else:
            msg = (f"No se encuentra el valor de '{param.value}' en el fichero "
                   f"de configuración '{DOTENV_PATH}'")
            if por_defecto:
                logging.warning(msg + f"\nSe tomará el valor por defecto: "
                                      f"'{por_defecto}'")
                return por_defecto
            raise ValueError(msg)


# --------------------------------------------------------------------------
# Definición de intervalos de Scrapping de datos
# --------------------------------------------------------------------------
INTERVALOS = {
    "Cada 5 minutos": 5,
    "Cada 15 minutos": 15,
    "Cada 20 minutos": 20,
    "Cada 45 minutos": 45,
    "Cada 20 segundos ": 0.33,
}

# --------------------------------------------------------------------------
# Parámetros DINÁMICOS y asignación de sus valores iniciales por defecto
# --------------------------------------------------------------------------
app_activada = True
voz_activada = False
tipo_notificaciones_activo = Notificaciones.TODOS_LOS_INTERVALOS
tupla_intervalo_activo = list(INTERVALOS.items())[INTERVALOS.__len__() - 1]  # último
# tupla_intervalo_activo = list(INTERVALOS.items())[0] # primero

# --------------------------------------------------------------------------
# Parámetros FIJOS de la aplicación
# --------------------------------------------------------------------------
LOGO_ACTIVO = Image.open(os.path.join(CARPETA_RAIZ, "centinela", "images", "ojo_abierto.png"))
LOGO_INACTIVO = Image.open(os.path.join(CARPETA_RAIZ, "centinela", "images", "ojo_cerrado.png"))
ICONO_ACTIVO_FICH = os.path.join(CARPETA_RAIZ, "centinela", "images", "ojo_abierto.ico")

# --------------------------------------------------------------------------
# Parámetros pre-cargados desde fichero de configuración de entorno: '.env'
# --------------------------------------------------------------------------
APP_NOMBRE = get(param=Param.APP_NOMBRE)
TOKEN_TELEGRAM = get(param=Param.TOKEN_TELEGRAM, parametro_secreto=True)
FICHERO_EXCEL_DATOS = os.path.join(CARPETA_RAIZ,
                                   get(param=Param.FICHERO_EXCEL_DATOS))
FICHERO_EXCEL_TEST = os.path.join(CARPETA_RAIZ, "Datos_Centinela__TEST__.xlsx")
FICHERO_LOG = os.path.join(CARPETA_RAIZ, "logs", get(param=Param.FICHERO_LOG))
_nivel_log_str = get(param=Param.NIVEL_LOG, por_defecto="INFO")
NIVEL_LOG = logging.getLevelNamesMapping().get(_nivel_log_str, logging.INFO)
URL_SCRAPPING = get(param=Param.URL_SCRAPPING)
URL_TITULO = get(param=Param.URL_TITULO, por_defecto="")

# --------------------------------------------------------------------------
# Otros valores no usados o usados de manera puntual o alternativa
# --------------------------------------------------------------------------
# Link al bot de Centinela en Telegram
CENTINELA_LINK = "https://t.me/Centinela_autobot"


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
