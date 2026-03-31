import time # Importante añadir esto arriba del archivo

def send(self, message: str, event: Events) -> None:
    if str(event) not in self.events:
        return

    payload = {
        "content": dedent(message),
        "username": "miau",
        "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg",
    }

    # Intentamos enviar hasta 3 veces si hay bloqueo por velocidad
    for intento in range(3):
        try:
            response = requests.post(url=self.webhook_api, json=payload, timeout=10)
            
            if response.status_code == 429:
                # Discord nos dice cuántos milisegundos esperar en el encabezado 'retry_after'
                espera = response.json().get("retry_after", 5000) / 1000
                print(f"[!] Rate Limit: Esperando {espera} segundos...")
                time.sleep(espera)
                continue # Reintenta el envío
                
            response.raise_for_status()
            break # Si salió bien (204), salimos del bucle
            
        except requests.exceptions.RequestException as e:
            print(f"[Discord Error] {e}")
            break
