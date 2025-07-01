import asyncio
import threading
import config
import logging

from centinela.chatbots import ChatbotTelegram
from scrappers.scrapper import Scrapper
from scrappers.scrapper_random import ScrapperRandom
from system_tray import CentinelaSystemTray

MENSAJE_FIJO = "Opciones disponibles:"
BANNER_TELEGRAM_ID = "AgACAgQAAxkBAAMTaElcxdIpY-3UdJnFwxc4V_e1KwEAArXFMRvJ5ElSVNaFlbLAShsBAAMCAAN5AAM2BA"

config.configurar_logging()
logger = logging.getLogger(__name__)


# ------------------- Main Scraping Loop -------------------
async def bucle_principal(
        scrap: Scrapper,
        data: Persistencia
):
    while True:
        data.lectura_nueva = scrap.leer_datos()
        await data.mostrar_datos(con_voz=config.voz_activada)
        intervalo = 60 * config.tupla_intervalo_activo[1]
        # time.sleep(intervalo)
        await asyncio.sleep(intervalo)
        print(f"Fin del intervalo...")


async def main():
    loop = asyncio.get_running_loop()

    # scrap=ScrapperVerkami(url=config.URL_ISPHANYA, titulo="Proyecto 'ISPHANYA'"),
    # scrap=ScrapperVerkami(url=config.URL_MORTADELO, titulo="Proyecto Mortadelo"),
    scrapper = ScrapperRandom(titulo="Datos sintéticos")
    chatbot = ChatbotTelegram(token=config.TOKEN_TELEGRAM)

    centinela_tray = CentinelaSystemTray(
        app_nombre=config.APP_NOMBRE,
        data_box=datos_persistentes,
        scrap=scrapper,
        chatbot=chatbot,
        loop=loop
    )

    # Hilo para la bandeja del sistema
    tray_thread = threading.Thread(
        target=centinela_tray.iniciar, daemon=True
    )
    tray_thread.start()

    # Iniciar tareas asíncronas para el chatbot y el scrapping
    task_bot = asyncio.create_task(
        chatbot.iniciar()
    )
    task_scrapper = asyncio.create_task(
        bucle_principal(scrap=scrapper, data=datos_persistentes)
    )

    centinela_tray.registrar_tareas_async(
        task_bot=task_bot, task_scrap=task_scrapper
    )

    # Espera a ambas tareas asíncronas juntas
    await asyncio.gather(task_bot, task_scrapper)


# ------------------- Entry Point -------------------
if __name__ == "__main__":
    msg = f"Centinela. Nivel de log: {logging.getLevelName(logger.getEffectiveLevel())}"
    logger.info(msg)
    print(msg)

    try:
        asyncio.run(main())
    except Exception as e:
        print(e.args[0])
