from collections import namedtuple

from centinela import config

import logging

from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

MENSAJE_FIJO = "Opciones disponibles:"
BANNER_TELEGRAM_ID = "AgACAgQAAxkBAAMTaElcxdIpY-3UdJnFwxc4V_e1KwEAArXFMRvJ5ElSVNaFlbLAShsBAAMCAAN5AAM2BA"

class BotTelegram:
    def __init__(self, token: str):
        self._bot = Bot(token)
        self._dp = Dispatcher()
        self._suscriptores = {}

        self._register_handlers()

        self._keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="👍 Suscribirte", callback_data="on"),
                InlineKeyboardButton(text="👎 Cancelar Suscripción", callback_data="off")
            ]]
        )

    def _register_handlers(self):
        # self._dp.message.register(self._handle_start, Command(commands=["start"]))
        self._dp.message.register(self._handle_on, Command(commands=["on"]))
        self._dp.message.register(self._handle_off, Command(commands=["off"]))
        self._dp.message.register(self._handle_help, Command(commands=["help"]))
        self._dp.message.register(self._handle_echo)  # Default handler

        self._dp.callback_query.register(self._handle_callback)

    async def _handle_callback(self, query: types.CallbackQuery):
        if query.data == "on":
            await self._handle_on(query.message)

        if query.data == "off":
            await self._handle_off(query.message)

    async def _handle_start(self, message: Message):
        await self.iniciar()

    async def _handle_help(self, message: Message):
        msg = ("AYUDA PARA EL USO DEL CHAT BOT DE CENTINELA:"
               "Pulsa cualquiera de los botones de opción que se muestran. \n"
               "También puedes usar los comandos en línea siguientes:\n"
               "   /on = suscribirte \n"
               "  /off = borrar suscripción")
        await message.answer(msg)
        await self._handle_echo(message)

    async def _handle_on(self, message: Message):
        # Añade al chat del usuario a la lista de suscriptores
        if message.chat.id not in list(self._suscriptores):
            self._suscriptores[message.chat.id] = message.chat.full_name
            msg = (f"Muchas gracias, '{message.chat.full_name}' (id={message.chat.id}) "
                   f"por suscribirte a las notificaciones de Centinela.\n\n"
                   f"A partir de ahora recibirás actualizaciones directamente en este "
                   f"chat cada vez que éstas ocurran.\n\n"
                   f"💚💚💚 ¡¡Gracias por usar Centinela!! ")
        else:
            nombre = self._suscriptores[message.chat.id]
            msg = f"{message.chat.full_name}, ya estás suscrito a las notificaciones de Centinela."
        await message.answer(msg)

    async def _handle_off(self, message: Message):
        # Retira al chat de la suscripción
        msg = f"{message.chat.full_name} (id={message.chat.id})"
        if message.chat.id in list(self._suscriptores):
            del self._suscriptores[message.chat.id]
            msg = (f"{msg}\n has sido dado de baja de las notificaciones de Centinela.\n"
                   f"¡¡Vuelve cuando quieras...!!")
        else:
            msg = f"{msg}: no estás suscrito a las notificaciones de Centinela."
        await message.answer(msg)

    async def _handle_echo(self, message: Message):
        await self._bot.delete_message(message.chat.id, message.message_id)
        # await message.answer(text="mensaje...", reply_markup=self._keyboard)
        await self._bot.send_photo(
            chat_id=message.chat.id,
            photo=BANNER_TELEGRAM_ID,
            caption=MENSAJE_FIJO,
            reply_markup=self._keyboard
        )

        # if message.photo:
        #     # Para obtener el id de una foto
        #     print(">>> Intento de enviar una foto")
        #     file_id = message.photo[-1].file_id
        #     await message.answer(f"El ID de la imagen es: {file_id}")

    async def iniciar(self):
        print("Bot iniciado (aiogram)")
        try:
            await self._dp.start_polling(self._bot)
        except Exception as e:
            logging.error(f"Error en 'start_polling': {e}")
            raise
        await self.enviar_mensaje_a_todos("ATENCIÓN: El bot ha sido iniciado...")
        await self.enviar_mensaje_a_todos("Seleccione una opción:", keyboard=True)


    async def enviar_mensaje_usuario(self, chat_id: int, texto: str):
        await self._bot.send_message(chat_id, texto)

    async def enviar_mensaje_a_todos(self, texto: str, keyboard=False):
        print(f">>> {self._suscriptores=}")
        for chat_id in list(self._suscriptores):
            await self.enviar_mensaje_usuario(chat_id, texto)
            if keyboard:
                await self._dp.message.reply(text=MENSAJE_FIJO, reply_markup=self._keyboard)

    async def detener(self):
        # En aiogram, puedes cerrar el bot manualmente si lo necesitas
        await self._bot.session.close()
        print("Bot detenido.")


if __name__ == '__main__':
    import asyncio

    async def main():
        bot = BotTelegram(config.TOKEN_TELEGRAM)
        task_bot = asyncio.create_task(bot.iniciar())

        # Simulamos lógica adicional
        while True:
            print("App principal ejecutando otras tareas...")
            await bot.enviar_mensaje_a_todos("Este mensaje se envía a todos...")
            await asyncio.sleep(10)

        # Si quisieras terminar:
        # await bot.detener()
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Error en el bot: {e}")
        raise
