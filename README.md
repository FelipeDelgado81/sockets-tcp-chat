# Sistema de Consulta Remota y Comandos TCP

Un sistema cliente-servidor en Python implementado mediante programación de sockets TCP de bajo nivel (`socket`). Esta aplicación permite establecer una comunicación síncrona en tiempo real sobre la capa de transporte utilizando la familia de direcciones IPv4 (`AF_INET`) y sockets orientados a conexión por flujo de bytes (`SOCK_STREAM`).

---

##  Tabla de Contenidos
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Lenguaje y Bibliotecas](#lenguaje-y-bibliotecas)
- [Configuración de Red](#configuración-de-red)
- [Instrucciones de Ejecución](#instrucciones-de-ejecución)
- [Comandos Disponibles y Ejemplos de Ejecución](#comandos-disponibles-y-ejemplos-de-ejecución)
- [Manejo de Errores y Cierre de Conexiones](#manejo-de-errores-y-cierre-de-conexiones)

---

##  Arquitectura del Sistema

El proyecto está diseñado bajo el patrón **Cliente-Servidor (TCP/IP)**:

1. **Servidor TCP (`server.py`):**
   - Inicializa el socket servidor, realiza la asociación a la IP y puerto (`bind`), y se pone en estado de escucha (`listen`).
   - Bloquea la ejecución a la espera de peticiones de conexión entrantes (`accept`) completando el handshake TCP de 3 vías.
   - Procesa los comandos recibidos desde el cliente y envía respuestas estructuradas o contenido de archivos.
   - Maneja desconexiones tanto limpias como abruptas para mantener los recursos del sistema libres.

2. **Cliente TCP (`client.py`):**
   - Crea un socket cliente y se conecta a la dirección del servidor (`connect`).
   - Ofrece una interfaz interactiva por consola donde el usuario ingresa comandos.
   - Codifica las peticiones en UTF-8, las transmite al servidor y decodifica las respuestas recibidas.
   - Incorpora límites de tiempo de espera (*timeouts*) para prevenir bloqueos indefinidos.

---

##  Requisitos del Sistema

### Requisitos Mínimos de SO:
- **Sistema Operativo:** Windows 10/11, macOS 10.15+, o distribuciones de Linux (Ubuntu, Debian, Fedora, Arch, etc.).
- **Terminal/Consola:** Command Prompt, PowerShell, Terminal de macOS o Bash/Zsh.

### Entorno y Dependencias:
- **No requiere bibliotecas ni dependencias externas (0 paquetes `pip`).** Toda la funcionalidad opera utilizando exclusivamente componentes nativos del núcleo de Python.

---

##  Lenguaje y Versión Utilizada

- **Lenguaje:** Python
- **Versión Requerida:** Python **3.8** o superior (compatible con Python 3.9, 3.10, 3.11, 3.12+).

---

##  Bibliotecas Necesarias

El proyecto utiliza únicamente módulos de la **Biblioteca Estándar de Python**:

| Módulo | Propósito |
| :--- | :--- |
| `socket` | Creación, configuración, bind, listen, accept, connect, envío (`send`) y recepción (`recv`) de sockets TCP/IP. |
| `datetime` | Obtención y formato de la marca de fecha y hora actual del sistema del servidor. |
| `sys` | Gestión de comandos y terminación limpia de ejecución del sistema. |
| `time` | Cálculo de tiempos de ejecución y control de pausas/tiempos de respuesta. |
| `os` | Manejo seguro de rutas de archivos y comprobaciones en el sistema operativo. |

---

##  Configuración de Red (IP y Puerto)

Los parámetros de red por defecto están definidos al inicio de los archivos `server.py` y `client.py`:

- **Dirección IP Local:** `127.0.0.1` (Interfaz de Loopback / `localhost`).
- **Puerto de Comunicación:** `65432` *(Puerto no privilegiado > 1024, configurable según necesidades)*.
- **Protocolo de Transporte:** TCP (`AF_INET`, `SOCK_STREAM`).
- **Tamaño de Buffer:** `1024` bytes.

---

##  Instrucciones de Ejecución

Para iniciar la aplicación correctamente, **se deben abrir dos terminales independientes** y seguir el orden estricto de inicio (el servidor debe estar escuchando antes de que el cliente intente conectarse).

### Paso 1: Iniciar el Servidor TCP
Abre la **primera terminal** en la carpeta del proyecto y ejecuta:

```bash
python server.py
# o si los archivos están en carpetas separadas:
python server/server.py
```

*Salida esperada:*
```text
[INICIO] Servidor TCP listo y escuchando en 127.0.0.1:65432
[ESPERA] Esperando conexión entrante de algún cliente...
```

### Paso 2: Iniciar el Cliente TCP
Abre una **segunda terminal** independiente en la carpeta del proyecto y ejecuta:

```bash
python client.py
# o si los archivos están en carpetas separadas:
python client/client.py
```

*Salida esperada:*
```text
[CONECTANDO] Intentando conectar a 127.0.0.1:65432...
[CONEXION EXITOSA] Conectado con éxito al servidor en 127.0.0.1:65432
Instrucciones: Escribe un mensaje o usa los comandos disponibles.
```

---

##  Ejemplo Básico de Ejecución y Comandos

### Comandos Disponibles en el Cliente:

| Comando | Descripción |
| :--- | :--- |
| `/hora` | Solicita la fecha y hora actual del servidor. |
| `/salir` | Cierra de manera limpia la sesión actual y finaliza el cliente. |
| `/archivo <nombre.txt>` | El cliente envia el archivo al servidor. |

---

### Traza Simulada de Ejecución

####  Terminal 1 (Servidor TCP)
```text
[INICIO] Servidor TCP listo y escuchando en 127.0.0.1:65432
[ESPERA] Esperando conexión entrante de algún cliente...
[CONEXION] Cliente conectado exitosamente desde ('127.0.0.1', 54321)
[MENSAJE] ('127.0.0.1', 54321) -> /hora
[INFO] Cliente ('127.0.0.1', 54321) solicitó desconexión mediante EXIT.
[DESCONEXION] Socket y recursos del cliente ('127.0.0.1', 54321) liberados de forma segura.
[ESPERA] Esperando conexión entrante de algún cliente...
```

####  Terminal 2 (Cliente TCP)
```text
[CONECTANDO] Intentando conectar a 127.0.0.1:65432...
[CONEXION EXITOSA] Conectado con éxito al servidor en 127.0.0.1:65432

Tú: /hora
[SERVIDOR] Hora actual: 2026-08-31 12:49:15


Tú: EXIT
[SERVIDOR] Confirmando cierre de sesión... Bye!
[LIMPIEZA] Cerrando el socket del cliente...
[CLIENTE] Conexión y sesión finalizadas.
```

---

##  Manejo de Errores y Cierre de Conexiones

El sistema implementa captura explícita de excepciones del módulo `socket` y manejo estructurado de errores para asegurar el cierre limpio de recursos:

1. **`ConnectionRefusedError`:**
   - **Causa:** El cliente intenta conectarse antes de iniciar el servidor o cuando el puerto `65432` no está escuchando.
   - **Manejo:** El cliente informa que el servidor está inaccesible y termina ordenadamente sin colapsar la aplicación.

2. **`ConnectionResetError`:**
   - **Causa:** Cierre abrupto de la conexión por cualquiera de las partes (caída de red, cierre forzado de terminal o envío de segmento TCP `RST`).
   - **Manejo:** Tanto el cliente como el servidor detectan la pérdida de la conexión, liberan el socket correspondiente en el bloque `finally` y evitan errores en cascada.

3. **`KeyboardInterrupt` (`Ctrl + C`):**
   - **Causa:** El usuario interrumpe manualmente la ejecución en la terminal.
   - **Manejo:** Se captura la señal de interrupción, garantizando la ejecución de los bloques `finally` para cerrar el socket del cliente o el socket servidor (`servidor_socket.close()`) y liberar el puerto en el SO.

4. **Recepción de `b""` (0 Bytes / TCP FIN):**
   - **Causa:** Cierre normal y ordenado del socket opuesto.
   - **Manejo:** `recv()` retorna una cadena de bytes vacía `b""`, activando el protocolo de cierre ordenado en ambas partes.
