import asyncio
import dataclasses
import os
import winotify
import pandas as pd
import logging

from aiogram.enums import parse_mode, ParseMode

from centinela.data_box import DataBox, DataBoxVerkami

from typing import Type
from copy import copy
from dataclasses import dataclass, asdict, fields
from datetime import datetime
from num2words import num2words
from pandas.errors import DataError

from centinela import tools, config
from centinela.chatbots import Chatbot
from scrappers.scrapper import Scrapper
from scrappers.scrapper_random import ScrapperRandom

logger = logging.getLogger(__name__)


cols = {
    "ti": "Titulo",         # Un nombre diferenciador para mostrar
    "f": "Fecha",           # La fecha de la lectura
    "r": "Restante",        # Valor de tiempo que resta para terminar el Verkami
    "u": "Unidades",        # Unidades (dias, horas, ...) del tiempo que resta
    "a": "Aportaciones",    # Número de aportaciones
    "o": "Objetivo",        # Importe inicial objetivo
    "t": "Total"            # Total recaudado hasta el momento
}


# noinspection DuplicatedCode
@dataclass
class Lectura:
    # noinspection DuplicatedCode
    titulo: str = ""
    fecha: str = ""
    restante: int = 0
    unidades: str = ""
    aportaciones: int = 0
    objetivo: float = 0
    total: float = 0

    def get_fecha_datetime(self) -> datetime:
        ret = None
        if self.fecha:
            ret = datetime.strptime(self.fecha, "%Y-%m-%d %H:%M:%S")
        return ret

    def set_fecha(self) -> None:
        self.fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class Persistencia:
    def __init__(self, nombre_fichero: str | os.PathLike = "",
                 clase_dato: Type=DataBox.Datos,
                 bot: Chatbot | None=None):
        self._df = None  # DataFrame
        self._bot = bot
        if not dataclasses.is_dataclass(clase_dato):
            raise TypeError(f"Se esperaba una clase de tipo '{clase_dato}'(Dataclass) y se ha recibido "
                            f"una clase de tipo '{clase_dato.__name__}'")

        self._clase_dato = clase_dato
        self._lectura_anterior: DataBoxVerkami = DataBoxVerkami()
        self._lectura_nueva: DataBoxVerkami = DataBoxVerkami()
        if nombre_fichero:
            self._fichero = os.path.join(os.getcwd(), nombre_fichero)
        else:
            self._fichero = None

        if nombre_fichero:
            if os.path.isfile(self._fichero):
                self._df = pd.read_excel(self._fichero)

                self._validar_campos()

                if self._df.shape[0] == 0:
                    raise ValueError(f"Fichero vacío '{self._fichero}'")

                # Ordenar por fecha y tomar la última fila
                self._df.sort_values(by=cols["f"], inplace=True)
                fila = self._df.iloc[-1]

                d = self.lectura_nueva

                self._lectura_anterior.datos.titulo = fila[d.col("Ti")]
                self._lectura_anterior.datos.fecha = fila[d.col("F")]
                self._lectura_anterior.datos.restante = fila[d.col("R")]
                self._lectura_anterior.datos.unidades = fila[d.col("U")]
                self._lectura_anterior.datos.aportaciones = fila[d.col("A")]
                self._lectura_anterior.datos.objetivo = fila[d.col("O")]
                self._lectura_anterior.datos.total = fila[d.col("T")]


    def _validar_campos(self) -> bool:
        # Campos definidos en la dataclass
        # campos_lectura = {campo.name for campo in fields(self._clase_dato)}
        campos_lectura = {campo.name for campo in fields(self._lectura_nueva.datos)}

        # Columnas del DataFrame
        campos_df = set(
            [col.lower() for col in self._df.columns]
        )

        # Comparación
        print(f"{campos_lectura=}")
        print(f"{campos_df=}")

        campos_faltantes = campos_lectura - campos_df
        campos_sobrantes = campos_df - campos_lectura

        if campos_faltantes or campos_sobrantes:
            msg = "❌ Las columnas del Excel no coinciden con los campos que se esperaban...\n"
            if campos_faltantes:
                msg += f"🔺 Campos faltantes en el Excel: {sorted(campos_faltantes)}\n"
            if campos_sobrantes:
                msg += f"🔻 Columnas sobrantes en el Excel: {sorted(campos_sobrantes)}\n"
            raise DataError(msg)

        return True


    @property
    def datos_cambiados(self) -> bool:
        ret = False
        if (
                self.lectura_anterior.datos.titulo != self.lectura_nueva.datos.titulo
                or (self.lectura_anterior.datos.fecha == "" and self.lectura_nueva.datos.fecha != "")
                or self.lectura_anterior.datos.total != self.lectura_nueva.datos.total
        ):
            ret = True

        return ret

    @property
    def lectura_nueva(self) -> DataBoxVerkami:
        return self._lectura_nueva

    @lectura_nueva.setter
    def lectura_nueva(self, datos_nuevos: DataBoxVerkami):
        # Antes sustituir la lectura nueva, saca una copia como lectura anterior
        self._lectura_anterior = copy(self.lectura_nueva)
        # Y ahora puede ya machacarla con el nuevo valor recién leído
        self._lectura_nueva = copy(datos_nuevos)

        if not self._lectura_nueva.datos.fecha:
            self._lectura_nueva.datos.set_fecha()

        if self.datos_cambiados:
            d = asdict(datos_nuevos.datos)
            for clave in list(d.keys()):
                d[clave.capitalize()] = d.pop(clave)
            nueva_fila = pd.DataFrame(d, index=[0])
            self._df = pd.concat(objs=[self._df, nueva_fila], ignore_index=True)

            # Persistencia de datos en fichero Excel
            if self._fichero:
                df = self._df.copy()
                df.columns = [col.capitalize() for col in df.columns]
                tools.exportar_excel(fich=self._fichero, data={"Hoja1": df})

    @property
    def lectura_anterior(self) -> DataBoxVerkami | None:
        if self._lectura_anterior:
            return self._lectura_anterior
        else:
            return None


    async def mostrar_datos(self, es_una_repeticion=False, con_voz=False):
        if ((config.tipo_notificaciones_activo == config.Notificaciones.TODOS_LOS_INTERVALOS or
             (config.tipo_notificaciones_activo == config.Notificaciones.SOLO_CAMBIOS
              and self.datos_cambiados)) or es_una_repeticion):
            if self.datos_cambiados:
                titulo2 = "... ¡NUEVOS DATOS!"
                melodia = winotify.audio.LoopingAlarm4
            else:
                titulo2 = "... (sin cambios)"
                melodia = winotify.audio.LoopingCall2

            numero = num2words(number=self.lectura_nueva.datos.total, lang="es")
            msg_voz = f"Atención: se ha alcanzado un total de {numero} euros"
            print(f"mostrar_datos() >> {con_voz=}")
            msg = self.lectura_nueva.salida_formateada_str(formato="c")
            tools.mostrar_notificacion(
                titulo=self.lectura_nueva.datos.fecha + titulo2,
                msg=msg,
                msg_hablado=msg_voz if con_voz else "",
                sonido=melodia
            )
            print(f"{self._bot=}  --- {self._bot.esta_activo=}")
            if self._bot:
                if self._bot.esta_activo:
                    await self._bot.enviar_mensaje_a_suscriptores(
                        texto=msg, keyboard=True, parse_mode=ParseMode.HTML
                    )

        logger.info(f"Lectura de datos desde: {self.lectura_nueva.datos.titulo}  -->>  {self.lectura_nueva.datos.fecha}  ({config.tupla_intervalo_activo[0]})")
        # print(f"mostrar_datos() (formato 'a' ) -->> \n{self.get_salida_tabulada("a")}\n" + "-" * 104 + "\n")
        logger.info(f"mostrar_datos() (formato 'ab') -->> \n{self.lectura_nueva.salida_formateada_str("ab")}\n")



