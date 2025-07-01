import asyncio
import threading
import logging
import winotify

import config
import tools

from PIL import ImageFile
from pystray import Icon, Menu, MenuItem

from centinela.chatbots import Chatbot
from centinela.data_box import DataBox

logger = logging.getLogger(__name__)


def _async_menu_wrapper(coroutine_func, loop: asyncio.AbstractEventLoop, *args, **kwargs):
    """
        Devuelve un callback síncrono para pystray que ejecuta una función async en el event loop dado.

        :param coroutine_func: Función asíncrona a ejecutar.
        :param loop: Instancia de asyncio. AbstractEventLoop.
        :param args: Argumentos posicionales para la función async.
        :param kwargs: Argumentos nombrados para la función async.
        :return: Función síncrona que puede usarse como callback de menú.
    """

    def callback(icon=None, item=None):
        asyncio.run_coroutine_threadsafe(
            coroutine_func(*args, **kwargs), loop
        )

    return callback



class CentinelaSystemTray:
    def __init__(
            self,
            app_nombre: str,
            data_box: DataBox,
            chatbot: Chatbot | None = None,
            loop: asyncio.AbstractEventLoop | None = None
    ):
        self._centinela_activo = True
        self._con_voz_activada = False

        self._data_box = data_box
        self._chatbot = chatbot
        self._loop = loop

        # self._centinela_system_tray = Icon(config.APP_NOMBRE, self._get_logo(), menu=self._get_menu())
        self._system_tray = Icon(app_nombre)
        self._system_tray.icon = self._get_logo()
        self._system_tray.menu = self._get_menu()
        self._system_tray.update_menu()

        self._task_bot = None
        self._task_scrap = None

    def registrar_tareas_async(self, task_bot, task_scrap):
        self._task_bot = task_bot
        self._task_scrap = task_scrap


    def iniciar(self):
        """
        Ejecuta el icono de sistema en un hilo separado para evitar bloqueo
        del event loop.
        """
        self._system_tray.run()

    def _get_logo(self) -> ImageFile:
        return (config.LOGO_ACTIVO
                if self._centinela_activo else config.LOGO_INACTIVO)

    def _get_menu(self) -> Menu:
        i = list(config.INTERVALOS.keys())
        submenu_intervalos = Menu(*[
            MenuItem(text=i[0], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=i[0]),
                     checked=lambda item: i[0] == config.tupla_intervalo_activo[0]),
            MenuItem(text=i[1], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=i[1]),
                     checked=lambda item: i[1] == config.tupla_intervalo_activo[0]),
            MenuItem(text=i[2], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=i[2]),
                     checked=lambda item: i[2] == config.tupla_intervalo_activo[0]),
            MenuItem(text=i[3], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=i[3]),
                     checked=lambda item: i[3] == config.tupla_intervalo_activo[0]),
            MenuItem(text=i[4], radio=True,
                     action=lambda icon: self.accion_fijar_intervalo(icon, texto_intervalo=i[4]),
                     checked=lambda item: i[4] == config.tupla_intervalo_activo[0]),
        ])
        submenu_notificar = Menu(*[
            MenuItem(text="Solo cambios de datos_nuevos", radio=True,
                     action=lambda icon: self.accion_fijar_notificaciones(
                         icon, valor=config.Notificaciones.SOLO_CAMBIOS),
                     checked=lambda item: config.tipo_notificaciones_activo == 0),
            MenuItem(text="Todos los intervalos", radio=True,
                     action=lambda icon: self.accion_fijar_notificaciones(
                         icon, valor=config.Notificaciones.TODOS_LOS_INTERVALOS),
                     checked=lambda item: config.tipo_notificaciones_activo == 1),
            MenuItem(text=f"Activar ChatBot de {self._chatbot.nombre}", radio=True,
                     action=_async_menu_wrapper(self.accion_activar_bot, self._loop),
                     checked=lambda item: self._chatbot.esta_activo),
            Menu.SEPARATOR,
            MenuItem(text="Con voz", action=self.accion_activar_voz,
                     checked=lambda item: self._con_voz_activada),
        ])
        menu = Menu(*[
            MenuItem(text="Activada", action=self.accion_activar_app,
                     checked=lambda item: self._centinela_activo),
            MenuItem(text="Intervalos", action=submenu_intervalos),
            MenuItem(text="Notificaciones", action=submenu_notificar),
            MenuItem(text="Mostrar última notificación",
                     action=_async_menu_wrapper(self.repetir_mostrar, self._loop)),
            Menu.SEPARATOR,
            MenuItem(text="Salir", action=self.accion_salir),
        ])
        return menu

    # async def bucle_principal_obsoleto(self):
    #     while True:
    #         print(f"bucle_principal    >> {self._centinela_activo=}")
    #         if self._centinela_activo:
    #             self._data.lectura_nueva = self._scrap.leer_datos()
    #             await self._data.mostrar_datos(con_voz=self._con_voz_activada)
    #             intervalo = 60 * config.tupla_intervalo_activo[1]
    #             print(f"{intervalo=}")
    #             # time.sleep(intervalo)
    #             await asyncio.sleep(intervalo)
    #             print(f"Fin del intervalo {time.thread_time()=}")

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

    # noinspection SpellCheckingInspection
    async def accion_activar_bot(self):
        print(f">>> {self._chatbot=}  --  {self._chatbot.esta_activo=}")
        if self._chatbot:
            if self._chatbot.esta_activo:
                await self._chatbot.desactivar()
                await self._chatbot.enviar_mensaje_a_suscriptores(
                    texto= "❌ Centinela <b>ha pausado</b> el envío de notificaciones a este Chatbot",
                    parse_mode="HTML"
                )
            else:
                await self._chatbot.activar()
                await self._chatbot.enviar_mensaje_a_suscriptores(
                    texto="✅ Centinela <b>ha actiado</b> el envío de notificaciones a este Chatbot",
                    parse_mode="HTML"
            )


    async def repetir_mostrar(self):
        await self._data_box.mostrar_datos(es_una_repeticion=True, con_voz=self._con_voz_activada)

    # noinspection SpellCheckingInspection
    async def accion_salir(self):
        # Cancelar tareas async
        if self._task_bot and not self._task_bot.done():
            self._task_bot.cancel()

        if self._task_scrap and not self._task_scrap.done():
            self._task_scrap.cancel()

        # Detener bot si tiene lógica de cierre
        if self._chatbot:
            await self._chatbot.parar()

        # Detener el icono de sistema
        self._system_tray.stop()

        # Detener el event loop tras un breve retraso para permitir cancelaciones
        def stop_loop():
            if self._loop and self._loop.is_running():
                self._loop.stop()

        threading.Timer(interval=1, function=stop_loop).start()
