# Chat TCP con sockets

Aplicacion cliente-servidor de chat con comandos

## Requisitos de instalacion

- Python 3.9 o superior

## Lenguaje y version

- Python 3.x

## Bibliotecas utilizadas

- `socket`, `datetime`, `os`, `errno` 

## Direccion IP y puerto

- IP: `127.0.0.1` (localhost)
- Puerto: `5050`

## Como iniciar el servidor

```bash
cd server
python3 server.py
```

## Como iniciar el cliente

```bash
cd client
python3 client.py
```

## Comandos disponibles

| Comando | Descripcion |
|---|---|
| `<texto libre>` | Envia un mensaje y el servidor responde con eco |
| `/hora` | Solicita la hora actual del servidor |
| `/archivo <nombre>` | Solicita el contenido de un archivo en `server/archivos/` (bloquea nombres con rutas, ej. `../`) |
| `/salir` | Cierra la conexion de forma ordenada |

## Ejemplo de ejecucion

**Terminal 1 (servidor):**
```
$ python3 server.py
[INICIO] Servidor TCP listo y escuchando en 127.0.0.1:5050
[ESPERA] Esperando conexion entrante de algun cliente
```

**Terminal 2 (cliente):**
```
$ python3 client.py
[CONECTANDO] Intentando conectar a 127.0.0.1:5050
[CONEXION EXITOSA] Conectado con exito al servidor en 127.0.0.1:5050
Tu: hola
[SERVIDOR] Recibido: hola

Tu: /hora
[SERVIDOR] Hora actual: 2026-08-29 20:25:16

Tu: /archivo saludo.txt
[ARCHIVO: saludo.txt]
Este es un archivo de prueba en el servidor

Tu: /salir
[SERVIDOR] Confirmando cierre de sesion... Bye!
```

## Ejecutar entre dos equipos distintos en la misma red

Por defecto el programa corre en `127.0.0.1` (localhost), solo dentro del mismo computador. Para usarlo entre dos equipos distintos conectados a la misma red:

1. **Elegir cual equipo sera el servidor.** Puede ser cualquiera de los dos; el otro sera el cliente

2. **En el equipo servidor**, obtener su IP local:
   - Windows: `ipconfig` → ver "Direccion IPv4"
   - macOS: `ipconfig getifaddr en0`
   - Linux: `hostname -I`

3. **En `server/server.py`** (equipo servidor), cambiar:
   ```python
   HOST = "127.0.0.1"
   ```
   por:
   ```python
   HOST = "0.0.0.0"
   ```
   Esto hace que el servidor escuche en todas sus interfaces de red, no solo en localhost

4. **En `client/client.py`** (equipo cliente), cambiar:
   ```python
   HOST = "127.0.0.1"
   ```
   por la IP real del equipo servidor obtenida en el paso 2:
   ```python
   HOST = "192.168.1.15"
   ```

5. **Firewall:** si el cliente no logra conectar, revisar que el firewall del equipo servidor no este bloqueando el puerto 5050 (en Windows, permitir Python en el Firewall de Windows Defender; en macOS, aceptar el aviso de conexiones entrantes al ejecutar el servidor)

## Notas de comportamiento

- El cliente tiene un timeout de 15 segundos esperando respuesta del servidor (`socket.timeout`)
- El servidor acepta hasta 5 conexiones en cola (`listen(5)`), pero atiende un cliente a la vez
- Si el puerto ya esta en uso, el servidor lo informa explicitamente en consola

