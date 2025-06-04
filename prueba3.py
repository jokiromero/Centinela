import asyncio
import logging
from tinyxmpp import XMPPClient


logging.basicConfig(level=logging.DEBUG)


def get_pass():
    print("get_pass()")
    return "C3nt1n3l4"
    # return "Such4t.0rg"


jid, passw = "centinela@suchat.org", get_pass()
destino = "joki@suchat.org"


async def main():
    client = XMPPClient(jid=jid, password=passw)
    client.on_message = on_message
    client.on_iq = on_iq
    client.on_presence = on_presence
    print("Iniciando conexión...")
    await client.connect(host="suchat.org", port=None, ssl=False)
    print("Conectado...")
    print("Haciendo PING...")
    await asyncio.wait_for(client.ping(), timeout=10)
    print("Enviando mensaje...")
    # await client.send_message(to=destino,  message="Prueba de mensaje enviado desde Centinela")
    try:
        await asyncio.wait_for(
            client.send_message(
                to=destino, message="Prueba de mensaje enviado desde Centinela"
            ), timeout=10
        )
        print("Mensaje enviado...")
    except asyncio.TimeoutError:
        print("Timeout al enviar el mensaje")


async def on_message(message):
    print(message)


async def on_presence(element):
    print(element)


async def on_iq(element):
    print(element)


# loop = asyncio.get_event_loop()
# loop.create_task(main())
# loop.run_forever()

asyncio.run(main())
