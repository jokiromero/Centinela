import asyncio
import threading
import traceback
import pystray

from dataclasses import dataclass
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from plyer import notification
from aiogram.filters import Command
import requests
from bs4 import BeautifulSoup

from PIL import Image, ImageDraw
from pystray import MenuItem as item
from aiogram import Bot, Dispatcher, types

import config

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
        # Simulación de scraping
        url = 'https://example.com/stocks'
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
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
class TelegramBot:
    def __init__(self, token: str):
        self._bot = Bot(token=token)
        self._dp = Dispatcher()
        self.active = True
        self._suscriptores = set()
        self._keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="👍 Suscribirte", callback_data="on"),
                InlineKeyboardButton(text="👎 Cancelar Suscripción", callback_data="off")
            ]]
        )
        self._register_handlers()

    def _register_handlers(self):
        self._dp.message.register(self._handle_start, Command(commands=["start"]))
        self._dp.message.register(self._handle_on, Command(commands=["on"]))
        self._dp.message.register(self._handle_off, Command(commands=["off"]))
        self._dp.message.register(self._handle_help, Command(commands=["help"]))
        self._dp.message.register(self._handle_echo)
        self._dp.callback_query.register(self._handle_callback)

    async def _handle_start(self, message: types.Message):
        if message.from_user.id not in self._suscriptores:
            self._suscriptores.add(message.from_user.id)
        await message.answer("Te has suscrito a las notificaciones de cotizaciones.")
        await self._handle_echo(message)

    async def _handle_callback(self, query: types.CallbackQuery):
        if query.data == "on":
            await self._handle_on(query.message)
        elif query.data == "off":
            await self._handle_off(query.message)

    async def _handle_help(self, message: types.Message):
        msg = (
            "AYUDA PARA EL USO DEL CHAT BOT DE CENTINELA:\n"
            "Pulsa cualquiera de los botones de opción que se muestran.\n\n"
            "También puedes usar los comandos en línea siguientes:\n"
            "/on = suscribirte\n"
            "/off = borrar suscripción"
        )
        await message.answer(msg)
        await self._handle_echo(message)

    async def _handle_on(self, message: types.Message):
        if message.chat.id not in self._suscriptores:
            self._suscriptores.add(message.chat.id)
            msg = (f"Gracias {message.chat.full_name} (id={message.chat.id}) por suscribirte.")
        else:
            msg = f"{message.chat.full_name}, ya estás suscrito."
        await message.answer(msg)

    async def _handle_off(self, message: types.Message):
        msg = f"{message.chat.full_name} (id={message.chat.id})"
        if message.chat.id in self._suscriptores:
            self._suscriptores.remove(message.chat.id)
            msg += "\nHas sido dado de baja de las notificaciones."
        else:
            msg += ": no estás suscrito."
        await message.answer(msg)

    async def _handle_echo(self, message: types.Message):
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
                    print(f">> Enviando mensaje a {user}: {text}")
                    await self._bot.send_message(user, text)
                except Exception:
                    print(f"Error al enviar mensaje a {user}:\n{traceback.format_exc()}")

    async def start(self):
        await self._dp.start_polling(self._bot, skip_updates=True)


# ------------------- System Tray -------------------
def create_image():
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, 64, 64), fill=(255, 255, 255))
    dc.text((10, 20), "S")
    return image


def tray_menu(icon, item_clicked):
    if str(item_clicked) == 'Salir':
        icon.stop()
    elif 'Intervalo' in str(item_clicked):
        value = int(str(item_clicked).split(' ')[-2])
        app_config.interval_minutes = value
    elif 'Telegram' in str(item_clicked):
        app_config.telegram_enabled = not app_config.telegram_enabled


def run_tray():
    icon = pystray.Icon("StockNotifier")
    icon.icon = create_image()
    icon.menu = pystray.Menu(
        item('Salir', tray_menu),
        item('Intervalo 1 min', tray_menu),
        item('Intervalo 30 min', tray_menu),
        item('Intervalo 60 min', tray_menu),
        item('Telegram ON/OFF', tray_menu)
    )
    icon.run()


# ------------------- Main Scraping Loop -------------------
async def main_loop(scraper: StockScraper, bot: TelegramBot):
    while True:
        try:
            new_data = scraper.fetch_data()
            print(f"{new_data=}")
            msg = f"Cotizaciones actualizadas: {new_data}"
            notify("Actualización Bolsa", msg)
            if app_config.telegram_enabled:
                await bot.broadcast(msg)
        except Exception:
            print(f"Error en el loop principal:\n{traceback.format_exc()}")

        await asyncio.sleep(app_config.interval_minutes * 60)


# ------------------- Main -------------------
async def main():
    scraper = StockScraper()
    telegram_bot = TelegramBot(token=config.TOKEN_TELEGRAM)

    # Hilo separado para la bandeja del sistema
    tray_thread = threading.Thread(target=run_tray, daemon=True)
    tray_thread.start()

    # Iniciar tareas asincrónicas del bot y del scraping
    bot_task = asyncio.create_task(telegram_bot.start())
    scraper_task = asyncio.create_task(main_loop(scraper, telegram_bot))

    await asyncio.gather(bot_task, scraper_task)


if __name__ == '__main__':
    asyncio.run(main())
