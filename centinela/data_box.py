# Sirve para poder usar "forward reference" que son declaraciones
# y usos de anotaciones sobre tipos o clases que se definen más
# adelante en el código (future)
from __future__ import annotations

import dataclasses
import logging
import os
import time

import pandas as pd
import winotify
import config
import tools

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, fields, field
from datetime import datetime
from typing import Literal, TypeVar, Type, Any, overload
from dataclasses import asdict
from aiogram.enums import ParseMode
from num2words import num2words
from chatbots import Chatbot

# definimos T como cualquier subclase de Databox()
T = TypeVar("T", bound="Databox")

logger = logging.getLogger(__name__)


class FormatoSalida(str, Enum):
    A = "a"
    B = "b"
    C = "c"
    AB = "ab"


class Databox(ABC):
    """
    Clase base que contiene los datos y formatos de visualización
    de los campos que se extraen de Web Sites mediante Scrapping
    """

    @dataclass(frozen=True, slots=True)
    class _Datos:
        """
        Dataclass para los campos y sus definiciones
        fronzen=True    Hace la instancia inmutable (como una tupla).
                        Evita cambios inesperados.
        slots=True      Ahorra memoria y mejora el rendimiento
                        evitando __dict__. También atrapa errores por
                        atributos inválidos. Disponible desde Python 3.10.
        field(default_factory=list)
                        Recomendado para campos mutables como listas o
                        diccionarios. Evita usar intereses=[] directamente.
        ejemplo:
            nombre: str
            edad: int
            intereses: List[str] = field(default_factory=list)
            email: Optional[str] = None
        """
        fecha: str = field(
            default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        def _set_fecha(self) -> Databox._Datos:
            nueva_fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return dataclasses.replace(self, fecha=nueva_fecha)

    def __init__(self, datos: Databox._Datos | None = None):
        self._datos = self._datos_anteriores = datos

    @classmethod
    def new_datos(cls: Type[T], **kwargs: Any) -> Databox._Datos:
        """
        Método de clase que permite crear objetos del tipo _Datos
        específicos para cada tipo de Databox
        :param kwargs:
        :return:
        """
        # Validar los campos del dataclass
        campos_validos = {f.name for f in fields(cls._Datos)}
        extras = set(kwargs) - campos_validos
        if extras:
            raise TypeError(f"Campos no válidos: {extras}")
        datos = cls._Datos(**kwargs)
        return datos

    @property
    def datos(self) -> Databox._Datos:
        return self._datos

    @abstractmethod
    def actualizar_datos(self, datos_nuevos: Databox._Datos):
        pass

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

    @classmethod
    def cargar(cls: Type[T], ruta: str) -> T:
        """
        cls: Type[T] indica que el argumento es la clase concreta que invoca el método.
        T asegura que el método devuelve un objeto del mismo tipo que cls.
        """
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

        df = pd.read_excel(ruta)
        if df.empty:
            raise ValueError("El archivo está vacío")

        columnas_esperadas = {f.name for f in fields(cls._Datos)}
        columnas_encontradas = set(df.columns)

        faltantes = columnas_esperadas - columnas_encontradas
        if faltantes:
            raise ValueError(f"Faltan columnas esperadas: {faltantes}")

        historial = [
            cls._Datos(**fila)  # type: ignore[arg-type]
            for fila in df.to_dict(orient="records")
        ]

        instancia = cls(historial[0])
        instancia._historial = historial
        instancia._datos = historial[-1]
        return instancia


# noinspection DuplicatedCode
class DataboxVerkami(Databox):
    """
    Clase que representa el conjunto de datos leídos del site de Verkami
    junto a sus métodos y formatos de visualización y persistencia
    """

    # noinspection DuplicatedCode
    @dataclass(frozen=True, slots=True)
    class _Datos(Databox._Datos):
        titulo: str = ""
        resto_valor: int = 0
        resto_etiq: str = ""
        aporta_valor: int = 0
        aporta_etiq: str = ""
        objetivo: int = 0
        total: int = 0
        fecha: str = field(
            default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        def _set_fecha(self) -> DataboxVerkami._Datos:
            nueva_fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return dataclasses.replace(self, fecha=nueva_fecha)

    def __init__(self, datos: DataboxVerkami._Datos | None = None,
                 nombre_fichero_excel: str | os.PathLike | None = None):
        super().__init__(datos)
        self._nombre_fichero = nombre_fichero_excel
        self._df_historia = None
        # self._datos = self._datos_anteriores = datos  (esto se hace en super())
        self._col = {
            "ti": "titulo",  # Un nombre diferenciador para mostrar
            "f": "fecha",  # La fecha de la lectura
            "rv": "resto_valor",  # Valor de tiempo que resta para terminar el Verkami
            "re": "resto_etiq",  # Unidades (dias, horas, ...) del tiempo que resta
            "av": "aporta_valor",  # Número de aportaciones
            "ae": "aporta_etiq",  # Aportaciones etiqueta
            "o": "objetivo",  # Importe inicial objetivo
            "t": "total"  # Total recaudado hasta el momento
        }
        # Añade entradas en mayúsculas que serán usadas en visualización
        # las minúsculas son para columnas del DataFrame y nombres internos de campos
        nuevas_entradas = {
            k.capitalize(): v.capitalize()
            for k, v in self._col.items()
            if k.capitalize() not in self._col
        }
        self._col.update(nuevas_entradas)

        if self._nombre_fichero:
            if os.path.isfile(self._nombre_fichero):
                self._df_historia = pd.read_excel(self._nombre_fichero)
                self._validar_campos()

                if self._df_historia.shape[0] == 0 or self._df_historia.empty:
                    raise ValueError(f"Fichero vacío '{self._nombre_fichero}'")

                # Ordenar por fecha y tomar la última fila
                self._df_historia.sort_values(by=self.col("F"), inplace=True)
                fila = self._df_historia.iloc[-1]

                self._datos = DataboxVerkami.new_datos(
                    titulo=fila[self.col("Ti")],
                    fecha=fila[self.col("F")],
                    resto_valor=fila[self.col("Rv")],
                    resto_etiq=fila[self.col("Re")],
                    aporta_valor=fila[self.col("Av")],
                    aporta_etiq = fila[self.col("Ae")],
                    objetivo=fila[self.col("O")],
                    total=fila[self.col("T")]
                )

    def col(self, key: Literal["ti", "Ti", "f", "F", "rv", "Rv", "re", "Re",
    "av", "Av", "ae", "Ae", "o", "O", "t", "T"]) -> str:
        return self._col[key]

    def _validar_campos(self) -> bool:
        # Campos definidos en la dataclass
        if not self.datos:
            self._datos = DataboxVerkami._Datos()
        campos_lectura = {campo.name for campo in fields(self.datos)}

        # Columnas del DataFrame
        campos_df = set(
            [col.lower() for col in self._df_historia.columns]
        )

        # Comparación entre los campos leídos del Excel y los campos del data_box
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
    def datos(self) -> DataboxVerkami._Datos:
        """
        Esta propiedad se ha repetido en la subclase splo para que
        el IDE de Pycharm pueda hacer su revisión estática de tipos y no
        señale errores de tipos en esta clase interna
        """
        return self._datos

    @overload
    @classmethod
    def new_datos(
            cls: Type[T], *,
            titulo: str,
            resto_valor: int,
            resto_etiq: str,
            aporta_valor: int,
            aporta_etiq: str,
            objetivo: float,
            total: float,
            fecha: str
    ) -> DataboxVerkami._Datos:
        ...
        """Esta firma de new_datos es sólo para definir los tipos para el IDE PyCharm"""

    @classmethod
    def new_datos(cls, **kwargs: Any) -> DataboxVerkami._Datos:
        """
        Se sobre escribe el método new_datos pero solamente para delegar
        sobre el superclase porque así se cumple que exista un método definido
        a continuación de un método decorado con @overload
        :param kwargs:
        :return:
        """
        return super().new_datos(**kwargs)

    def actualizar_datos(self, datos_nuevos: DataboxVerkami._Datos) -> None:
        # Antes sustituir la lectura nueva, saca una copia como lectura anterior
        self._datos_anteriores = self._datos
        # Y ahora puede ya machacarla con el nuevo valor recién leído
        self._datos = datos_nuevos

        # if self._datos_anteriores is None:
        #     self._datos_anteriores = self._datos

        if self.datos_cambiados:
            # Persistencia de datos en fichero Excel
            d = asdict(datos_nuevos)
            for clave in list(d.keys()):
                d[clave.capitalize()] = d.pop(clave)
            nueva_fila = pd.DataFrame(d, index=[0])
            self._df_historia = pd.concat(
                objs=[self._df_historia, nueva_fila], ignore_index=True
            )

            if self._nombre_fichero:
                self.persistir_datos()

    @property
    def datos_cambiados(self) -> bool:
        ret = False
        if (
                self._datos_anteriores is None
                or self.datos.titulo != self._datos_anteriores.titulo
                or (self.datos.fecha == "" and self._datos_anteriores.fecha != "")
                or self.datos.resto_valor != self._datos_anteriores.resto_valor
                or self.datos.resto_etiq != self._datos_anteriores.resto_etiq
                or self.datos.total != self._datos_anteriores.total
        ):
            ret = True
        return ret

    def persistir_datos(self) -> None:
        if self._nombre_fichero:
            df = self._df_historia.copy()
            df.columns = [col.capitalize() for col in df.columns]
            tools.exportar_excel(fich=self._nombre_fichero, data={"Hoja1": df})
            logger.info(f"Los datos han sido guardados en el fichero Excel "
                        f"'{self._nombre_fichero}'")

        else:
            logger.warning("No se ha suministrado un nombre de fichero Excel "
                           "para almacenar los datos leídos")

    def salida_formateada_str(self, formato: FormatoSalida = FormatoSalida.A) -> str:
        def _formato_a(datos: DataboxVerkami._Datos) -> str:
            df = pd.DataFrame(asdict(datos), index=[0])
            return df.to_string(index=False)

        def _formato_ab(datos: DataboxVerkami._Datos) -> str:
            df = pd.DataFrame(asdict(datos), index=[0])
            columnas_1 = [self.col("ti"), self.col("f"), self.col("o")]
            columnas_2 = [self.col("rv"), self.col("re"), self.col("av"),
                          self.col("ae"),  self.col("t")]
            linea1 = "\n" + df[columnas_1].to_string(index=False)
            linea2 = "\n" + df[columnas_2].to_string(index=False)
            largo = int(max(len(linea1), len(linea2)) / 2)
            rayas = "\n" + "-" * largo
            fmt = linea1 + rayas + linea2 + rayas
            return fmt

        def _formato_b(datos: DataboxVerkami._Datos) -> str:
            fmt = f"{datos.fecha}: {datos.titulo:28}\n"
            fmt += (f"{self.col('O')}: {datos.objetivo:,.0f} €, "
                    f"Quedan {datos.resto_valor:,.0f} {datos.resto_etiq:18}\n")
            fmt += (f"{datos.aporta_etiq}: {datos.aporta_valor:,.0f}, "
                    f"{self.col('T')}: {datos.total:,.0f} €")
            return fmt

        def _formato_c(datos: DataboxVerkami._Datos) -> str:
            promedio = 0
            if datos.aporta_valor != 0:
                promedio = datos.total / datos.aporta_valor

            fmt = f"<b>{datos.fecha}</b>: {datos.titulo:28}\n"
            fmt += (f"{self.col('O')}: <b>{datos.objetivo:7,.0f} €</b>, "
                    f"tiempo restante: <b>{datos.resto_valor} {datos.resto_etiq}</b>\n")
            fmt += (f"<b>{datos.aporta_valor}</b> {datos.aporta_etiq}, {self.col('T')} "
                    f"recaudado: <b>{datos.total:7,.0f} €</b>\n")
            fmt += f"({promedio:,.0f} € promedio/aportación)"
            return f"<code>{fmt}</code>"

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
    async def mostrar_datos(self, es_una_repeticion=False, con_voz=False,
                            chatbot: Chatbot | None = None):
        if ((config.tipo_notificaciones_activo == config.Notificaciones.TODOS_LOS_INTERVALOS or
             (config.tipo_notificaciones_activo == config.Notificaciones.SOLO_CAMBIOS
              and self.datos_cambiados)) or es_una_repeticion):
            texto_cambio = ""
            if self.datos_cambiados:
                texto_cambio = "** ¡NUEVOS DATOS! **"
                melodia = winotify.audio.LoopingAlarm4
            else:
                texto_cambio = "... (sin cambios) ..."
                melodia = winotify.audio.LoopingCall2

            numero = num2words(number=self.datos.total, lang="es")
            msg_voz = f"Atención: se ha alcanzado un total de {numero} euros"
            msg1 = self.salida_formateada_str(formato=FormatoSalida.B)
            tools.mostrar_notificacion(
                titulo=texto_cambio,
                msg=msg1,
                msg_hablado=msg_voz if con_voz else "",
                sonido=melodia
            )
            if chatbot:
                if chatbot.esta_activo:
                    msg2 = self.salida_formateada_str(formato=FormatoSalida.C)
                    await chatbot.enviar_mensaje_a_suscriptores(
                        texto=texto_cambio + "\n" + msg2,
                        keyboard=True, parse_mode=ParseMode.HTML
                    )

        logger.info(f"Lectura de datos desde: {self.datos.titulo}  -->>  "
                    f"{self.datos.fecha}  ({config.tupla_intervalo_activo[0]})")
        formato = FormatoSalida.AB
        logger.info(f"mostrar_datos() (formato '{formato.value}') -->> \n{self.salida_formateada_str(formato)}\n")


if __name__ == "__main__":
    # Pruebas del módulo
    def main_1():
        data = DataboxVerkami.new_datos(
            titulo="Prueba de datos nuevos",
            objetivo=1111,
            resto_etiq="Horas",
            resto_valor=1,
            aporta_valor=111,
            aporta_etiq="Aportaciones",
            total=11119.99

        )
        print(f"Prueba: {data=}")

        dv = DataboxVerkami(nombre_fichero_excel=config.FICHERO_EXCEL_TEST)
        dv.actualizar_datos(datos_nuevos=data)
        print(f"Prueba 1 DataboxVerkami: \n{dv.salida_formateada_str(formato=FormatoSalida.A)}")
        print(f"{dv._datos_anteriores=}")
        print(f"{dv.datos_cambiados=}")


        # for f in FormatoSalida.__members__.values():
        #     print(f">> Salida '{f.value}'" + ("-" * 60))
        #     print(dv.salida_formateada_str(formato=f))
        #     print("")
        time.sleep(10)
        dv.actualizar_datos(
            datos_nuevos=DataboxVerkami.new_datos(
                titulo = "Datos cambiados",
                objetivo = 2222,
                resto_etiq = "Dias",
                resto_valor = 2,
                aporta_valor = 222,
                aporta_etiq = "Aportaciones",
                total = 11119.99
            )
        )
        print(f"Prueba 2 DataboxVerkami: \n{dv.salida_formateada_str(formato=FormatoSalida.A)}")
        print(f"{dv._datos_anteriores=}")
        print(f"{dv.datos_cambiados=}")

        time.sleep(5)
        dv.actualizar_datos(
            DataboxVerkami.new_datos(
                titulo = "Datos cambiados",
                objetivo = 2222,
                resto_etiq = dv.datos.resto_etiq,
                resto_valor = dv.datos.resto_valor,
                aporta_valor = dv.datos.aporta_valor,
                aporta_etiq = dv.datos.aporta_etiq,
                total = dv.datos.total
        )
        )
        print(f"Prueba 3 DataboxVerkami: \n{dv.salida_formateada_str(formato=FormatoSalida.A)}")
        print(f"{dv._datos_anteriores=}")
        print(f"{dv.datos_cambiados=}")


    def main_2():
        dv = DataboxVerkami(datos=DataboxVerkami.new_datos(
            titulo="Datos cambiados",
            objetivo=1111,
            resto_etiq="Dias",
            resto_valor=1,
            aporta_valor=11,
            aporta_etiq="Aportaciones",
            total=11119.99

        ))
        print(f"Prueba 1 DataboxVerkami: \n{dv.salida_formateada_str(formato=FormatoSalida.A)}")

        dv.actualizar_datos(
            DataboxVerkami.new_datos(
                titulo="Datos cambiados",
                fecha="2023-12-31 00:00:00",
                objetivo=2222,
                resto_etiq="Horas",
                resto_valor=2,
                aporta_valor=222,
                aporta_etiq="Aportaciones",
                total=22229.99

            )
        )
        print(f"Prueba 2 DataboxVerkami: \n{dv.salida_formateada_str(formato=FormatoSalida.A)}")


    # ----------------------------- PRUEBAS --------------------------
    # asyncio.run(main_1())
    main_1()
