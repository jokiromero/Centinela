"""
https://pillow.readthedocs.io/en/stable/

llamada a la API de Telegram:
id del grupo "Grupo_Centinela": -2429045608

enviar un mensaje a un chat sabiendo el chat-id
curl -X POST "https://api.telegram.org/bot8126096557:AAFqH6XABfmd-ZQlVdoSHiCAVT9O8JMt0iY/sendMessage" -d "chat_id=-8126096557&text=my sample text"

"""
# bot_card_pillow.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart, Command
from PIL import Image, ImageDraw, ImageFont
import io

import config

API_TOKEN = config.TOKEN_TELEGRAM
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

connected_users = set()

# Ruta a la fuente: ajusta según tu sistema
# Windows: "C:\\Windows\\Fonts\\arial.ttf"
# Linux: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FUENTE_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FUENTE_NEGRITA = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def generar_tarjeta_visual(nombre: str, valor: float, estado: str) -> bytes:
    # Dimensiones y estilos
    ancho, alto = 600, 320
    fondo_color = (240, 240, 240)
    borde_color = (52, 152, 219)
    estado_color = (39, 174, 96) if estado == "Activo" else (231, 76, 60)
    sombra_color = (200, 200, 200)

    # Crear imagen base
    img = Image.new("RGB", (ancho, alto), fondo_color)
    draw = ImageDraw.Draw(img)

    # Sombra (simulada)
    sombra_offset = 6
    draw.rounded_rectangle(
        xy=[sombra_offset, sombra_offset, ancho - 20 + sombra_offset, alto - 40 + sombra_offset],
        radius=20, fill=sombra_color
    )

    # Tarjeta principal
    draw.rounded_rectangle(
        xy=[10, 10, ancho - 20, alto - 40],
        radius=20,
        fill="white",
        outline=borde_color,
        width=3
    )

    # Cargar fuentes
    fuente_titulo = ImageFont.truetype(FUENTE_NEGRITA, 26)
    fuente_texto = ImageFont.truetype(FUENTE_REGULAR, 20)
    fuente_estado = ImageFont.truetype(FUENTE_NEGRITA, 20)

    # Texto de la tarjeta
    draw.text((540, 30), "💳 Tarjeta de Usuario", font=fuente_titulo, fill=(44, 62, 80), anchor="rs")
    draw.text((40, 90), f"👤 Nombre:", font=fuente_texto, fill=(52, 73, 94))
    draw.text((180, 90), nombre, font=fuente_texto, fill=(41, 128, 185))

    draw.text((40, 140), f"💰 Valor:", font=fuente_texto, fill=(52, 73, 94))
    draw.text((180, 140), f"${valor:,.2f}", font=fuente_texto, fill=(39, 174, 96))

    draw.text((40, 190), f"📈 Estado:", font=fuente_texto, fill=(52, 73, 94))
    draw.text((180, 190), estado, font=fuente_estado, fill=estado_color)

    draw.text((40, 250), "Gracias por usar nuestro servicio 🙌", font=fuente_texto, fill=(127, 140, 141))

    # Convertir a bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    connected_users.add(message.chat.id)
    await message.answer("✅ Estás registrado para recibir tarjetas visuales.")

@dp.message(Command("enviar"))
async def enviar_tarjeta(message: Message):
    imagen_bytes = generar_tarjeta_visual("Juan Pérez", 2450.30, "Activo")
    archivo = BufferedInputFile(imagen_bytes, filename="tarjeta.png")
    print(f"{connected_users=}")
    errores = 0
    for user_id in connected_users:
        try:
            await bot.send_photo(chat_id=user_id, photo=archivo, caption="📩 Tu tarjeta personalizada:")
        except Exception as e:
            logging.warning(f"Error enviando imagen a {user_id}: {e}")
            errores += 1

    await message.answer(f"✅ Tarjeta enviada a {len(connected_users) - errores} usuarios.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
