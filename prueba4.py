import logging
from sleekxmpp import ClientXMPP


class SendMessage(ClientXMPP):
    def __init__(self, jid, password, recipient, message):
        super(SendMessage, self).__init__(jid, password)
        self.recipient = recipient
        self.message = message
        self.add_event_handler("session_start", self.start)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.send_message(mto=self.recipient, mbody=self.message, mtype='chat')
        self.disconnect(wait=True)


def get_pass():
    return "Such4t.0rg"


jid = "joki@suchat.org"
password = get_pass()
recipient = "centinela@suchat.org"
message = "Prueba de mensaje enviado desde Centinela"

logging.basicConfig(level=logging.DEBUG)

xmpp = SendMessage(jid, password, recipient, message)
xmpp.register_plugin('xep_0030')  # Service Discovery
xmpp.register_plugin('xep_0199')  # XMPP Ping

if xmpp.connect():
    xmpp.process(block=True)
    print("Mensaje enviado...")
else:
    print("No se pudo conectar")
