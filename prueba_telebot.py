
from centinela import config
import logging
import telebot

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BotTelegram:
    def __init__(self, token: str):
        self._bot = telebot.TeleBot(token)
        self._register_handlers()

    def _register_handlers(self):
        @self._bot.message_handler(commands=["start"])
        def _handle_start(message):
            self._handle_start(message)

        @self._bot.message_handler(commands=["on"])
        def _handle_on(message):
            self._handle_on(message)

        @self._bot.message_handler(commands=["off"])
        def _handle_off(message):
            self._handle_off(message)

        @self._bot.message_handler(commands=["help"])
        def _handle_help(message):
            self._handle_help(message)

        @self._bot.message_handler(func=lambda message: True)
        def _handle_echo(message):
            self._handle_echo(message)

    def _handle_start(self, message):
        self._bot.send_message(message.chat.id, "¡Hola! Has iniciado el bot.")

    def _handle_help(self, message):
        self._bot.send_message(message.chat.id, "Este bot te puede ayudar con /start y /help.")

    def _handle_echo(self, message):
        self._bot.send_message(message.chat.id, f"Has dicho: {message.text}")

    def _handle_on(self, message):
        self._bot.send_message(message.chat.id, "Comando /on pulsado")

    def _handle_off(self, message):
        self._bot.send_message(message.chat.id, "Comando /off pulsado")

    def iniciar(self):
        print("Bot iniciado (Telebot)")
        try:
            self._bot.polling()
        except Exception as e:
            logging.error(f"Error en 'polling': {e}")
            raise

    def enviar_mensaje_usuario(self, chat_id: int, texto: str):
        self._bot.send_message(chat_id, texto)

    def detener(self):
        # En Telebot, no hay un método específico para detener el bot
        # Puedes utilizar un flag para controlar el bucle de polling
        print("Bot detenido.")


if __name__ == '__main__':
    import threading

    def main():
        bot = BotTelegram(config.TOKEN_TELEGRAM)
        task_bot = threading.Thread(target=bot.iniciar)
        task_bot.start()

        # Simulamos lógica adicional
        while True:
            print("App principal ejecutando otras tareas...")
            import time
            time.sleep(10)

    try:
        main()
    except Exception as e:
        logging.error(f"Error en el bot: {e}")
        raise
