import asyncio
import threading
import time
from abc import ABC
from dataclasses import dataclass

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from plyer import notification
from aiogram.filters import Command
import requests
from bs4 import BeautifulSoup
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem
from aiogram import Bot, Dispatcher, types

import config
from chatbots.chatbot import Chatbot
from chatbots.chatbot_telegram import ChatbotTelegram
from datos_persistentes import DatosPersistentes, Lectura
from scrappers.scrapper import Scrapper
from scrappers.scrapper_random import ScrapperRandom


MENSAJE_FIJO = "Opciones disponibles:"
BANNER_TELEGRAM_ID = "AgACAgQAAxkBAAMTaElcxdIpY-3UdJnFwxc4V_e1KwEAArXFMRvJ5ElSVNaFlbLAShsBAAMCAAN5AAM2BA"


# ------------------- Config -------------------
@dataclass
class AppConfig:
    interval_minutes: int = 1
    telegram_enabled: bool = True


app_config = AppConfig()


# ------------------- Scraper -------------------
class StockScraper:
    def __init__(self):
        self.last_data = {}

    def fetch_data(self) -> dict:
        # Simulación de scraping (usar URL real y parsing correcto)
        url = 'https://example.com/stocks'
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        # Simulación de extracción
        data = {'AAPL': '180.00', 'GOOGL': '2800.00'}
        return data

    def has_changed(self, new_data: dict) -> bool:
        if new_data != self.last_data:
            self.last_data = new_data
            return True
        return False


# ------------------- Notifier -------------------
def notify(title: str, message: str):
    notification.notify(
        title=title,
        message=message,
        timeout=5
    )


# ------------------- Telegram Bot -------------------
class TelegramBot(Chatbot, ABC):
    def __init__(self, token: str):
        super().__init__()
        self._bot = Bot(token=token)
        self._dp = Dispatcher()
        self.active = True
        self._suscriptores = set()
        self._register_handlers()
        self._keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="👍 Suscribirte", callback_data="on"),
                InlineKeyboardButton(text="👎 Cancelar Suscripción", callback_data="off")
            ]]
        )

    def _register_handlers(self):
        self._dp.message.register(self.start, Command(commands=["start"]))
        self._dp.message.register(self._handle_on, Command(commands=["on"]))
        self._dp.message.register(self._handle_off, Command(commands=["off"]))
        self._dp.message.register(self._handle_help, Command(commands=["help"]))
        self._dp.message.register(self._handle_echo)  # Default handler
        self._dp.callback_query.register(self._handle_callback)

    def start(self, msg: types.Message):
        if msg.from_user.id not in self._suscriptores:
            self._suscriptores.add(msg.from_user.id)
        msg.reply("Te has suscrito a las notificaciones de cotizaciones.")

    async def _handle_callback(self, query: types.CallbackQuery):
        """Callbacks para recoger la pulsación de los botones"""
        if query.data == "on":
            await self._handle_on(query.message)

        if query.data == "off":
            await self._handle_off(query.message)

    async def _handle_start(self, message: types.Message):
        """Callbacks para recoger el comando /start"""
        print("_handle_start")
        # self._iniciar_bot()
        # await self.activar()

    def _handle_help(self, message: types.Message):
        """Callbacks para recoger el comando /help"""
        msg = ("AYUDA PARA EL USO DEL CHAT BOT DE CENTINELA:"
               "Pulsa cualquiera de los botones de opción que se muestran. \n"
               "También puedes usar los comandos en línea siguientes:\n"
               "   /on = suscribirte \n"
               "  /off = borrar suscripción")
        message.answer(msg)
        self._handle_echo(message)

    async def _handle_on(self, message: types.Message):
        """Callbacks para recoger el comando /on"""
        # Añade al chat del usuario a la lista de suscriptores
        if message.chat.id not in self._suscriptores:
            self._suscriptores.add(message.chat.id)
            msg = (f"Muchas gracias, '{message.chat.full_name}' (id={message.chat.id}) "
                   f"por suscribirte a las notificaciones de Centinela.\n\n"
                   f"A partir de ahora recibirás actualizaciones directamente en este "
                   f"chat cada vez que éstas ocurran.\n\n"
                   f"💚💚💚 ¡¡Gracias por usar Centinela!! ")
        else:
            msg = f"{message.chat.full_name}, ya estás suscrito a las notificaciones de Centinela."
        await message.answer(msg)

    async def _handle_off(self, message: types.Message):
        """Callbacks para recoger el comando /off"""
        # Retira al chat de la suscripción
        msg = f"{message.chat.full_name} (id={message.chat.id})"
        if message.chat.id in self._suscriptores:
            self._suscriptores.remove(message.chat.id)
            msg = (f"{msg}\n has sido dado de baja de las notificaciones de Centinela.\n"
                   f"¡¡Vuelve cuando quieras...!!")
        else:
            msg = f"{msg}: no estás suscrito a las notificaciones de Centinela."
        await message.answer(msg)

    async def _handle_echo(self, message: types.Message):
        """Callbacks para reaccionar con una respuesta por defecto"""
        await self._bot.delete_message(message.chat.id, message.message_id)
        await self._bot.send_photo(
            chat_id=message.chat.id,
            photo=BANNER_TELEGRAM_ID,
            caption=MENSAJE_FIJO,
            reply_markup=self._keyboard
        )

    async def broadcast(self, text: str):
        if self.active:
            for user in self._suscriptores:
                try:
                    await self._bot.send_message(user, text)
                except Exception as e:
                    print(f"Error al enviar a {user}: {e}")

    def run(self):
        asyncio.run(self._dp.start_polling(self._bot, skip_updates=True))


