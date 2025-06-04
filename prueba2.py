#
# https://medium.com/@supun1001/python-reading-credentials-from-windows-credential-manager-generic-creds-bfcafb99055a
#
import keyring
import asyncio
import aioxmpp


def get_pass():
    print("get_pass()")
    # return "C3nt1n3l4"
    return "Such4t.0rg"


async def mensaje_xmpp(mensaje: str):
    # destino = aioxmpp.JID.fromstr("centinela@salas.suchat.org")
    destino = aioxmpp.JID.fromstr("centinela@suchat.org")
    jid = aioxmpp.JID.fromstr("joki@suchat.org")
    passw = get_pass()
    print(f"{jid=}")

    cli = aioxmpp.PresenceManagedClient(
        jid,
        aioxmpp.make_security_layer(passw)
    )
    print(f"{cli.connected()=}")
    async with cli.connected() as stream:
        print(f"{stream=}")
        msg = aioxmpp.Message(
            to=destino,
            type=aioxmpp.MessageType.CHAT
            # type_=aioxmpp.MessageType.GROUPCHAT
        )
        msg.body[None] = msg

        await cli.send(msg)

    # conn = cli.connected()
    # print(f"{conn=}")
    # msg = aioxmpp.Message(
    #     to=destino,
    #     type_=aioxmpp.MessageType.CHAT
    #     # type_=aioxmpp.MessageType.GROUPCHAT
    # )
    # msg.body[None] = msg
    # print(msg)
    # await cli.send(msg)


if __name__ == "__main__":
    # keyring.set_password("xmpp", "centinela@suchat.org", "C3nt1n3l4")
    print("Enviando el mensaje...")
    asyncio.run(mensaje_xmpp("Esto es una prueba"))
    print("Terminado!")