import threading
import time

import pystray
import winotify.audio
import pathlib
import os

from PIL import ImageFile
from pystray import Icon, Menu, MenuItem
from winotify import Notification
from num2words import num2words
from app import config
from app.tools import hablar
from app.scrapper_verkami import ScrapperVerkami
from app.datos_persistentes import DatosPersistentes

app_activada = True
voz_activada = True

# tupla_intervalo_activo = list(intervalos.items())[intervalos.__len__() - 1]
tupla_intervalo_activo = ("Cada 1 minutos", 1)
tipo_notificaciones_activo = config.Notificaciones.TODOS_LOS_INTERVALOS


def get_logo() -> ImageFile:
    return config.LOGO_ACTIVO if app_activada else config.LOGO_INACTIVO


def get_menu() -> Menu:
    global tupla_intervalo_activo
    intervalos = list(config.INTERVALOS.keys())
    submenu_intervalos = Menu(*[
        MenuItem(text=intervalos[0], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[0]),
                 checked=lambda item: intervalos[0] == tupla_intervalo_activo[0]),
        MenuItem(text=intervalos[1], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[1]),
                 checked=lambda item: intervalos[1] == tupla_intervalo_activo[0]),
        MenuItem(text=intervalos[2], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[2]),
                 checked=lambda item: intervalos[2] == tupla_intervalo_activo[0]),
        MenuItem(text=intervalos[3], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[3]),
                 checked=lambda item: intervalos[3] == tupla_intervalo_activo[0]),
        MenuItem(text=intervalos[4], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[4]),
                 checked=lambda item: intervalos[4] == tupla_intervalo_activo[0]),
    ])
    submenu_notificar = Menu(*[
        MenuItem(text="Sólo cambios de datos_nuevos", radio=True,
                 action=lambda icon: accion_fijar_notificaciones(icon, valor=config.Notificaciones.SOLO_CAMBIOS),
                 checked=lambda item: tipo_notificaciones_activo == 0),
        MenuItem(text="Todos los intervalos", radio=True,
                 action=lambda icon: accion_fijar_notificaciones(icon,
                                                                 valor=config.Notificaciones.TODOS_LOS_INTERVALOS),
                 checked=lambda item: tipo_notificaciones_activo == 1),
        Menu.SEPARATOR,
        MenuItem(text="Con voz", action=accion_activar_voz, checked=lambda item: voz_activada),
    ])
    menu = Menu(*[
        MenuItem(text="Activada", action=accion_activar_desactivar, checked=lambda item: app_activada),
        MenuItem(text="Intervalos", action=submenu_intervalos),
        MenuItem(text="Notificaciones", action=submenu_notificar),
        MenuItem(text="Último datos_nuevos", action=accion_ultimo_valor),
        Menu.SEPARATOR,
        MenuItem(text="Salir", action=accion_salir),
    ])
    return menu


def mostrar_notificacion(
        titulo: str = "Atención...",
        msg: str = "Aplicación Centinela, ejecutándose en "
                   "segundo plano desde la bandeja del sistema...",
        sonido=winotify.audio.Reminder
):
    toast = Notification(
        app_id=config.APP_NOMBRE,
        title=titulo,
        msg=msg,
        duration="short",
        icon=config.ICONO_ACTIVO_FICH
    )
    toast.set_audio(sonido, loop=False)
    toast.show()


def mostrar_datos():
    intervalo = 60 * tupla_intervalo_activo[1]
    if (tipo_notificaciones_activo == config.Notificaciones.TODOS_LOS_INTERVALOS or
            (data.datos_cambiados and tipo_notificaciones_activo == config.Notificaciones.SOLO_CAMBIOS)):
        if data.datos_cambiados:
            titulo2 = "... ¡NUEVOS DATOS!"
            melodia = winotify.audio.LoopingAlarm4
        else:
            titulo2 = "... (sin cambios)"
            melodia = winotify.audio.LoopingCall2

        mostrar_notificacion(
            titulo=scrap.datos_web.fecha + titulo2,
            msg=f"{data.get_salida_tabulada(2)}",
            sonido=melodia
        )
        if voz_activada:
            numero = num2words(number=data.lectura_nueva.total, lang="es")
            msg = f"Atención: se ha alcanzado un total de {numero} euros"
            hilo_hablar = threading.Thread(
                target=hablar,
                kwargs={"msg": msg, "error": False, "beep": False}
            )
            hilo_hablar.start()

    print(f"{data.lectura_nueva.fecha} ... {tupla_intervalo_activo[0]=}")
    print(f"{data.get_salida_tabulada(0)}\n-----------------------------------------------------------------\n")


def bucle_principal():
    global app_activada, tupla_intervalo_activo

    while True:
        if app_activada:
            intervalo = 60 * tupla_intervalo_activo[1]
            data.lectura_nueva = scrap.leer_datos()
            mostrar_datos()
            time.sleep(intervalo)


def accion_fijar_intervalo(icon, texto_intervalo):
    # todo: verificar que 'texto_intervalo' existe (es una clave) en
    #   el diccionario 'intervalos' para evitar que este función sea llamada
    #   con valores no existentes y devuelva un error no contrado
    global tupla_intervalo_activo, hilo_principal
    tupla_intervalo_activo = (texto_intervalo, config.INTERVALOS[texto_intervalo])
    icon.menu = get_menu()
    icon.update_menu()

    msg = f"El nuevo intervalo se fijó a\n'{texto_intervalo}'"
    mostrar_notificacion(msg=msg, sonido=winotify.audio.LoopingCall)


def accion_fijar_notificaciones(icon, valor=0):
    global tipo_notificaciones_activo
    tipo_notificaciones_activo = valor if valor in (0, 1) else 0
    icon.menu = get_menu()
    icon.update_menu()


def accion_activar_voz(icon):
    global voz_activada
    voz_activada = not voz_activada
    icon.icon = get_logo()
    icon.menu = get_menu()
    icon.update_menu()


def accion_activar_desactivar(icon):
    global app_activada
    app_activada = not app_activada
    icon.icon = get_logo()
    icon.menu = get_menu()
    icon.update_menu()


def accion_ultimo_valor(icon):
    mostrar_datos()


def accion_salir(icon):
    icon.stop()


if __name__ == '__main__':
    centinela_system_tray = Icon(config.APP_NOMBRE, get_logo(), menu=get_menu())

    scrap = ScrapperVerkami()
    data = DatosPersistentes(config.FICHERO_EXCEL_DATOS)

    # Iniciamos la tarea de centinela en un hilo en segundo plano
    hilo_principal = threading.Thread(name="hilo_principal", target=bucle_principal)
    hilo_principal.daemon = True  # Para que el hilo se detenga cuando se cierre la aplicación
    hilo_principal.start()

    # Iniciamos la aplicación
    centinela_system_tray.run()
