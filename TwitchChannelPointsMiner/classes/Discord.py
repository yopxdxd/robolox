from textwrap import dedent
import requests
from TwitchChannelPointsMiner.classes.Settings import Events

class Discord(object):
    __slots__ = ["webhook_api", "events"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        self.events = [str(e) for e in events]

    def send(self, message: str, event: Events) -> None:
        if str(event) in self.events:
            # 1. Estructura del payload según la API actual de Discord
            payload = {
                "content": dedent(message),
                "username": "miau",
                "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg?ex=675f44bc&is=675df33c&hm=c5b85b4773614e3ac51b4ed284b811fe637556655e30c36843a2bfaab63c883e&",
            }
            
            try:
                # 2. Uso estricto de json= y timeout para evitar cuelgues del minero
                response = requests.post(
                    url=self.webhook_api, 
                    json=payload, 
                    timeout=10
                )
                
                # 3. Fuerza a que cualquier código de error (4xx o 5xx) lance una excepción visible
                response.raise_for_status()
                
            except requests.exceptions.HTTPError as errh:
                # Error de Discord (ej. Webhook borrado, Rate Limit, etc.)
                print(f"[Discord Webhook] Error HTTP: {errh}")
                if response.status_code == 429:
                    print("[Discord Webhook] Advertencia: Discord está limitando la velocidad de los mensajes.")
            except requests.exceptions.RequestException as err:
                # Error general de red (tu internet o caída de Discord)
                print(f"[Discord Webhook] Error de conexión: {err}")
