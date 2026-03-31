import time
import requests
from textwrap import dedent
from TwitchChannelPointsMiner.classes.Settings import Events

class Discord(object):
    __slots__ = ["webhook_api", "events"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        self.events = [str(e) for e in events]

    def send(self, message: str, event: Events) -> None:
        if str(event) not in self.events:
            return

        payload = {
            "content": dedent(message),
            "username": "miau",
            "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg",
        }

        for intento in range(3):
            try:
                response = requests.post(url=self.webhook_api, json=payload, timeout=10)
                
                if response.status_code == 204:
                    break 

                if response.status_code == 429:
                    data = response.json()
                    espera = data.get("retry_after", 5)
                    print(f"[Discord] Rate Limit: Esperando {espera} segundos...")
                    time.sleep(espera)
                    continue

                response.raise_for_status()
            except Exception as e:
                print(f"[Discord Error] {e}")
                break
