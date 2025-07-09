import asyncio
import threading

import config
import logging

from centinela.chatbots import ChatbotTelegram
from centinela.scrappers.scrapper_random import ScrapperRandom
from centinela.system_tray import CentinelaSystemTray
from centinela.data_box import DataboxVerkami
from centinela.scrappers.scrapper import Scrapper
from centinela.scrappers.scrapper_random import ScrapperRandom
from centinela.scrappers.scrapper_verkami import ScrapperVerkami
from centinela.config import Param, get, DOTENV_PATH

MENSAJE_FIJO = "Opciones disponibles:"
BANNER_TELEGRAM_ID = "AgACAgQAAxkBAAMTaElcxdIpY-3UdJnFwxc4V_e1KwEAArXFMRvJ5ElSVNaFlbLAShsBAAMCAAN5AAM2BA"

config.configurar_logging()
logger = logging.getLogger(__name__)



async def main():
    # TO-DO: Revisar fichero setup.py y actualizar según la última refactorización.
    loop = asyncio.get_running_loop()

    scrapper = ScrapperVerkami(url=config.URL_SCRAPPING, titulo=config.URL_TITULO)

    chatbot = ChatbotTelegram(token=config.TOKEN_TELEGRAM)
    data_box = DataboxVerkami(nombre_fichero_excel=config.FICHERO_EXCEL_DATOS)

    centinela_tray = CentinelaSystemTray(
        app_nombre=get(Param.APP_NOMBRE, DOTENV_PATH),
        scrapper=scrapper,
        data_box=data_box,
        chatbot=chatbot,
        loop=loop
    )

    # Hilo para la bandeja del sistema
    tray_thread = threading.Thread(target=centinela_tray.iniciar,
                                   daemon=True)
    tray_thread.start()

    # Iniciar tareas asíncronas para el chatbot y el scrapping
    task_bot = asyncio.create_task(chatbot.iniciar())
    task_scrapper = asyncio.create_task(centinela_tray.bucle_scrapping())

    centinela_tray.registrar_tareas_async(task_bot=task_bot,
                                          task_scrap=task_scrapper)

    # Espera a ambas tareas asíncronas juntas
    await asyncio.gather(task_bot, task_scrapper)



# ------------------- Entry Point -------------------
if __name__ == "__main__":
    msg = (f"Centinela. Nivel de log: "
           f"{logging.getLevelName(logger.getEffectiveLevel())}")
    logger.info(msg)
    print(msg)

    try:
        asyncio.run(main())

    except Exception as e:
        # traceback.print_exc(-1)
        raise
