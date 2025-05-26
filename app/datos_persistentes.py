import os
from copy import copy

import pandas as pd

from typing import Any, Literal
from datetime import datetime
from dataclasses import dataclass, asdict

from app import tools

cols = {
    "f": "Fecha",
    "d": "Dias",
    "a": "Aportaciones",
    "o": "Obj",
    "t": "Total"
}


@dataclass
class Lectura:
    fecha: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dias: int = 0
    aportaciones: int = 0
    objetivo: float = 0
    total: float | None = None

    def get_fecha(self) -> datetime:
        return datetime.strptime(self.fecha, "%Y-%m-%d  %H:%M:%S")


class DatosPersistentes:
    def __init__(self, nombre_fichero: str | os.PathLike = ""):
        self._df = None  # DataFrame
        self._lectura_anterior: Lectura = Lectura()
        self._lectura_nueva: Lectura = Lectura()
        if nombre_fichero:
            self._fichero = os.path.join(os.getcwd(), nombre_fichero)
        else:
            self._fichero = None

        if nombre_fichero:
            if os.path.isfile(self._fichero):
                columnas = str(", ".join(cols))
                self._df = pd.read_excel(self._fichero)
                if self._df.shape[0] > 0:  # Si tiene al menos un registro
                    self._df.sort_values(by=cols["f"], inplace=True)
                    self._lectura_anterior = Lectura(
                        fecha=self._df.iloc[-1][cols["f"]],
                        dias=self._df.iloc[-1][cols["d"]],
                        aportaciones=self._df.iloc[-1][cols["a"]],
                        objetivo=self._df.iloc[-1][cols["o"]],
                        total=self._df.iloc[-1][cols["t"]],
                    )

    @property
    def datos_cambiados(self) -> bool:
        ret = False
        if self.lectura_anterior.total is None or self.lectura_anterior.total != self.lectura_nueva.total:
            ret = True
        return ret

    @property
    def lectura_nueva(self) -> Lectura:
        return self._lectura_nueva

    @lectura_nueva.setter
    def lectura_nueva(self, datos_nuevos: Lectura):
        self._lectura_nueva = copy(datos_nuevos)

        if self.datos_cambiados:
            print("lectura_nueva() ha detectado que los datos_web han cambiado...")
            nueva_fila = pd.DataFrame(asdict(datos_nuevos), index=[0])
            self._df = pd.concat(objs=[self._df, nueva_fila], ignore_index=True)
            self._guardar_lectura()

    @property
    def lectura_anterior(self) -> Lectura | None:
        if self._lectura_anterior:
            return self._lectura_anterior
        else:
            return None

    def _guardar_lectura(self):
        if self._fichero:
            tools.exportar_excel(fich=self._fichero, data={"Hoja1": self._df})

        print(f"_guardar_lectura() conserva una copia de la lectura nueva como anterior: {self.lectura_nueva}")
        self._lectura_anterior = copy(self.lectura_nueva)

    def get_salida_tabulada(self, formato: Literal[0, 1, 2]) -> str:
        def _formato0(lec: Lectura) -> str:
            df = pd.DataFrame(asdict(lec), index=[0])
            return df.to_string(index=False)

        def _formato1(lec: Lectura) -> str:
            fmt = ""
            fmt += f"{cols["d"]:18} = {lec.dias:8d}\n"
            fmt += f"{cols["a"]:18} = {lec.aportaciones:8d}\n"
            fmt += f"{cols["o"]:18} = {lec.objetivo:11,.2f} €\n"
            fmt += f"{cols["t"]:18} = {lec.total:11,.2f} €"
            return fmt

        def _formato2(lec: Lectura) -> str:
            fmt = ""
            fmt += f"{lec.dias} {cols["d"]}.  {cols["o"]}: {lec.objetivo:7,.0f} €\n"
            fmt += f"{lec.aportaciones} {cols["a"][:5]}. {cols["t"]}: {lec.total:7,.0f} €\n"
            fmt += f"({(lec.total / lec.aportaciones):,.0f} € promedio por cada una)"
            return fmt

        salida = ""

        if formato == 0:
            salida = _formato0(self.lectura_nueva)
        elif formato == 1:
            salida = _formato1(self.lectura_nueva)
        elif formato == 2:
            salida = _formato2(self.lectura_nueva)

        return salida
