import asyncio
import logging
import os
from copy import copy

import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Literal
from dataclasses import asdict

import winotify
from aiogram.enums import ParseMode
from num2words import num2words

import config
import tools
from chatbots import Chatbot, ChatbotTelegram

logger = logging.getLogger(__name__)


class DataBox(ABC):
    """
    Clase base que contiene los datos y formatos de visualización
    de los campos que se extraen de Web Sites mediante Scrapping
    """

    @dataclass
    class _Datos:
        """Dataclass para los campos y sus definiciones"""
        pass

    @abstractmethod
    def __init__(self):
        self._datos: DataBox._Datos = self._Datos()
        self._datos_anteriores: DataBox._Datos = self._Datos()

    @property
    def datos(self) -> _Datos:
        return self._datos

    @datos.setter
    def datos(self, datos_nuevos: _Datos) -> None:
        self._datos_anteriores = copy(self._datos)
        self._datos = copy(datos_nuevos)

    @abstractmethod
    def salida_formateada_str(self, *args) -> str:
        pass

    @property
    @abstractmethod
    def datos_cambiados(self) -> bool:
        """
        Devuelve si los datos nuevos son diferentes a los datos anteriores
        """
        pass

    @abstractmethod
    async def mostrar_datos(self, *args, **kwargs) -> None:
        """
        Controla la visualización de los datos en diferentes formas (notificaciones Windows),
        chatbot, etc.
        """
        pass

    @abstractmethod
    def persistir_datos(self) -> None:
        """
        Hace persistentes los datos de alguna manera.
        Las subclases definirán si es en Base de Datos, fichero, etc...
        """
        pass


