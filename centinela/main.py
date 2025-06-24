import asyncio
import threading
import time
import logging

import winotify.audio
from PIL import ImageFile
from pystray import Icon, Menu, MenuItem

from centinela import tools, config
from chatbots.chatbot import Chatbot
from chatbots.chatbot_telegram import ChatbotTelegram
from scrappers.scrapper import Scrapper
from scrappers.scrapper_random import ScrapperRandom
from centinela.datos_persistentes import DatosPersistentes, Lectura
from centinela.system_tray import Centinela

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')



def main():
    # scrap=ScrapperVerkami(url=config.URL_ISPHANYA),
    # scrap=ScrapperVerkami(url=config.URL_MORTADELO, titulo="Proyecto Mortadelo"),
    scrap = ScrapperRandom(titulo="Datos sintéticos")
    bot = ChatbotTelegram(config.TOKEN_TELEGRAM)
    data = DatosPersistentes(config.FICHERO_EXCEL_DATOS, clase_dato=Lectura, bot=bot)

    centinela = Centinela(app_nombre=config.APP_NOMBRE, scrap=scrap, bot=bot, data=data)
    centinela.ejecutar()


if __name__ == '__main__':
    main()
