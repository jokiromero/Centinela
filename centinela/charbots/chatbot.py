from abc import ABC, abstractmethod


class Chatbot(ABC):
    def __init__(self):
        self._inicializado = False

    @abstractmethod
    def _inicializar(self, *args, **kwargs) -> None:
        pass

    def _check_inicializado(self):
        if not self._inicializado:
            raise RuntimeError("La clase no ha sido inicializada correctamente...")

    @abstractmethod
    async def iniciar(self, *args, **kwargs):
        pass

    @abstractmethod
    async def enviar_mensaje_usuario(self, *args, **kwargs):
        pass

    @abstractmethod
    async def enviar_mensaje_a_suscriptores(self, *args, **kwargs):
        pass

    @abstractmethod
    async def detener(self):
        pass

