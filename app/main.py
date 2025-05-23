import threading
import time
import winotify.audio

from datetime import datetime
from PIL import ImageFile
from pystray import Icon, Menu, MenuItem
from winotify import Notification

from app import config
from app.scrapper_verkami import ScrapperVerkami

app_activada = True

# tupla_intervalo_activo = list(intervalos.items())[intervalos.__len__() - 1]
tupla_intervalo_activo = ("Cada 1 minutos", 1)
scrap = ScrapperVerkami()


def get_logo() -> ImageFile:
    return config.LOGO_ACTIVO if app_activada else config.LOGO_INACTIVO


def get_menu() -> Menu:
    global tupla_intervalo_activo
    # Método 1 (no funciona)
    # submenu = Menu(*[
    #     MenuItem(texto_intervalo, action=lambda icon: fijar_intervalo(icon, texto_intervalo),
    #              checked=lambda item: True if tupla_intervalo_activo == (texto_intervalo, minutos) else False)
    #     for texto_intervalo, minutos in intervalos.items()
    # ])
    # Método 2 (no funciona)
    # submenu = []
    # for texto_intervalo, minutos in intervalos.items():
    #     submenu.append(
    #         MenuItem(text=texto_intervalo, action=lambda icon: fijar_intervalo(icon, texto_intervalo),
    #                  checked=lambda item: tupla_intervalo_activo == (texto_intervalo, minutos))
    #     )
    # Método 3 (sí funciona)
    submenu = Menu(*[
        MenuItem(text=list(config.INTERVALOS.keys())[0],
                 action=lambda icon: fijar_intervalo(icon, texto_intervalo=list(config.INTERVALOS.keys())[0]),
                 checked=lambda item: list(config.INTERVALOS.keys())[0] == tupla_intervalo_activo[0]),
        MenuItem(text=list(config.INTERVALOS.keys())[1],
                 action=lambda icon: fijar_intervalo(icon, texto_intervalo=list(config.INTERVALOS.keys())[1]),
                 checked=lambda item: list(config.INTERVALOS.keys())[1] == tupla_intervalo_activo[0]),
        MenuItem(text=list(config.INTERVALOS.keys())[2],
                 action=lambda icon: fijar_intervalo(icon, texto_intervalo=list(config.INTERVALOS.keys())[2]),
                 checked=lambda item: list(config.INTERVALOS.keys())[2] == tupla_intervalo_activo[0]),
        MenuItem(text=list(config.INTERVALOS.keys())[3],
                 action=lambda icon: fijar_intervalo(icon, texto_intervalo=list(config.INTERVALOS.keys())[3]),
                 checked=lambda item: list(config.INTERVALOS.keys())[3] == tupla_intervalo_activo[0]),
        MenuItem(text=list(config.INTERVALOS.keys())[4],
                 action=lambda icon: fijar_intervalo(icon, texto_intervalo=list(config.INTERVALOS.keys())[4]),
                 checked=lambda item: list(config.INTERVALOS.keys())[4] == tupla_intervalo_activo[0]),
    ])
    menu = Menu(*[
        MenuItem(text="Activada", action=activar_desactivar, checked=lambda item: app_activada),
        MenuItem(text="Intervalos", action=submenu),
        MenuItem(text="Último valor", action=ultimo_valor),
        MenuItem(text="Salir", action=salir),
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
    global scrap
    intervalo = 60 * tupla_intervalo_activo[1]
    mostrar_notificacion(
        titulo=scrap.timestamp,
        msg=f"{scrap.get_salida_tabulada()}"
    )
    print(f"{scrap.timestamp} ... {tupla_intervalo_activo[0]=} ... {intervalo/60=}")
    print(f"{scrap.get_salida_tabulada()}\n-----------------------------------------------------------------\n")


def bucle_principal():
    global app_activada, tupla_intervalo_activo, scrap

    while True:
        if app_activada:
            intervalo = 60 * tupla_intervalo_activo[1]
            scrap.actualizar_datos()
            mostrar_datos()
            time.sleep(intervalo)


def fijar_intervalo(icon, texto_intervalo):
    # todo: verificar que 'texto_intervalo' existe (es una clave) en
    #   el diccionario 'intervalos' para evitar que este función sea llamada
    #   con valores no existentes y devuelva un error no contrado
    global tupla_intervalo_activo, hilo_principal
    tupla_intervalo_activo = (texto_intervalo, config.INTERVALOS[texto_intervalo])
    icon.menu = get_menu()
    icon.update_menu()

    msg = f"El nuevo intervalo se fijó a\n'{texto_intervalo}'"
    mostrar_notificacion(msg=msg, sonido=winotify.audio.LoopingCall)


def activar_desactivar(icon):
    global app_activada
    app_activada = not app_activada
    icon.icon = get_logo()
    icon.menu = get_menu()
    icon.update_menu()


def ultimo_valor(icon):
    mostrar_datos()


def salir(icon):
    icon.stop()


if __name__ == '__main__':
    centinela_system_tray = Icon(config.APP_NOMBRE, get_logo(), menu=get_menu())

    # Iniciamos la tarea de centinela en un hilo en segundo plano
    hilo_principal = threading.Thread(name="hilo_principal", target=bucle_principal)
    hilo_principal.daemon = True  # Para que el hilo se detenga cuando se cierre la aplicación
    hilo_principal.start()

    # Iniciamos la aplicación
    centinela_system_tray.run()
