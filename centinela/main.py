import threading
import time

import winotify.audio
from PIL import ImageFile
from pystray import Icon, Menu, MenuItem

from centinela import tools, config
from scrappers.scrapper_verkami import ScrapperVerkami
from centinela.datos_persistentes import DatosPersistentes


def get_logo() -> ImageFile:
    return config.LOGO_ACTIVO if config.app_activada else config.LOGO_INACTIVO


def get_menu() -> Menu:
    intervalos = list(config.INTERVALOS.keys())
    submenu_intervalos = Menu(*[
        MenuItem(text=intervalos[0], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[0]),
                 checked=lambda item: intervalos[0] == config.tupla_intervalo_activo[0]),
        MenuItem(text=intervalos[1], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[1]),
                 checked=lambda item: intervalos[1] == config.tupla_intervalo_activo[0]),
        MenuItem(text=intervalos[2], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[2]),
                 checked=lambda item: intervalos[2] == config.tupla_intervalo_activo[0]),
        MenuItem(text=intervalos[3], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[3]),
                 checked=lambda item: intervalos[3] == config.tupla_intervalo_activo[0]),
        MenuItem(text=intervalos[4], radio=True,
                 action=lambda icon: accion_fijar_intervalo(icon, texto_intervalo=intervalos[4]),
                 checked=lambda item: intervalos[4] == config.tupla_intervalo_activo[0]),
    ])
    submenu_notificar = Menu(*[
        MenuItem(text="Sólo cambios de datos_nuevos", radio=True,
                 action=lambda icon: accion_fijar_notificaciones(icon, valor=config.Notificaciones.SOLO_CAMBIOS),
                 checked=lambda item: config.tipo_notificaciones_activo == 0),
        MenuItem(text="Todos los intervalos", radio=True,
                 action=lambda icon: accion_fijar_notificaciones(icon,
                                                                 valor=config.Notificaciones.TODOS_LOS_INTERVALOS),
                 checked=lambda item: config.tipo_notificaciones_activo == 1),
        Menu.SEPARATOR,
        MenuItem(text="Con voz", action=accion_activar_voz, checked=lambda item: config.voz_activada),
    ])
    menu = Menu(*[
        MenuItem(text="Activada", action=accion_activar_app, checked=lambda item: config.app_activada),
        MenuItem(text="Intervalos", action=submenu_intervalos),
        MenuItem(text="Notificaciones", action=submenu_notificar),
        MenuItem(text="Mostrar última notificación", action=repetir_mostrar),
        Menu.SEPARATOR,
        MenuItem(text="Salir", action=accion_salir),
    ])
    return menu


def bucle_principal():
    while True:
        if config.app_activada:
            data.lectura_nueva = scrap.leer_datos()
            data.mostrar_datos()
            intervalo = 60 * config.tupla_intervalo_activo[1]
            time.sleep(intervalo)


# noinspection SpellCheckingInspection
def accion_fijar_intervalo(icon, texto_intervalo):
    # todo: verificar que 'texto_intervalo' existe (es una clave) en
    #   el diccionario 'intervalos' para evitar que este función sea llamada
    #   con valores no existentes y devuelva un error no contrado
    config.tupla_intervalo_activo = (texto_intervalo, config.INTERVALOS[texto_intervalo])
    icon.menu = get_menu()
    icon.update_menu()

    msg = f"El nuevo intervalo se fijó a\n'{texto_intervalo}'"
    tools.mostrar_notificacion(msg=msg, sonido=winotify.audio.LoopingCall)


# noinspection SpellCheckingInspection
def accion_fijar_notificaciones(icon, valor=0):
    config.tipo_notificaciones_activo = valor if valor in (0, 1) else 0
    icon.menu = get_menu()
    icon.update_menu()


# noinspection SpellCheckingInspection
def accion_activar_voz(icon):
    config.voz_activada = not config.voz_activada
    print(f"Menú activar/desactivar voz >> {config.voz_activada=}")
    icon.icon = get_logo()
    icon.menu = get_menu()
    icon.update_menu()


# noinspection SpellCheckingInspection
def accion_activar_app(icon):
    config.app_activada = not config.app_activada
    icon.icon = get_logo()
    icon.menu = get_menu()
    icon.update_menu()


def repetir_mostrar(icon):
    data.mostrar_datos(es_una_repeticion=True)


# noinspection SpellCheckingInspection
def accion_salir(icon):
    icon.stop()


if __name__ == '__main__':
    centinela_system_tray = Icon(config.APP_NOMBRE, get_logo(), menu=get_menu())

    # scrap = ScrapperVerkami(url=config.URL_ISPHANYA)
    scrap = ScrapperVerkami(url=config.URL_MORTADELO, nombre="Proyecto Mortadelo")
    data = DatosPersistentes(config.FICHERO_EXCEL_DATOS)

    # Iniciamos la tarea de centinela en un hilo en segundo plano
    hilo_principal = threading.Thread(name="hilo_principal", target=bucle_principal)
    hilo_principal.daemon = True  # Para que el hilo se detenga cuando se cierre la aplicación
    hilo_principal.start()

    # Iniciamos la aplicación
    centinela_system_tray.run()