# noinspection DuplicatedCode
class DataBoxVerkami(DataBox):
    """
    Clase que representa el conjunto de datos leídos del site de Verkami junto a sus métodos y formatos
    de visualización y persistencia
    """
    # noinspection DuplicatedCode
    @dataclass
    class _Datos:
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

    def __init__(self, nombre_fichero_excel: str | os.PathLike | None = None):
        super().__init__()
        self._nombre_fichero = nombre_fichero_excel
        self._df = None
        self._datos: DataBox._Datos = self._Datos()
        self._col = {
            "ti": "titulo",  # Un nombre diferenciador para mostrar
            "f": "fecha",  # La fecha de la lectura
            "r": "restante",  # Valor de tiempo que resta para terminar el Verkami
            "u": "unidades",  # Unidades (dias, horas, ...) del tiempo que resta
            "a": "aportaciones",  # Número de aportaciones
            "o": "objetivo",  # Importe inicial objetivo
            "t": "total"  # Total recaudado hasta el momento
        }
        # añade entradas en mayúsculas
        nuevas_entradas = {
            k.capitalize(): v.capitalize()
            for k, v in self._col.items()
            if k.capitalize() not in self._col
        }
        self._col.update(nuevas_entradas)

        if self._nombre_fichero:
            if os.path.isfile(self._nombre_fichero):
                self._df = pd.read_excel(self._nombre_fichero)
                self._validar_campos()

                if self._df.shape[0] == 0:
                    raise ValueError(f"Fichero vacío '{self._nombre_fichero}'")

                # Ordenar por fecha y tomar la última fila
                self._df.sort_values(by=self.col("F"), inplace=True)
                fila = self._df.iloc[-1]

                d = self._datos_anteriores

                d.titulo = fila[self.col("Ti")]
                d.fecha = fila[self.col("F")]
                d.restante = fila[self.col("R")]
                d.unidades = fila[self.col("U")]
                d.aportaciones = fila[self.col("A")]
                d.objetivo = fila[self.col("O")]
                d.total = fila[self.col("T")]


    def _validar_campos(self) -> bool:
        # Campos definidos en la dataclass
        campos_lectura = {campo.name for campo in fields(self.datos)}

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
            raise KeyError(msg)

        return True


    @property
    def datos(self) -> _Datos:
        """
        Esta propiedad se ha repetido en la subclase splo para que
        el IDE de Pycharm pueda hacer su revisión estática de tipos y no
        señale errores de tipos en esta clase interna
        """
        return self._datos

    @datos.setter
    def datos(self, datos_nuevos: _Datos):
        # Antes sustituir la lectura nueva, saca una copia como lectura anterior
        self._datos_anteriores = copy(self._datos)
        # Y ahora puede ya machacarla con el nuevo valor recién leído
        self._datos = copy(datos_nuevos)

        # si no tiene fecha asignada, le asigna la fecha del sistema
        if not self._datos.fecha:
            self._datos.set_fecha()

        if self.datos_cambiados:
            d = asdict(datos_nuevos)
            for clave in list(d.keys()):
                d[clave.capitalize()] = d.pop(clave)
            nueva_fila = pd.DataFrame(d, index=[0])
            self._df = pd.concat(objs=[self._df, nueva_fila], ignore_index=True)

            # Persistencia de datos en fichero Excel
            if self._nombre_fichero:
                df = self._df.copy()
                df.columns = [col.capitalize() for col in df.columns]
                tools.exportar_excel(fich=self._nombre_fichero, data={"Hoja1": df})


    @property
    def datos_cambiados(self) -> bool:
        ret = False
        if (
                self.datos.titulo != self.datos.titulo
                or (self.datos.fecha == "" and self.datos.fecha != "")
                or self.datos.total != self.datos.total
        ):
            ret = True

        return ret

    def persistir_datos(self) -> None:
        if not self._nombre_fichero:
            logger.warning("No se ha suministrado un nombre de fichero Excel "
                           "para almacenar los datos leídos")

    def col(self, key: Literal["ti", "Ti", "f", "F", "r", "R", "u", "U", "a", "A", "o", "O", "t", "T"]) -> str:
        return self._col[key]

    def salida_formateada_str(self, formato: Literal["a", "b", "c", "ab"] = "a") -> str:
        def _formato_a(datos: DataBoxVerkami._Datos) -> str:
            df = pd.DataFrame(asdict(datos), index=[0])
            return df.to_string(index=False)

        def _formato_ab(datos: DataBoxVerkami._Datos) -> str:
            df = pd.DataFrame(asdict(datos), index=[0])
            columnas_1 = [self.col("ti"), self.col("f"), self.col("o")]
            columnas_2 = [self.col("r"), self.col("u"), self.col("a"), self.col("t")]
            linea1 = "\n" + df[columnas_1].to_string(index=False)
            linea2 = "\n" + df[columnas_2].to_string(index=False)
            largo = int(max(len(linea1), len(linea2)) / 2)
            rayas = "\n" + "-" * largo
            fmt = linea1 + rayas + linea2 + rayas
            return fmt

        def _formato_b(datos: DataBoxVerkami._Datos) -> str:
            fmt = f"{datos.fecha}: {datos.titulo:28}\n"
            fmt += f"{self.col('O')}: {datos.objetivo:,.0f} €, Quedan {datos.restante:3d} {datos.unidades:18}\n"
            fmt += f"{self.col('A')}: {datos.aportaciones:4d}, {self.col('T')}: {datos.total:,.2f} €"
            return fmt

        def _formato_c(datos: DataBoxVerkami._Datos) -> str:
            promedio = 0
            if datos.aportaciones != 0:
                promedio = datos.total / datos.aportaciones

            fmt = f"<b>{datos.fecha}</b>: {datos.titulo:28}\n"
            fmt += f"{self.col('O')}: <b>{datos.objetivo:7,.0f} €</b>, tiempo restante: <b>{datos.restante} {datos.unidades}</b>\n"
            fmt += f"<b>{datos.aportaciones}</b> {self.col('A')}, {self.col('T')} recaudado: <b>{datos.total:7,.0f} €</b>\n"
            fmt += f"({promedio:,.0f} € promedio/aportación)"
            return fmt

        salida = ""

        if formato == "a":
            salida = _formato_a(self.datos)
        elif formato == "b":
            salida = _formato_b(self.datos)
        elif formato == "c":
            salida = _formato_c(self.datos)
        elif formato == "ab":
            salida = _formato_ab(self.datos)

        return salida

    # noinspection SpellCheckingInspection
    async def mostrar_datos(
            self,
            es_una_repeticion=False,
            con_voz=False,
            chatbot: Chatbot | None = None
    ):
        if ((config.tipo_notificaciones_activo == config.Notificaciones.TODOS_LOS_INTERVALOS or
             (config.tipo_notificaciones_activo == config.Notificaciones.SOLO_CAMBIOS
              and self.datos_cambiados)) or es_una_repeticion):
            if self.datos_cambiados:
                txt_cambiados = "** ¡NUEVOS DATOS! **"
                melodia = winotify.audio.LoopingAlarm4
            else:
                txt_cambiados = "... (sin cambios) ..."
                melodia = winotify.audio.LoopingCall2

            numero = num2words(number=self.datos.total, lang="es")
            msg_voz = f"Atención: se ha alcanzado un total de {numero} euros"
            msg = self.salida_formateada_str(formato="b")
            tools.mostrar_notificacion(
                titulo=txt_cambiados,
                msg=msg,
                msg_hablado=msg_voz if con_voz else "",
                sonido=melodia
            )
            if chatbot:
                print(f"{chatbot=}  --- {chatbot.esta_activo=}")
                if chatbot.esta_activo:
                    await chatbot.enviar_mensaje_a_suscriptores(
                        texto=msg, keyboard=True, parse_mode=ParseMode.HTML
                    )

        logger.info(
            f"Lectura de datos desde: {self.datos.titulo}  -->>  {self.datos.fecha}  ({config.tupla_intervalo_activo[0]})")
        print(f"mostrar_datos() (formato 'a' ) -->> \n{self.salida_formateada_str("a")}\n" + "-" * 104 + "\n")
        logger.info(f"mostrar_datos() (formato 'ab') -->> \n{self.salida_formateada_str("ab")}\n")


if __name__ == "__main__":
    async def main():
        loop = asyncio.get_event_loop()

        data = DataBoxVerkami()
        data.datos.titulo = "Prueba de datos nuevos"
        data.datos.set_fecha()
        data.datos.objetivo = 250000
        data.datos.unidades = "Horas"
        data.datos.restante = 12
        data.datos.aportaciones = 133
        data.datos.total = 125000
        print(data.datos)

        for f in ["a", "b", "c", "ab"]:
            print(f">> Salida '{f}'" + ("-" * 60))
            print(data.salida_formateada_str(formato=f))
            print("")

    asyncio.run(main())

