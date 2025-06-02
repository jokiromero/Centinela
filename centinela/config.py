import os
import pathlib

from enum import IntEnum
from PIL import Image


class Notificaciones(IntEnum):
    SOLO_CAMBIOS = 0
    TODOS_LOS_INTERVALOS = 1


APP_NOMBRE = "Centinela"
APP_VERSION = "1.0"
URL_ISPHANYA = "https://www.verkami.com/projects/40960-isphanya"
FICHERO_EXCEL_DATOS = "Datos_Centinela.xlsx"

# Valores iniciales por defecto
app_activada = True
voz_activada = False

# tupla_intervalo_activo = list(intervalos.items())[intervalos.__len__() - 1]
tupla_intervalo_activo = ("Cada 1 minutos", 1)
tipo_notificaciones_activo = Notificaciones.TODOS_LOS_INTERVALOS

# carpeta = os.getcwd()
carpeta = pathlib.Path(__file__).parent
# print(f"{carpeta=}")
LOGO_ACTIVO = Image.open(os.path.join(carpeta, r"images\ojo_abierto.png"))
LOGO_INACTIVO = Image.open(os.path.join(carpeta, r"images\ojo_cerrado.png"))
ICONO_ACTIVO_FICH = os.path.join(carpeta, r"images\ojo_abierto.ico")

INTERVALOS = {
    "Cada 5 minutos": 5,
    "Cada 15 minutos": 15,
    "Cada 20 minutos": 20,
    "Cada 45 minutos": 45,
    "Cada hora": 60,
}
