# Sirve para poder usar "forward reference" que son declaraciones
# y usos de anotaciones sobre tipos o clases que se definen más
# adelante en el código (future)
from __future__ import annotations

from abc import ABC, abstractmethod

import logging
import asyncio

from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from centinela import config

logger = logging.getLogger(__name__)

MENSAJE_FIJO = "Opciones disponibles:"
BANNER_TELEGRAM_ID = "AgACAgQAAxkBAAMTaElcxdIpY-3UdJnFwxc4V_e1KwEAArXFMRvJ5ElSVNaFlbLAShsBAAMCAAN5AAM2BA"


# noinspection DuplicatedCode
class Chatbot(ABC):
    def __init__(self):
        self._nombre = "(sin nombre)"
        self._inicializado = False
        self._activo = False
        self._task = None

    @abstractmethod
    def _inicializar(self, *args, **kwargs) -> None:
        pass

    def _check_inicializado(self):
        if not self._inicializado:
            raise RuntimeError("La clase no ha sido inicializada correctamente...")

    @property
    def esta_activo(self) -> bool:
        if self._activo is None:
            self._activo = False
        return self._activo

    async def activar(self) -> None:
        if not self.esta_activo:
            self._activo = True

    async def desactivar(self) -> None:
        if self.esta_activo:
            self._activo = False

    @property
    def nombre(self) -> str:
        return self._nombre

    @abstractmethod
    async def enviar_mensaje_usuario(self, *args, **kwargs):
        pass

    @abstractmethod
    async def enviar_mensaje_a_suscriptores(self, *args, **kwargs):
        pass

    @abstractmethod
    async def iniciar(self):
        pass

    @abstractmethod
    async def parar(self):
        pass



