import winsound
import os
import pyglet
import time

from gtts import gTTS
from threading import Thread, Lock
from winotify import Notification

import config

bloqueo_hablar = Lock()


def avisos(msg: str, titulo="", error=False, hablado=True, beep=True):
    notification_win(msg, titulo, error)
    if hablado:
        hilo_hablar = Thread(
            target=hablar,
            kwargs={"msg": msg, "error": error, "beep": beep}
        )
        hilo_hablar.start()


def notification_win(
        msg: str,
        titulo="",
        error=False,
        aplicacion=config.nombre_aplicacion
):
    # fichero = os.path.join(os.getcwd(), "images\\reus_peq.ico")
    fich_icono = os.path.join(os.getcwd(), "images\\eye.svg")
    if error:
        titulo = "Error: " + titulo

    cartelito = Notification(
        app_id=aplicacion,
        title=titulo,
        msg=msg,
        duration="long",
        icon=fich_icono
    )
    cartelito.show()


def hablar(msg: str, beep=True, error=False):
    bloqueo_hablar.acquire()
    if beep:
        _beep(error)

    fichero = os.path.join(os.getcwd(), r"tmp\hablar.mp3")

    tts = gTTS(text=msg, lang="es", tld="es", slow=False)
    if os.path.exists(fichero):
        os.remove(fichero)
    tts.save(fichero)

    sonido = pyglet.media.load(fichero, streaming=False)
    sonido.play()
    time.sleep(sonido.duration)  # prevenir que el delete mate el proceso
    if os.path.exists(fichero):
        os.remove(fichero)

    bloqueo_hablar.release()


def _beep(error=False):
    normal_sound = os.path.join(
        os.getcwd(), "images\\mixkit-melodic-bonus-collect-1938.wav"
    )
    error_sound = os.path.join(
        os.getcwd(), "images\\Error.wav"
    )
    fichero = error_sound if error else normal_sound
    winsound.PlaySound(fichero, winsound.SND_ASYNC)
    time.sleep(1.5)
