import time, requests, threading
from textwrap import dedent
from TwitchChannelPointsMiner.classes.Settings import Events

class Discord(object):
    __slots__ = ["webhook_api", "events", "bloqueo"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        self.events = [str(e) for e in events]
        self.bloqueo = 0
        # Hilo que revisa el estado del bloqueo cada 60 minutos
        threading.Thread(target=self._monitor_log, daemon=True).start()

    def _monitor_log(self):
        """Informa en el log de Render cada 60 minutos sobre el estado del Rate Limit"""
        while True:
            time.sleep(3600) # Espera 60 minutos
            ahora = time.time()
            if ahora < self.bloqueo:
                restante = int(self.bloqueo - ahora)
                print(f"[Render Log] Status: Rate Limit ACTIVO. Faltan {restante}s para desbloquear.")
            else:
                print("[Render Log] Status: Sistema de notificaciones OK (Sin bloqueos).")

    def _enviar(self, payload):
        try:
            resp = requests.post(self.webhook_api, json=payload, timeout=10)
            if resp.status_code == 429:
                espera = float(resp.headers.get("Retry-After", 10))
                self.bloqueo = time.time() + espera
                print(f"[Discord] ¡Rate Limit! Descartando mensajes por {espera}s.")
        except:
            pass

    def send(self, message: str, event: Events) -> None:
        # Descarte total de eventos no deseados o si estamos bloqueados
        if str(event) not in self.events or time.time() < self.bloqueo:
            return

        payload = {
            "content": dedent(message),
            "username": "miau",
            "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg"
        }

        threading.Thread(target=self._enviar, args=(payload,), daemon=True).start()
