import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from dataclasses import asdict


class DataBox(ABC):
    """
    Clase base que contiene los datos y formatos de visualización
    de los campos que se extraen de los Web Sites mediante Scrapping
    """

    @dataclass
    class Datos:
        """Dataclass para los campos y sus definiciones"""
        pass

    @abstractmethod
    def __init__(self):
        self._datos: DataBox.Datos = self.Datos()

    @property
    def datos(self) -> Datos:
        return self._datos

    @abstractmethod
    def salida_formateada_str(self, *args)->str:
        pass



# noinspection DuplicatedCode
class DataBoxVerkami(DataBox):
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

    def __init__(self):
        super().__init__()
        self._datos: DataBox.Datos = self._Datos()
        self._columnas =  {
            "ti": "titulo",         # Un nombre diferenciador para mostrar
            "f": "fecha",           # La fecha de la lectura
            "r": "restante",        # Valor de tiempo que resta para terminar el Verkami
            "u": "unidades",        # Unidades (dias, horas, ...) del tiempo que resta
            "a": "aportaciones",    # Número de aportaciones
            "o": "objetivo",        # Importe inicial objetivo
            "t": "total"            # Total recaudado hasta el momento
        }
        # añade entradas en mayúsculas
        nuevas_entradas = {
            k.capitalize(): v.capitalize()
            for k, v in self._columnas.items()
            if k.capitalize() not in self._columnas
        }

        self._columnas.update(nuevas_entradas)

    @property
    def datos(self) -> _Datos:
        """
        Esta propiedad se ha repetido en la subclase sólo para que
        el IDE de Pycharm pueda hacer su revisión estática de tipos y no
        señale errores de tipos en esta clase interna
        """
        return self._datos

    def col(self, key: Literal["ti", "Ti", "f", "F", "r", "R", "u", "U", "a", "A", "o", "O", "t", "T"]) -> str:
        return self._columnas[key]

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
            fmt = f"{datos.titulo:28}\n"
            fmt += f"{datos.unidades:18} = {datos.restante:8d}\n"
            fmt += f"{self.col('A'):18} = {datos.aportaciones:8d}\n"
            fmt += f"{self.col('O'):18} = {datos.objetivo:11,.2f} €\n"
            fmt += f"{self.col('T'):18} = {datos.total:11,.2f} €"
            return fmt

        def _formato_c(datos: DataBoxVerkami._Datos) -> str:
            promedio = 0
            if datos.aportaciones != 0:
                promedio = datos.total / datos.aportaciones

            fmt = f"<b>{datos.fecha}</b>: {datos.titulo:28}\n"
            fmt += f"{self.col('O')}: <b>{datos.objetivo:7,.0f} €</b>, tiempo restante: <b>{datos.restante} {datos.unidades}</b>\n"
            fmt += f"<b>{datos.aportaciones}</b> {self.col('A')}, {self.col('T')} recaudado: <b>{datos.total:7,.0f} €</b>\n"
            fmt += f"({promedio:,.0f} € promedio por aport.)"
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


if __name__ == "__main__":
    data = DataBoxVerkami()
    data.datos.titulo = "Prueba de datos nuevos"
    data.datos.set_fecha()
    data.datos.objetivo = 250000
    data.datos.unidades = "Horas"
    data.datos.restante = 12
    data.datos.aportaciones = 133
    data.datos.total = 125000
    print(data.datos)

    print(data.salida_formateada_str("a"))
    print(">>>>>>>>>>>>>>>>>>>>>")
    print(data.salida_formateada_str("ab"))
    print(">>>>>>>>>>>>>>>>>>>>>")
    print(data.salida_formateada_str("b"))
    print(">>>>>>>>>>>>>>>>>>>>>")
    print(data.salida_formateada_str("c"))
    print(">>>>>>>>>>>>>>>>>>>>>")