if __name__ == "__main__":
    # Pruebas del módulo
    config.configurar_logging()

    p = Persistencia(config.FICHERO_EXCEL_DATOS, DataBox.Datos)
    datos = p.lectura_nueva.datos
    datos.titulo = "Prueba de valores"
    datos.set_fecha()
    datos.objetivo = 32000
    datos.restante = 12
    datos.aportaciones = 133
    datos.total = 35100.00

    print(p.datos_cambiados)
    print(asyncio.run(p.mostrar_datos()))

    s = ScrapperRandom("Datos de prueba sintéticos")

    datos = p.lectura_nueva.datos
    print(p.datos_cambiados)
    print(asyncio.run(p.mostrar_datos()))

    # datos = p.lectura_nueva.datos
    # print(p.datos_cambiados)
    # print(asyncio.run(p.mostrar_datos()))
    #
    # datos = p.lectura_nueva.datos
    # print(p.datos_cambiados)
    # print(asyncio.run(p.mostrar_datos()))
    #
    # datos = p.lectura_nueva.datos
    # print(p.datos_cambiados)
    # print(asyncio.run(p.mostrar_datos()))
    #
    # datos = p.lectura_nueva.datos
    # print(p.datos_cambiados)
    # print(asyncio.run(p.mostrar_datos()))
    #
    # datos = p.lectura_nueva.datos
    # print(p.datos_cambiados)
    # print(asyncio.run(p.mostrar_datos()))

