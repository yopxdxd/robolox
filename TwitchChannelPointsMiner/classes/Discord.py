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
                
                # 1. Éxito
                if response.status_code == 204:
                    # Opcional: Ver cuántas peticiones te quedan
                    # print(f"Peticiones restantes: {response.headers.get('x-ratelimit-remaining')}")
                    break 

                # 2. Rate Limit (Error 429)
                if response.status_code == 429:
                    # LEER DIRECTO DE LAS CABECERAS (Más seguro que el JSON)
                    espera_header = response.headers.get("Retry-After")
                    
                    if espera_header:
                        espera = float(espera_header)
                    else:
                        # Si no está en el header, intentamos el JSON como última opción
                        try:
                            espera = response.json().get("retry_after", 5000) / 1000
                        except:
                            espera = 5
                    
                    print(f"--- BLOQUEO DE DISCORD ---")
                    print(f"Tiempo de espera restante: {espera} segundos")
                    print(f"ID del Webhook: {response.headers.get('x-ratelimit-bucket')}")
                    print(f"--------------------------")
                    
                    time.sleep(espera)
                    continue

                response.raise_for_status()
                
            except Exception as e:
                print(f"[Discord Error] {e}")
                break