class ChatbotTelegram(Chatbot):
    def _inicializar(self, token: str) -> None:
        self._token = token
        self._nombre = "TELEGRAM"
        self._inicializado = True

    def __init__(self, token: str) -> None:
        super().__init__()
        self._inicializar(token)
        self._bot = Bot(token)
        self._dp = Dispatcher()
        self._suscriptores = set()
        self._register_handlers()
        self._keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="👍 Suscribirte", callback_data="on"),
                InlineKeyboardButton(text="👎 Cancelar Suscripción", callback_data="off")
            ]]
        )
        self._activo = False
        self._task = None

    def _register_handlers(self):
        # self._dp.message.register(self._handle_start, Command(commands=["start"]))
        self._dp.message.register(self._handle_on, Command(commands=["on"]))
        self._dp.message.register(self._handle_off, Command(commands=["off"]))
        self._dp.message.register(self._handle_help, Command(commands=["help"]))
        self._dp.message.register(self._handle_echo)  # Default handler

        self._dp.callback_query.register(self._handle_callback)

    async def _handle_callback(self, query: types.CallbackQuery):
        """Callbacks para recoger la pulsación de los botones"""
        if query.data == "on":
            await self._handle_on(query.message)

        if query.data == "off":
            await self._handle_off(query.message)

    def _handle_start(self, message: Message):
        """Callbacks para recoger el comando /start"""
        print("_handle_start")
        # self._iniciar_bot()
        self.iniciar()

    async def _handle_help(self, message: Message):
        """Callbacks para recoger el comando /help"""
        msg = ("_\n<b><u>AYUDA PARA EL USO DEL CHAT BOT DE CENTINELA:</u></b>\n\n"
               "Pulsa cualquiera de los botones de opción que se muestran. \n"
               "También puedes usar los siguientes comandos en línea:\n"
               "   /on = suscribirte a las notificaciones\n"
               "  /off = borrar suscripción")
        await message.answer(msg, parse_mode=ParseMode.HTML)
        await self._handle_echo(message)

    async def _handle_on(self, message: Message):
        """Callbacks para recoger el comando /on"""

        # Añade al chat del usuario a la lista de suscriptores
        if message.chat.id not in self._suscriptores:
            self._suscriptores.add(message.chat.id)
            msg = (f"Muchas gracias, '{message.chat.full_name}' (id={message.chat.id}) "
                   f"por suscribirte a las notificaciones de Centinela.\n\n")
        else:
            msg = (f"{message.chat.full_name}, ya estabas suscrito a las notificaciones de Centinela. "
                   f"No hace falta que hagas nada adicional...\n\n")

        if self.esta_activo:
            msg += (f"A partir de ahora y mientras dure la sesión actual, recibirás "
                    f"actualizaciones directamente en este chatbot cada vez "
                    f"que éstas ocurran.\n\n 💚💚💚 ¡¡Gracias por usar Centinela!!")
        else:
            msg += (f"Lamentablemente, Centinela tiene desactivado en este momento "
                    f"el envío de notificaciones al chatbot. Cuando se activen de nuevo "
                    f"y si aún estás suscrito, volverás a recibir actualizaciones.")

        caption = self._get_estado(chat_id=message.chat.id,
                                   usuario=message.chat.full_name)
        await self._bot.send_photo(
            chat_id=message.chat.id,
            photo=BANNER_TELEGRAM_ID,
            caption=caption,
            reply_markup=None
        )
        await message.answer(msg, reply_markup=self._keyboard)

    # noinspection DuplicatedCode
    async def _handle_off(self, message: Message):
        """Callbacks para recoger el comando /off"""
        # Retira al chat de la suscripción
        msg = f"{message.chat.full_name} (id={message.chat.id})"
        if message.chat.id in self._suscriptores:
            self._suscriptores.remove(message.chat.id)
            msg = (f"{msg}\nHas cancelado tu suscripción a las notificaciones de Centinela.\n"
                   f"¡¡Vuelve cuando quieras...!!")
        else:
            msg = f"{msg}: no estás suscrito a las notificaciones de Centinela."

        caption = self._get_estado(chat_id=message.chat.id,
                                   usuario=message.chat.full_name)
        await self._bot.send_photo(
            chat_id=message.chat.id,
            photo=BANNER_TELEGRAM_ID,
            caption=caption,
            reply_markup=None
        )
        await message.answer(msg, reply_markup=self._keyboard)

    async def _handle_echo(self, message: Message):
        """
        Callbacks para reaccionar a cualquier mensaje de los usuarios y responder
        con una respuesta por defecto. Si se analiza y discrimina sobre el contenido
        de message.text, se pueden elaborar respuestas en función del mensaje recibido
        """
        await self._bot.delete_message(message.chat.id, message.message_id)
        mensaje = (self._get_estado(
            chat_id=message.chat.id, usuario=message.chat.full_name
        ) + "\n" + MENSAJE_FIJO)
        await self._bot.send_photo(
            chat_id=message.chat.id,
            photo=BANNER_TELEGRAM_ID,
            caption=mensaje,
            reply_markup=self._keyboard
        )

        # if message.photo:
        #     # Para obtener el id de una foto
        #     print(">>> Intento de enviar una foto")
        #     file_id = message.photo[-1].file_id
        #     await message.answer(f"El ID de la imagen es: {file_id}")

    async def iniciar(self):
        try:
            await self._dp.start_polling(self._bot, skip_updates=True)

        except asyncio.CancelledError:
            logger.info("Bot cancelado...")
            await self._dp.storage.close()
            await self._bot.session.close()
            raise

    async def parar(self):
        # En aiogram, puedes cerrar el bot manualmente si lo necesitas
        # await self._bot.session.close()
        if self.esta_activo:
            await self.enviar_mensaje_a_suscriptores(
                texto=f"ATENCIÓN: Este chatbot ha sido parado desde el Servidor de "
                      f"Centinela, que es desde donde se generan y se gestionan las "
                      f"notificaciones.\nPor este motivo, a partir de ahora dejarán "
                      f"de recibirse actualizaciones..."
            )
            await self.desactivar()

        await self._dp.stop_polling()
        await self._dp.storage.close()
        await self._bot.session.close()
        logger.info("Bot detenido.")

    async def enviar_mensaje_usuario(self, chat_id: int, texto: str, keyboard=False,
                                     linea_estado=False, parse_mode: str | None = None):
        if linea_estado:
            texto = f"{texto} \n\n" + self._get_estado(chat_id=chat_id, usuario="Usuario")
        await self._bot.send_message(chat_id=chat_id, text=texto, parse_mode=parse_mode,
                                     reply_markup=self._keyboard if keyboard else None)

    async def enviar_mensaje_a_suscriptores(self, texto: str, keyboard=False,
                                            linea_estado=False, parse_mode: str | None = None):
        for chat_id in self._suscriptores:
            await self.enviar_mensaje_usuario(chat_id=chat_id, texto=texto, parse_mode=parse_mode,
                                              linea_estado=linea_estado, keyboard=keyboard)

    def _get_estado(self, chat_id: int, usuario: str) -> str:
        estado_usuario = "🟢 SUSCRITO" if chat_id in self._suscriptores else "🔴 NO SUSCRITO"
        estado_bot = "✅ ACTIVADO" if self.esta_activo else "❌‍ DESACTIVADO"
        return f"{usuario}: {estado_usuario}  >>>  Bot: {estado_bot}"

    async def activar(self):
        if not self.esta_activo:
            await super().activar()
            logger.info(f"Chatbot activado")

    async def desactivar(self):
        if self.esta_activo:
            await super().desactivar()
            logger.info(f"Chatbot desactivado")


if __name__ == '__main__':
    # pruebas del módulo
    def main():
        bot = ChatbotTelegram(config.TOKEN_TELEGRAM)

        # Tarea 1: iniciar polling del bot
        bot.iniciar()

        valor = "99"
        # Tarea 2: lógica adicional (por ejemplo, enviar mensajes periódicos)
        while valor > "0":
            asyncio.sleep(10)
            msg = "🔔 Este es un mensaje automático para los suscriptores."
            bot.enviar_mensaje_a_suscriptores(msg, keyboard=True)
            valor = input("Valor...(0 = fin): ")

    try:
        main()

    except KeyboardInterrupt:
        print("Bot detenido por el usuario...")
