import socket
import sys

# ==============================================================================
# CONFIGURACIÓN DEL CLIENTE
# ==============================================================================
HOST = "127.0.0.1"          # IP del servidor (loopback)
PORT = 5050                 # Puerto del servidor
BUFFER_SIZE = 1024          # Tamaño de buffer de recepción
TIMEOUT_SEGUNDOS = 15.0     # Tiempo límite de espera para respuestas del socket (segundos)


def iniciar_cliente():
    """
    Inicia el cliente TCP, establece conexión con el servidor,
    valida la entrada del usuario, impone timeouts y maneja
    excepciones de red de forma segura con bloque finally.
    """
    cliente_socket = None
    try:
        # socket(): Crear socket IPv4 (AF_INET) y TCP (SOCK_STREAM)
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # --------------------------------------------------------------
        # CASO DE ERROR 3 (CLIENTE): Configuración de límite de tiempo (Timeout)
        # --------------------------------------------------------------
        # Define un tiempo máximo de espera para connect(), recv(), send().
        # Si la red no responde en este lapso, Python arroja socket.timeout.
        cliente_socket.settimeout(TIMEOUT_SEGUNDOS)

        print(f"[CONECTANDO] Intentando conectar a {HOST}:{PORT}...")
        
        # connect(): Inicia el Handshake TCP (SYN -> SYN-ACK -> ACK)
        cliente_socket.connect((HOST, PORT))

    # --------------------------------------------------------------
    # CASO DE ERROR 1 (CLIENTE): Servidor apagado o puerto cerrado
    # --------------------------------------------------------------
    # Se genera ConnectionRefusedError cuando el host remoto existe,
    # pero no hay ningún proceso escuchando en ese puerto (el SO responde con RST).
    except ConnectionRefusedError:
        print(f"[ERROR CONEXION] No se pudo conectar a {HOST}:{PORT}. El servidor está apagado o el puerto está cerrado.")
        return

    # Excepción por agotamiento de tiempo de espera al intentar conectar
    except socket.timeout:
        print(f"[ERROR TIMEOUT] Tiempo agotado ({TIMEOUT_SEGUNDOS}s) intentando conectar con el servidor.")
        return

    # Excepción si la IP o Hostname no se pueden resolver en DNS / sistema local
    except socket.gaierror:
        print(f"[ERROR RED] No se pudo resolver la dirección host '{HOST}'. Verifique la dirección IP.")
        return

    # Errores del sistema operativo al gestionar sockets
    except OSError as e:
        print(f"[ERROR OS] Error de sistema operativo al intentar conectar: {e}")
        return

    # Captura general para otros errores no contemplados
    except Exception as e:
        print(f"[ERROR INESPERADO] Error al intentar conectar: {e}")
        return

    else:
        # El bloque 'else' se ejecuta ÚNICAMENTE si el bloque try no arrojó ninguna excepción
        print(f"[CONEXION EXITOSA] Conectado con éxito al servidor en {HOST}:{PORT}")
        print("Instrucciones: Escribe un mensaje o usa los comandos: /hora, /archivo <nombre.txt>, /salir\n")

    # Bucle interactivo de envío y recepción
    try:
        while True:
            try:
                # Lectura de la consola del usuario
                mensaje = input("Tú: ")
            except (KeyboardInterrupt, EOFError):
                print("\n[SALIDA] Interrupción detectada en consola (Ctrl+C / Ctrl+D). Cerrando sesión...")
                break

            # --------------------------------------------------------------
            # CASO DE ERROR 4 (CLIENTE): Validación previa al envío
            # --------------------------------------------------------------
            # Se limpia el mensaje de espacios y se evita enviar cadenas vacías al socket.
            mensaje_limpio = mensaje.strip()
            if not mensaje_limpio:
                print("[ADVERTENCIA] No se permiten mensajes vacíos. Por favor ingresa texto.")
                continue

            try:
                # send(): Envía los bytes codificados en UTF-8 a través del socket TCP
                cliente_socket.send(mensaje_limpio.encode("utf-8"))

                # --------------------------------------------------------------
                # CASO DE ERROR 2 Y 3 (CLIENTE): Caída de conexión y Timeout en recv()
                # --------------------------------------------------------------
                # recv() espera la respuesta del servidor.
                datos = cliente_socket.recv(BUFFER_SIZE)

                # Detección de cierre ordenado por parte del servidor (Segmento FIN -> 0 bytes)
                if not datos:
                    print("[INFO SERVIDOR] El servidor cerró la conexión ordenadamente (FIN recibido).")
                    break

                # Decodificación y visualización de la respuesta
                respuesta = datos.decode("utf-8", errors="replace")
                print(f"{respuesta}\n")

                # Si se envió el comando /salir, romper el bucle tras la respuesta del servidor
                if mensaje_limpio == "/salir":
                    break

            # AGOTAMIENTO DE TIEMPO: El servidor no respondió dentro del TIMEOUT_SEGUNDOS configurado
            except socket.timeout:
                print(f"[ERROR TIMEOUT] El servidor tardó más de {TIMEOUT_SEGUNDOS}s en responder.")

            # CAÍDA DE CONEXIÓN: El servidor o la red cayeron abruptamente mientras se transmitía
            except ConnectionResetError:
                print("[ERROR CONEXION] Se perdió la conexión con el servidor (ConnectionResetError / RST).")
                break

            # CAÑERÍA ROTA: Intentar enviar a un socket cerrado por el servidor
            except BrokenPipeError:
                print("[ERROR CONEXION] Cañería rota (BrokenPipeError). El servidor cerró el socket.")
                break

            # Errores generales de socket en transporte
            except socket.error as e:
                print(f"[ERROR SOCKET] Ocurrió un error en la transmisión de datos: {e}")
                break

            # Excepciones imprevistas en la sesión
            except Exception as e:
                print(f"[ERROR INESPERADO] Excepción no controlada durante el chat: {e}")
                break

    finally:
        # --------------------------------------------------------------
        # CASO DE ERROR 5 (CLIENTE): Cierre garantizado del socket cliente
        # --------------------------------------------------------------
        # Garantiza que el socket cliente se cierre en cualquier circunstancia (normal o falla).
        if cliente_socket:
            print("[LIMPIEZA] Cerrando el socket del cliente...")
            try:
                cliente_socket.close()
            except OSError as e:
                print(f"[ERROR] Error al cerrar socket cliente: {e}")
        print("[CLIENTE] Conexión y sesión finalizadas.")


if __name__ == "__main__":
    iniciar_cliente()

