import os
from pathlib import Path
import time
from os import PathLike
from threading import Thread, Lock

import pyglet
import winotify

import openpyxl
import openpyxl.utils
import pandas as pd
from gtts import gTTS
from openpyxl.styles import Alignment, Font, PatternFill

from centinela import config

bloqueo_hablar = Lock()


def mostrar_notificacion(
        titulo: str = "Atención...",
        msg: str = "Aplicación Centinela, ejecutándose en "
                   "segundo plano desde la bandeja del sistema...",
        sonido=winotify.audio.Reminder,
        msg_hablado: str = ""
):
    toast = winotify.Notification(
        app_id=config.APP_NOMBRE,
        title=titulo,
        msg=msg,
        duration="short",
        icon=config.ICONO_ACTIVO_FICH
    )
    toast.set_audio(sonido, loop=False)
    toast.show()

    if msg_hablado:
        hilo_hablar = Thread(target=hablar, kwargs={"msg": msg_hablado})
        hilo_hablar.start()
        print(f"Mensaje hablado: {msg_hablado}")


def hablar(msg: str):
    bloqueo_hablar.acquire()
    carpeta = os.path.join(Path(__file__).parent, "tmp")
    if not os.path.isdir(carpeta):
        os.mkdir(carpeta)

    fichero = os.path.join(carpeta, "hablar.mp3")
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


def exportar_excel(
        fich: str | PathLike,
        data: dict,
        index_excel: bool = False,
        mode: str = "w",
        ancho_columnas: dict = None
) -> None:
    """
        Facilita la exportanción a Excel de Pandas.DataFrames
            fich = Nombre completo del fichero Excel de salida
            data = Es un diccionario cuyas claves son los nombres de ls hojas
                      del Excel a crear y cuyos datos son objetos DataFrame que van
                      a exportarse
            index_excel = bool - Si es True el índice se exportará al Excel.
                      Por defecto es False
            fmode = 'W' para sobreescribir o "a" para añadir al fichero existente
                     pero sobreescribiendo las pestañas pre-existentes
            ancho_columnas = opcional, diccionario con los anchos deseados para las
                             las columnas sobre las que no se prefiera el ancho
                             automático (autofit)
        """
    if not isinstance(data, dict):
        msg = "Parámetro 'data' debe ser de tipo 'dict'..."
        # logger.error(msg)
        raise TypeError(msg)

    # Borrar el fichero si existe y si el modo no es "a"
    if os.path.exists(fich) and mode != "a":
        os.remove(fich)
    else:
        print(f"Escribiendo fichero de salida '{fich}'")

    with pd.ExcelWriter(
            fich, date_format="yyyy-mm-dd", mode=mode, engine="openpyxl",
            if_sheet_exists="replace" if mode == "a" else None
    ) as writer:
        def as_text(value):
            return "" if value is None else str(value)

        for hoja, df in data.items():
            if not isinstance(df, pd.DataFrame):
                msg = "Parámetro 'datos' debe ser de tipo 'pandas.DataFrame'..."
                raise TypeError(msg)

            df.to_excel(writer,
                        sheet_name=hoja,
                        header=True,
                        # engine="openpyxl",
                        index=index_excel,
                        merge_cells=False,
                        # encoding="utf-8",
                        freeze_panes=(1, 0)
                        )

            wb = writer.book
            ws = wb[hoja]
            fill_cabecera = PatternFill(
                fgColor="00858C", fill_type="solid",
                start_color="00858C", end_color="00858C"
            )
            font_cabecera = Font(name="Consolas", size=10, color="FFFFFF",
                                 bold=True)
            font_cuerpo = Font(name="Consolas", size=10, color="000000",
                               bold=False)
            alin_cabecera = Alignment(vertical="bottom")
            alin_cuerpo = Alignment(vertical="top")
            ult_col = len(df.columns) + 1 if index_excel else len(df.columns)
            for row in ws.iter_rows(min_row=1, min_col=1, max_row=len(df) + 1,
                                    max_col=ult_col):
                for cell in row:
                    if cell.row == 1:
                        cell.fill = fill_cabecera
                        cell.font = font_cabecera
                        cell.alignment = alin_cabecera
                    else:
                        cell.font = font_cuerpo
                        cell.alignment = alin_cuerpo

            for column_cells in ws.columns:
                if ancho_columnas and column_cells[0].value in ancho_columnas:
                    new_column_length = ancho_columnas[column_cells[0].value]
                else:
                    new_column_length = max(
                        len(as_text(cell.value)) for cell in column_cells)
                new_column_letter = (openpyxl.utils.get_column_letter(
                    column_cells[0].column))

                if new_column_length > 0:
                    ws.column_dimensions[
                        new_column_letter].width = new_column_length + 1

                # todo: alinear las columnas numéricas a la derecha
                #  column_cells[0].value ==> nombre de la columna
                #  tipo float ==> issubclass(float, type(column_cells[1].value)
                #  tipo int ==> issubclass(int, type(column_cells[1].value)
