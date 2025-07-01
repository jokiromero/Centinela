import logging
import asyncio

from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from centinela import config
from centinela.chatbot_old.chatbot_old import Chatbot

logger = logging.getLogger(__name__)

MENSAJE_FIJO = "Opciones disponibles:"
BANNER_TELEGRAM_ID = "AgACAgQAAxkBAAMTaElcxdIpY-3UdJnFwxc4V_e1KwEAArXFMRvJ5ElSVNaFlbLAShsBAAMCAAN5AAM2BA"


class ChatbotTelegram(Chatbot):
    def _inicializar(self, token: str) -> None:
        self._token = token
        self._inicializado = True

    def __init__(self, token: str):
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

    async def _handle_start(self, message: Message):
        """Callbacks para recoger el comando /start"""
        print("_handle_start")
        # self._iniciar_bot()
        await self.activar()


    async def _handle_help(self, message: Message):
        """Callbacks para recoger el comando /help"""
        msg = ("AYUDA PARA EL USO DEL CHAT BOT DE CENTINELA:"
               "Pulsa cualquiera de los botones de opción que se muestran. \n"
               "También puedes usar los comandos en línea siguientes:\n"
               "   /on = suscribirte \n"
               "  /off = borrar suscripción")
        await message.answer(msg)
        await self._handle_echo(message)

    async def _handle_on(self, message: Message):
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

    async def _handle_off(self, message: Message):
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

    async def _handle_echo(self, message: Message):
        """Callbacks para reaccionar con una respuesta por defecto"""
        await self._bot.delete_message(message.chat.id, message.message_id)
        await self._bot.send_photo(
            chat_id=message.chat.id,
            photo=BANNER_TELEGRAM_ID,
            caption=MENSAJE_FIJO,
            reply_markup=self._keyboard
        )
        await self._bot.send_message(chat_id=message.chat.id,
                                     text=f"💚💚💚 ¡¡Gracias por usar Centinela!!",)

        # if message.photo:
        #     # Para obtener el id de una foto
        #     print(">>> Intento de enviar una foto")
        #     file_id = message.photo[-1].file_id
        #     await message.answer(f"El ID de la imagen es: {file_id}")

    def _iniciar_bot(self):
        try:
            print("Iniciando Bot (aiogram) --- start polling")
            self._dp.start_polling(self._bot, skip_updates=True)
            print("... después de start polling")

        except Exception as e:
            logging.error(f"Error en 'start_polling': {e}")
            raise
        # await self.enviar_mensaje_a_suscriptores("ATENCIÓN: El bot ha sido iniciado...")
        # await self.enviar_mensaje_a_suscriptores(
        #     "Seleccione una opción:", keyboard=True
        # )

    # def _activar_bot_loop_obsoleto(self):
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     self._task = loop.create_task(self._iniciar_bot())
    #     loop.run_forever()

    async def activar(self):
        print(f"activar() -- {self._activo=}")
        if not self._activo:
            # self._task = asyncio.create_task(self._iniciar_bot())
            await self._dp.start_polling(self._bot, skip_updates=True)
            self._activo = True

    def desactivar(self):
        # En aiogram, puedes cerrar el bot manualmente si lo necesitas
        # await self._bot.session.close()
        if self._activo:         # and self._task:
            # self._task.cancel()
            # try:
            #     await self._task
            # except asyncio.CancelledError:
            #     logging.info("Tarea cancelada correctamente...")
            self._bot.session.close()
            self._dp.stop_polling()
            self._activo = False
            print("Bot detenido.")

    async def enviar_mensaje_usuario(self, chat_id: int, texto: str):
        await self._bot.send_message(chat_id, texto)

    async def enviar_mensaje_a_suscriptores(self, texto: str, keyboard=False):
        print(f">>> {self._suscriptores=}")
        for chat_id in self._suscriptores:
            await self.enviar_mensaje_usuario(chat_id, texto)
            if keyboard:
                await self._bot.send_message(
                    chat_id=chat_id, text=MENSAJE_FIJO, reply_markup=self._keyboard
                )



if __name__ == '__main__':
    # async def main(bot: Chatbot):
    #     task_bot = asyncio.create_task(bot._iniciar_bot())
    #     # Simulamos lógica adicional
    #     while True:
    #         print("App principal ejecutando otras tareas...")
    #         msg = (f"ATENCIÓN: Está recibiendo este mensaje por estar suscrito a las "
    #                f"notificaciones de Centinela\n")
    #         await bot.enviar_mensaje_a_suscriptores(texto=msg, keyboard=True)
    #         await asyncio.sleep(10)
    #
    #     # Si quisieras terminar:
    #     # await bot.desactivar()
    # try:
    #     mibot = ChatbotTelegram(config.TOKEN_TELEGRAM)
    #     asyncio.run(main(mibot))
    #
    # except Exception as ex:
    #     logging.error(f"Error en el bot: {ex}")
    #     raise

    def main():
        bot = ChatbotTelegram(config.TOKEN_TELEGRAM)

        # Tarea 1: iniciar polling del bot
        bot.activar()

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

