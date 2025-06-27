"""
🎯 Objetivo
Cuando el bot envía una foto, registra en un archivo Excel (mensajes.xlsx) los siguientes datos:

Fecha y hora del mensaje (timestamp)

ID del mensaje (message_id)

ID del chat (chat_id)

Con el comando /limpiar, el bot:

Lee el archivo Excel.

Filtra los mensajes de más de 30 días.

Intenta borrar esos mensajes con bot.delete_message(...).

Elimina las filas borradas del Excel y guarda el archivo actualizado.
"""


import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor
import pandas as pd
from datetime import datetime, timedelta
import os

API_TOKEN = 'TU_TOKEN_AQUI'
EXCEL_FILE = 'mensajes.xlsx'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Asegura que el archivo Excel exista con columnas si aún no fue creado
def inicializar_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=['timestamp', 'message_id', 'chat_id'])
        df.to_excel(EXCEL_FILE, index=False)

# Guarda datos del mensaje en el Excel
def guardar_mensaje(timestamp: datetime, message_id: int, chat_id: int):
    df = pd.read_excel(EXCEL_FILE)
    nuevo = pd.DataFrame([{
        'timestamp': timestamp,
        'message_id': message_id,
        'chat_id': chat_id
    }])
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

# Comando para enviar una imagen y guardar el mensaje
@dp.message_handler(commands=['foto'])
async def enviar_foto(message: types.Message):
    inicializar_excel()

    # Envía una imagen local
    photo = InputFile("ruta/a/tu/imagen.jpg")
    sent_msg = await message.answer_photo(photo, caption="Esta imagen ha sido registrada para borrado futuro.")

    # Guarda la info del mensaje
    timestamp = datetime.now()
    guardar_mensaje(timestamp, sent_msg.message_id, sent_msg.chat.id)

# Comando para limpiar mensajes de hace más de 30 días
@dp.message_handler(commands=['limpiar'])
async def limpiar_mensajes_antiguos(message: types.Message):
    inicializar_excel()
    try:
        df = pd.read_excel(EXCEL_FILE, parse_dates=['timestamp'])
    except Exception as e:
        await message.answer("Error al leer el archivo de mensajes.")
        return

    ahora = datetime.now()
    umbral = ahora - timedelta(days=30)

    eliminados = 0
    indices_a_borrar = []

    for index, row in df.iterrows():
        if pd.to_datetime(row['timestamp']) < umbral:
            try:
                await bot.delete_message(chat_id=row['chat_id'], message_id=row['message_id'])
                eliminados += 1
                indices_a_borrar.append(index)
            except Exception as e:
                print(f"No se pudo borrar mensaje {row['message_id']}: {e}")

    # Eliminar las filas del Excel correspondientes
    df.drop(index=indices_a_borrar, inplace=True)
    df.to_excel(EXCEL_FILE, index=False)

    await message.answer(f"Se han borrado {eliminados} mensajes multimedia antiguos.")

# Comando básico de prueba
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Usa /foto para enviar una imagen registrada.\nUsa /limpiar para borrar imágenes de más de 30 días.")

if __name__ == '__main__':
    inicializar_excel()
    executor.start_polling(dp, skip_updates=True)