# ------------------- System Tray -------------------
def create_image():
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, 64, 64), fill=(255, 255, 255))
    dc.text((10, 20), "S")
    return image


def tray_menu(icon, item):
    if str(item) == 'Salir':
        icon.stop()
        asyncio.get_event_loop().stop()
    elif 'Intervalo' in str(item):
        value = int(str(item).split(' ')[-1])
        app_config.interval_minutes = value
    elif 'Telegram' in str(item):
        app_config.telegram_enabled = not app_config.telegram_enabled


def run_tray():
    icon = pystray.Icon(config.APP_NOMBRE)
    icon.icon = create_image()
    icon.menu = pystray.Menu(
        MenuItem('Salir', tray_menu),
        MenuItem('Intervalo 1 min', tray_menu),
        MenuItem('Intervalo 30 min', tray_menu),
        MenuItem('Intervalo 60 min', tray_menu),
        MenuItem('Telegram ON/OFF', tray_menu)
    )
    icon.run()


# ------------------- Main Scraping Loop -------------------
async def bucle_principal(
        scrap: Scrapper,
        data: DatosPersistentes
):
    while True:
        # new_data = scrap.fetch_data()
        # print(f"{new_data=}")
        # if scrapper.has_changed(new_data):
        #     msg = f"Cotizaciones actualizadas: {new_data}"
        #     notify("Actualización Bolsa", msg)
        #     if app_config.telegram_enabled:
        #         await bot.broadcast(msg)
        # # await asyncio.sleep(app_config.interval_minutes * 60)
        # time.sleep(app_config.interval_minutes * 60)

        data.lectura_nueva = scrap.leer_datos()
        await data.mostrar_datos(con_voz=config.voz_activada)
        intervalo = 60 * config.tupla_intervalo_activo[1]
        print(f"{intervalo=}")
        time.sleep(intervalo)
        # await asyncio.sleep(intervalo)
        print(f"Fin del intervalo...")


# ------------------- Entry Point -------------------
if __name__ == "__main__":
    # scrap=ScrapperVerkami(url=config.URL_ISPHANYA),
    # scrap=ScrapperVerkami(url=config.URL_MORTADELO, titulo="Proyecto Mortadelo"),
    scrapper = ScrapperRandom(titulo="Datos sintéticos")
    chatbot = ChatbotTelegram(token=config.TOKEN_TELEGRAM)

    # Hilo para la bandeja del sistema
    tray_thread = threading.Thread(target=run_tray, daemon=True)
    tray_thread.start()

    # Hilo para el bot de Telegram
    bot_thread = threading.Thread(target=chatbot.activar, daemon=True)
    bot_thread.start()

    datos_persistentes = DatosPersistentes(config.FICHERO_EXCEL_DATOS,
                                           clase_dato=Lectura, bot=chatbot)

    # Bucle principal
    asyncio.run(bucle_principal(scrap=scrapper, data=datos_persistentes))
