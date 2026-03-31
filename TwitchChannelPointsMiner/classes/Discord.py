import time
import requests
import threading
from textwrap import dedent
from TwitchChannelPointsMiner.classes.Settings import Events

class Discord(object):
    __slots__ = ["webhook_api", "webhook_error_api", "events"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        # Webhook secundario para alertas de estado y errores
        self.webhook_error_api = "https://discord.com/api/webhooks/1488486345046360185/5Ii1Lddtlb4J9sRnoLfHGt5XcOaOtdzfmi9-4CtqiD6gOxfYirS3wfw1jRPhd1yF7FOV"
        self.events = [str(e) for e in events]
        
        # Hilo de recordatorio cada 60 minutos en el log de Render
        threading.Thread(target=self._log_reminder, daemon=True).start()

    def _log_reminder(self):
        """Mantiene el log de Render con actividad cada hora"""
        while True:
            time.sleep(3600)
            print("[Render Log] Status Check: El minero y el sistema de alertas están operativos.")

    def _send_alert(self, content):
        """Envía notificaciones de estado al canal de errores"""
        try:
            payload = {
                "content": content,
                "username": "Monitor de Estado",
                "avatar_url": "https://i.imgur.com/8nS8vXo.png"
            }
            requests.post(url=self.webhook_error_api, json=payload, timeout=5)
        except:
            pass # No queremos que un error en la alerta detenga el minero

    def _async_send(self, payload):
        """Procesa el envío del webhook principal en segundo plano"""
        for intento in range(3):
            try:
                response = requests.post(url=self.webhook_api, json=payload, timeout=10)
                
                if response.status_code == 204:
                    break 

                if response.status_code == 429:
                    # Extraemos el tiempo de espera del header de Discord
                    espera_header = response.headers.get("Retry-After")
                    espera = float(espera_header) if espera_header else 5
                    
                    # Notificamos al canal secundario sobre el bloqueo
                    alerta = f"⚠️ **Rate Limit en Webhook Principal**\nReintentando envío en `{espera}` segundos."
                    self._send_alert(alerta)
                    
                    print(f"[Discord] Rate Limit: Esperando {espera}s...")
                    time.sleep(espera)
                    continue

                response.raise_for_status()
            except Exception as e:
                # Avisamos al canal secundario si hay un error crítico (ej. URL inválida)
                self._send_alert(f"❌ **Error en Webhook Principal**: `{str(e)}`")
                print(f"[Discord Error] {e}")
                break

    def send(self, message: str, event: Events) -> None:
        if str(event) not in self.events:
            return

        payload = {
            "content": dedent(message),
            "username": "miau",
            "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg?ex=675f44bc&is=675df33c&hm=c5b85b4773614e3ac51b4ed284b811fe637556655e30c36843a2bfaab63c883e&",
        }

        # Lanzar en hilo separado para que el minero nunca se detenga
        threading.Thread(target=self._async_send, args=(payload,), daemon=True).start()
