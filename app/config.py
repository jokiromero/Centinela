import os
from PIL import Image, ImageFile

APP_NOMBRE = "Centinela"
APP_VERSION = "1.0"
URL_ISPHANYA = "https://www.verkami.com/projects/40960-isphanya"

carpeta = os.getcwd()
LOGO_ACTIVO = Image.open(os.path.join(carpeta, r"images\ojo_abierto.png"))
LOGO_INACTIVO = Image.open(os.path.join(carpeta, r"images\ojo_cerrado.png"))
ICONO_ACTIVO_FICH = os.path.join(carpeta, r"images\ojo_abierto.ico")

INTERVALOS = {
    "Cada 1 minutos": 1,
    "Cada 2 minutos": 2,
    "Cada 3 minutos": 3,
    "Cada 4 minutos": 4,
    "Cada 5 minutos": 5,
}