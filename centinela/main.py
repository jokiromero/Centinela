import asyncio
import threading

import config
import logging

from centinela.chatbots import ChatbotTelegram
from centinela.scrappers.scrapper import Scrapper
from centinela.scrappers.scrapper_random import ScrapperRandom
from centinela.system_tray import CentinelaSystemTray
from centinela.data_box import DataBoxVerkami

MENSAJE_FIJO = "Opciones disponibles:"
BANNER_TELEGRAM_ID = "AgACAgQAAxkBAAMTaElcxdIpY-3UdJnFwxc4V_e1KwEAArXFMRvJ5ElSVNaFlbLAShsBAAMCAAN5AAM2BA"

config.configurar_logging()
logger = logging.getLogger(__name__)


# ------------------- Main Scraping Loop -------------------
async def bucle_principal(scrap: Scrapper):
    while True:
        databox = scrap.leer_datos()
        await databox.mostrar_datos(con_voz=config.voz_activada)
        # actualizar_datos_persistentes
        intervalo = 60 * config.tupla_intervalo_activo[1]
        await asyncio.sleep(intervalo)


# noinspection DuplicatedCode
async def main():
    loop = asyncio.get_running_loop()

    # scrap=ScrapperVerkami(url=config.URL_ISPHANYA, titulo="Proyecto 'ISPHANYA'"),
    # scrap=ScrapperVerkami(url=config.URL_MORTADELO, titulo="Proyecto Mortadelo"),
    scrapper = ScrapperRandom(url="ninguna", titulo="Datos sintéticos")

    chatbot = ChatbotTelegram(token=config.TOKEN_TELEGRAM)
    data_box = DataBoxVerkami(nombre_fichero_excel=config.FICHERO_EXCEL_DATOS)

    centinela_tray = CentinelaSystemTray(
        app_nombre=config.APP_NOMBRE,
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
    task_scrapper = asyncio.create_task(bucle_principal(scrap=scrapper))

    # Espera a ambas tareas asíncronas juntas
    centinela_tray.registrar_tareas_async(task_bot=task_bot, task_scrap=task_scrapper)
    await asyncio.gather(task_bot, task_scrapper)



# ------------------- Entry Point -------------------
if __name__ == "__main__":
    msg = f"Centinela. Nivel de log: {logging.getLevelName(logger.getEffectiveLevel())}"
    logger.info(msg)
    print(msg)

    try:
        asyncio.run(main())
    except Exception as e:
        # traceback.print_exc(-1)
        raise
