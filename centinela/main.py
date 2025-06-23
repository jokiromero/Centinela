import asyncio
import threading
import time
import logging

import winotify.audio
from PIL import ImageFile
from pystray import Icon, Menu, MenuItem

from centinela import tools, config
from chatbots.chatbot import Chatbot
from chatbots.chatbot_telegram import ChatbotTelegram
from scrappers.scrapper import Scrapper
from scrappers.scrapper_random import ScrapperRandom
from centinela.datos_persistentes import DatosPersistentes, Lectura

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Centinela:
    def __init__(
            self,
            app_nombre: str,
            data: DatosPersistentes | None = None,
            scrap: Scrapper | None = None,
            bot: Chatbot | None = None
    ):
        self._centinela_activo = True
        self._con_voz_activada = False

        self._data = data
        self._scrap = scrap
        self._bot = bot

        # self._centinela_system_tray = Icon(config.APP_NOMBRE, self._get_logo(), menu=self._get_menu())
        self._system_tray = Icon(app_nombre)
        self._system_tray.icon = self._get_logo()
        self._system_tray.menu = self._get_menu()
        self._system_tray.update_menu()
        self._task_centinela_tray = None
        self._task_bot = None

    def ejecutar(self):
        # Hilo para la bandeja del sistema
        self._task_centinela_tray = threading.Thread(target=self._iniciar_system_tray, daemon=True)
        self._task_centinela_tray.start()

        if self._bot:
            print("Se configuró un bot y se activó...")
            # Hilo para el chatbot
            self._task_bot = threading.Thread(target=self._bot.activar, daemon=True)
            self._task_bot.start()
        else:
            print("El bot no se informó y no puede activarse...")

        # Bucle principal
        asyncio.run(self.bucle_principal())


    def _iniciar_system_tray(self):
        """
        Ejecuta el icono de sistema en un hilo separado para evitar bloqueo del event loop.
        """
        self._system_tray.run()

    def _get_logo(self) -> ImageFile:
        return config.LOGO_ACTIVO if self._centinela_activo else config.LOGO_INACTIVO

    def _get_menu(self) -> Menu:
        intervalos = list(config.INTERVALOS.keys())
        submenu_intervalos = Menu(*[
            MenuItem(text=intervalos[0], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=intervalos[0]),
                     checked=lambda item: intervalos[0] == config.tupla_intervalo_activo[0]),
            MenuItem(text=intervalos[1], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=intervalos[1]),
                     checked=lambda item: intervalos[1] == config.tupla_intervalo_activo[0]),
            MenuItem(text=intervalos[2], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=intervalos[2]),
                     checked=lambda item: intervalos[2] == config.tupla_intervalo_activo[0]),
            MenuItem(text=intervalos[3], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=intervalos[3]),
                     checked=lambda item: intervalos[3] == config.tupla_intervalo_activo[0]),
            MenuItem(text=intervalos[4], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=intervalos[4]),
                     checked=lambda item: intervalos[4] == config.tupla_intervalo_activo[0]),
        ])
        submenu_notificar = Menu(*[
            MenuItem(text="Sólo cambios de datos_nuevos", radio=True,
                     action=lambda icon: self.accion_fijar_notificaciones(
                         icon, valor=config.Notificaciones.SOLO_CAMBIOS
                     ),
                     checked=lambda item: config.tipo_notificaciones_activo == 0),
            MenuItem(text="Todos los intervalos", radio=True,
                     action=lambda icon: self.accion_fijar_notificaciones(
                         icon, valor=config.Notificaciones.TODOS_LOS_INTERVALOS),
                     checked=lambda item: config.tipo_notificaciones_activo == 1),
            Menu.SEPARATOR,
            MenuItem(text="Con voz", action=self.accion_activar_voz,
                     checked=lambda item: self._con_voz_activada),
        ])
        menu = Menu(*[
            MenuItem(text="Activada", action=self.accion_activar_app,
                     checked=lambda item: self._centinela_activo),
            MenuItem(text="Intervalos", action=submenu_intervalos),
            MenuItem(text="Notificaciones", action=submenu_notificar),
            MenuItem(text="Mostrar última notificación", action=self.repetir_mostrar),
            Menu.SEPARATOR,
            MenuItem(text="Salir", action=self.accion_salir),
        ])
        return menu

    async def bucle_principal(self):
        while True:
            print(f"bucle_principal    >> {self._centinela_activo=}")
            if self._centinela_activo:
                self._data.lectura_nueva = self._scrap.leer_datos()
                await self._data.mostrar_datos(con_voz=self._con_voz_activada)
                intervalo = 60 * config.tupla_intervalo_activo[1]
                print(f"{intervalo=}")
                # time.sleep(intervalo)
                await asyncio.sleep(intervalo)
                print(f"Fin del intervalo {time.thread_time()=}")

    # noinspection SpellCheckingInspection
    def accion_fijar_intervalo(self, icon, texto_intervalo):
        # todo: verificar que 'texto_intervalo' existe (es una clave) en
        #   el diccionario 'intervalos' para evitar que este función sea llamada
        #   con valores no existentes y devuelva un error no contrado
        config.tupla_intervalo_activo = (texto_intervalo, config.INTERVALOS[texto_intervalo])
        icon.menu = self._get_menu()
        icon.update_menu()

        msg = f"El nuevo intervalo se fijó a\n'{texto_intervalo}'"
        tools.mostrar_notificacion(msg=msg, sonido=winotify.audio.LoopingCall)

    # noinspection SpellCheckingInspection
    def accion_fijar_notificaciones(self, icon, valor=0):
        config.tipo_notificaciones_activo = valor if valor in (0, 1) else 0
        icon.menu = self._get_menu()
        icon.update_menu()

    # noinspection SpellCheckingInspection
    def accion_activar_voz(self):
        self._con_voz_activada = not self._con_voz_activada
        print(f"Menú activar/desactivar voz >> {config.voz_activada=}")
        fin_mensaje = "activados" if self._con_voz_activada else "desactivados"
        tools.mostrar_notificacion(
            msg="Mensajes de voz " + fin_mensaje,
            msg_hablado="Los mensajes de voz han sido " + fin_mensaje
        )
        # self._system_tray.icon = self._get_logo()
        self._system_tray.menu = self._get_menu()
        self._system_tray.update_menu()

    # noinspection SpellCheckingInspection
    def accion_activar_app(self):
        self._centinela_activo = not self._centinela_activo
        self._system_tray.icon = self._get_logo()
        self._system_tray.menu = self._get_menu()
        self._system_tray.update_menu()

    def repetir_mostrar(self):
        self._data.mostrar_datos(es_una_repeticion=True, con_voz=self._con_voz_activada)

    # noinspection SpellCheckingInspection
    def accion_salir(self):
        self._system_tray.stop()


def main():
    # scrap=ScrapperVerkami(url=config.URL_ISPHANYA),
    # scrap=ScrapperVerkami(url=config.URL_MORTADELO, titulo="Proyecto Mortadelo"),
    scrap = ScrapperRandom(titulo="Datos sintéticos")
    bot = ChatbotTelegram(config.TOKEN_TELEGRAM)
    data = DatosPersistentes(config.FICHERO_EXCEL_DATOS, clase_dato=Lectura, bot=bot)

    centinela = Centinela(app_nombre=config.APP_NOMBRE, scrap=scrap, bot=bot, data=data)
    centinela.ejecutar()


if __name__ == '__main__':
    main()
