import random
from collections import OrderedDict
from copy import copy
from faker import Faker
from centinela.datos_persistentes import Lectura, DatosPersistentes


def generar_valores_nuevos(val: Lectura) -> Lectura:
    copia = copy(val)
    copia.dias -= fake.random_element(
        elements=OrderedDict([(0, 0.8), (1, 0.2)])
    )
    aportaciones_nuevas = fake.random_int(min=1, max=5)
    importe_de_aportaciones = fake.random_int(min=30, max=70) * aportaciones_nuevas
    copia.aportaciones += aportaciones_nuevas
    copia.total += importe_de_aportaciones
    return copia


if __name__ == "__main__":
    val_inicial = Lectura(
        dias=40,
        aportaciones=0,
        objetivo=6000,
        total=0
    )
    fake = Faker()
    data = DatosPersistentes(nombre_fichero="prueba.xlsx")
    if data.lectura_anterior.fecha == "":
        print(f"--> Sin lectura anterior {data.lectura_anterior=}")
        print(f"    Asignamos valores por defecto...")
        val_inicial.set_fecha()
        data.lectura_nueva = val_inicial

    print(f"--> Lectura anterior {data.lectura_anterior=}")
    cambios_de_valor = [10, 14, 23, 40, 41]

    val_act = data.lectura_anterior
    for i in range(45):
        if i in cambios_de_valor or i == 0:
            nuevo = generar_valores_nuevos(val_act)
            print(f"¡¡DATOS NUEVOS HAN SIDO LEÍDOS!!------------------------------")
            print(nuevo)
            val_act = copy(nuevo)
        else:
            print(f">>\tRepetimos datos\n{val_act}")

        data.lectura_nueva = val_act

