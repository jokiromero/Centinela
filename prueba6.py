from centinela import config

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message


class BotTelegram:
    def __init__(self, token: str):
        self._bot = Bot(token)
        self._dp = Dispatcher()
        self._register_handlers()

    def _register_handlers(self):
        self._dp.message.register(
            self._handle_start, Command(commands=["start"]))
        self._dp.message.register(
            self._handle_help, Command(commands=["help"]))
        self._dp.message.register(
            self._handle_echo)  # Default handler

    async def _handle_start(self, message: Message):
        await message.answer("¡Hola! Has iniciado el bot.")

    async def _handle_help(self, message: Message):
        await message.answer("Este bot te puede ayudar con /start y /help.")

    async def _handle_echo(self, message: Message):
        await message.answer(f"Has dicho: {message.text}")

    async def iniciar(self):
        print("Bot iniciado (aiogram)")
        await self._dp.start_polling(self._bot)

    async def enviar_mensaje_usuario(self, chat_id: int, texto: str):
        await self._bot.send_message(chat_id, texto)

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
            await asyncio.sleep(10)

        # Si quisieras terminar:
        # await bot.detener()

    asyncio.run(main())
