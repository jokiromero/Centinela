# Sirve para poder usar "forward reference" que son declaraciones
# y usos de anotaciones sobre tipos o clases que se definen más
# adelante en el código (future)
from __future__ import annotations

import asyncio
import logging
from typing import Callable, Any, Coroutine

import winotify

from centinela import config
from centinela import tools

from PIL import ImageFile
from pystray import Icon, Menu, MenuItem

from centinela.chatbots import Chatbot
from centinela.data_box import Databox
from centinela.scrappers.scrapper import Scrapper

logger = logging.getLogger(__name__)



def _async_menu_wrapper(coroutine_func: Callable[..., Coroutine[Any, Any, Any]],
                        loop: asyncio.AbstractEventLoop) -> Callable[..., None]:
    """
    Crea un wrapper que permite ejecutar funciones asíncronas (async def)
    desde contextos síncronos como el menú de pystray, que corre en un hilo
    distinto al del event loop principal.

    Utiliza `asyncio.run_coroutine_threadsafe` para enviar la corutina al loop
    de manera segura desde otros hilos.

    Parámetros:
    ----------
    coroutine_func : Callable[..., Coroutine]
        Función async que se desea ejecutar (ej. `async def mi_func(...):`).
    loop : asyncio.AbstractEventLoop
        El event loop principal de asyncio donde deben ejecutarse las tareas.

    Devuelve:
    --------
    Callable[..., None]
        Una función síncrona que acepta cualquier argumento y lanza la corutina
        de forma segura en el loop.

    Ejemplo de uso:
    --------------
        MenuItem(
            text="Salir",
            action=lambda icon: _async_menu_wrapper(self.accion_salir, self._loop)(icon)
        )
    """
    def wrapper(*args: Any, **kwargs: Any) -> None:
        future = asyncio.run_coroutine_threadsafe(
            coroutine_func(*args, **kwargs), loop
        )

        # (Opcional) Descomentar el bloque try para capturar errores del futuro
        #            (no recomendado si bloquea el hilo)
        # try:
        #     result = future.result(timeout=3)  # cuidado: esto bloquea el hilo
        # except Exception as e:
        #     print(f"[ERROR en async task del menú]: {e}")
    return wrapper



class CentinelaSystemTray:
    def __init__(
            self,
            app_nombre: str,
            scrapper: Scrapper,
            data_box: Databox,
            chatbot: Chatbot | None = None,
            loop: asyncio.AbstractEventLoop | None = None
    ):
        self._centinela_activo = True
        self._con_voz_activada = False

        self._scrapper = scrapper
        self._data_box = data_box
        self._chatbot = chatbot
        self._loop = loop

        self._system_tray = Icon(app_nombre)
        self._system_tray.icon = self._get_logo()
        self._system_tray.menu = self._get_menu()
        self._system_tray.update_menu()

        self._task_bot = None
        self._task_scrap = None

        # Se asegura que el Scrapper asignado a CentinelaSystemTray tiene un objeto
        # datos compatible (de la misma clase) que el objeto datos que incluye el Databox
        # asociado
        if type(self._scrapper.datos) is not type(self._data_box.datos):
            raise TypeError(f"CentinelaSystemTray requiere que sus propiedades 'scrapper' "
                            f"y 'data_box' tengan ambas el mismo tipo de 'Datos' "
                            f"(sean objetos instancia de la misma clase 'Datos')\n"
                            f"{type(self._scrapper.datos)=}\n"
                            f"{type(self._data_box.datos)=}")

    async def bucle_scrapping(self):
        logger.info("Comienza el bucle principal 'bucle_scrapping()'...")
        try:
            while True:
                lectura = self._scrapper.leer_datos()
                self._data_box.actualizar_datos(lectura)
                await self._data_box.mostrar_datos(
                    con_voz=self._con_voz_activada, chatbot=self._chatbot
                )
                intervalo = 60 * config.tupla_intervalo_activo[1]
                await asyncio.sleep(intervalo)
                if self._scrapper.hemos_terminado():
                    break

        except asyncio.CancelledError:
            logger.info("Tarea 'bucle_scrapping()' cancelada...")

        except ValueError:
            logger.exception(f"Error leyendo la página '{self._scrapper.url}'")
            raise

        if self._scrapper.hemos_terminado():
            logger.info("Se han terminado los datos en el Website...")
            if self._chatbot.esta_activo:
                logger.debug("Enviando mensaje de fin a los suscriptores...")
                await self._chatbot.enviar_mensaje_a_suscriptores(
                    texto="Atención: este WebSite ya no está generando nuevos datos\n"
                          "Centinela dejará de enviar nuevos mensajes."
                )
                await self._chatbot.desactivar()

        await self.accion_salir(self._system_tray)

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
            MenuItem(text="Salir",
                     # action=_async_menu_wrapper(self.accion_salir, self._loop))
                     action=lambda icon: _async_menu_wrapper(self.accion_salir,
                                                             self._loop)(icon))
        ])
        return menu


    # noinspection SpellCheckingInspection
    def accion_fijar_intervalo(self, icon, texto_intervalo):
        # TO-DO: verificar que 'texto_intervalo' existe (es una clave) en
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
        fin_mensaje = "activados" if self._con_voz_activada else "desactivados"
        msg = "Mensajes de voz " + fin_mensaje
        tools.mostrar_notificacion(
            msg=msg,
            msg_hablado="Los mensajes de voz han sido " + fin_mensaje
        )
        self._system_tray.menu = self._get_menu()
        self._system_tray.update_menu()
        logger.info(msg)

    # noinspection SpellCheckingInspection
    def accion_activar_app(self):
        self._centinela_activo = not self._centinela_activo
        self._system_tray.icon = self._get_logo()
        self._system_tray.menu = self._get_menu()
        self._system_tray.update_menu()

    # noinspection SpellCheckingInspection
    async def accion_activar_bot(self):
        if self._chatbot:
            if self._chatbot.esta_activo:
                await self._chatbot.desactivar()
                await self._chatbot.enviar_mensaje_a_suscriptores(
                    texto= "❌ Centinela <b>ha pausado</b> el envío de notificaciones a este Chatbot",
                    linea_estado=True, parse_mode="HTML"
                )
            else:
                await self._chatbot.activar()
                await self._chatbot.enviar_mensaje_a_suscriptores(
                    texto="✅ Centinela <b>ha activado</b> el envío de notificaciones a este Chatbot",
                    linea_estado=True, parse_mode="HTML"
            )

    async def repetir_mostrar(self):
        await self._data_box.mostrar_datos(
            es_una_repeticion=True, con_voz=self._con_voz_activada, chatbot=self._chatbot
        )

    # noinspection SpellCheckingInspection
    async def accion_salir(self, icon):
        logger.info(">> Saliendo de la aplicación...")

        icon.stop()

        if self._chatbot:
            await self._chatbot.parar()

        # Cancelar tareas async
        def _cancelar_tareas():
            if self._task_bot and not self._task_bot.done():
                self._task_bot.cancel()

            if self._task_scrap and not self._task_scrap.done():
                self._task_scrap.cancel()

            # Detener el icono de sistema
            self._system_tray.stop()

        self._loop.call_soon_threadsafe(_cancelar_tareas)
