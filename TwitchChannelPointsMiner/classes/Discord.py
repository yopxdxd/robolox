import time
import requests
import threading
from textwrap import dedent
from TwitchChannelPointsMiner.classes.Settings import Events

class Discord(object):
    __slots__ = ["webhook_api", "webhook_error_api", "events"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        # Webhook secundario para alertas de Rate Limit y errores
        self.webhook_error_api = "https://discord.com/api/webhooks/1488486345046360185/5Ii1Lddtlb4J9sRnoLfHGt5XcOaOtdzfmi9-4CtqiD6gOxfYirS3wfw1jRPhd1yF7FOV"
        self.events = [str(e) for e in events]
        
        # Iniciar el recordatorio de actividad en el log de Render
        threading.Thread(target=self._log_reminder, daemon=True).start()
        # Prueba inicial para confirmar que el webhook secundario funciona al arrancar
        self._send_alert("✅ **Sistema de Notificaciones Iniciado**: El minero está operativo.")

    def _log_reminder(self):
        """Mantiene el log de Render con actividad cada hora"""
        while True:
            time.sleep(3600)
            print("[Render Log] Status Check: El minero y el sistema de alertas siguen activos.")

    def _send_alert(self, content):
        """Envía notificaciones de estado al canal de errores (Webhook Secundario)"""
        if not self.webhook_error_api:
            return
        try:
            payload = {
                "content": content,
                "username": "Monitor de Estado",
                "avatar_url": "https://i.imgur.com/8nS8vXo.png"
            }
            # Usamos json= para asegurar compatibilidad con Discord
            requests.post(url=self.webhook_error_api, json=payload, timeout=5)
        except Exception as e:
            print(f"[Error Alerta] No se pudo enviar mensaje al webhook secundario: {e}")

    def _async_send(self, payload):
        """Procesa el envío del webhook principal en segundo plano sin detener el farmeo"""
        for intento in range(3):
            try:
                # IMPORTANTE: Usamos json= para evitar que Discord rechace la petición
                response = requests.post(url=self.webhook_api, json=payload, timeout=10)
                
                # Éxito: Discord devuelve 204 si el mensaje se envió bien
                if response.status_code == 204:
                    break 

                # Rate Limit Detectado (Error 429)
                if response.status_code == 429:
                    # Intentamos leer el tiempo de espera de las cabeceras (más fiable)
                    espera_header = response.headers.get("Retry-After")
                    espera = float(espera_header) if espera_header else 5
                    
                    # Avisamos al canal secundario sobre el bloqueo
                    alerta = f"⚠️ **Rate Limit en Webhook Principal**\nReintentando envío en `{espera}` segundos."
                    self._send_alert(alerta)
                    
                    print(f"[Discord] Rate Limit: Esperando {espera}s en segundo plano...")
                    time.sleep(espera)
                    continue

                # Si hay otro error (401, 404, etc), lanzamos excepción
                response.raise_for_status()
                
            except Exception as e:
                # Informamos del error crítico al canal secundario
                self._send_alert(f"❌ **Error Crítico en Webhook Principal**: `{str(e)}`")
                print(f"[Discord Error] {e}")
                break

    def send(self, message: str, event: Events) -> None:
        """Función principal llamada por el minero"""
        if str(event) not in self.events:
            return

        payload = {
            "content": dedent(message),
            "username": "miau",
            "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg",
        }

        # Ejecutamos el envío en un hilo nuevo (Thread)
        # Esto hace que 'send' termine en milisegundos y el minero siga trabajando
        threading.Thread(target=self._async_send, args=(payload,), daemon=True).start()
