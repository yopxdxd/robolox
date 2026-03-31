import time, requests, threading
from textwrap import dedent
from TwitchChannelPointsMiner.classes.Settings import Events

class Discord(object):
    __slots__ = ["webhook_api", "events", "bloqueo"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        self.events = [str(e) for e in events]
        self.bloqueo = 0  # Tiempo hasta el cual no enviaremos nada

    def _enviar(self, payload):
        resp = requests.post(self.webhook_api, json=payload, timeout=10)
        if resp.status_code == 429:
            # Si Discord frena, guardamos el tiempo de espera y bloqueamos todo
            espera = float(resp.headers.get("Retry-After", 5))
            self.bloqueo = time.time() + espera
            print(f"[Discord] Bloqueado por {espera}s. Descartando mensajes...")

    def send(self, message: str, event: Events) -> None:
        # 1. Filtro de eventos y filtro de tiempo (descarte total si hay ratelimit)
        if str(event) not in self.events or time.time() < self.bloqueo:
            return

        # 2. Creamos el mensaje
        payload = {
            "content": dedent(message),
            "username": "miau",
            "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg"
        }

        # 3. Enviamos en segundo plano para no trabar el minero
        threading.Thread(target=self._enviar, args=(payload,), daemon=True).start()
