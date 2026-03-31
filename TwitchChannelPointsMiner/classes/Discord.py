import time, requests, threading
from textwrap import dedent
from TwitchChannelPointsMiner.classes.Settings import Events

class Discord(object):
    __slots__ = ["webhook_api", "events", "bloqueo"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        self.events = [str(e) for e in events]
        self.bloqueo = 0

    def _enviar(self, payload):
        try:
            resp = requests.post(self.webhook_api, json=payload, timeout=10)
            if resp.status_code == 429:
                espera = float(resp.headers.get("Retry-After", 10))
                self.bloqueo = time.time() + espera
                print(f"[Discord] Bloqueo de {espera}s. Ignorando mensajes...")
        except:
            pass # Evita que el script se cierre si falla el internet

    def send(self, message: str, event: Events) -> None:
        # Si el evento no está en la lista o estamos en tiempo de bloqueo, no hacemos NADA
        if str(event) not in self.events or time.time() < self.bloqueo:
            return

        payload = {
            "content": dedent(message),
            "username": "miau",
            "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg"
        }

        # Enviamos en un hilo separado para que el minero siga sumando puntos
        threading.Thread(target=self._enviar, args=(payload,), daemon=True).start()
