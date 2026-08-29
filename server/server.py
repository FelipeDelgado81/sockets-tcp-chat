import socket
import datetime
import os
import sys
import errno

# ==============================================================================
# CONFIGURACIÓN DEL SERVIDOR
# ==============================================================================
HOST = "127.0.0.1"      # Loopback / Localhost
PORT = 5050             # Puerto de escucha del servidor
BUFFER_SIZE = 1024      # Tamaño máximo de buffer de lectura en bytes

# Directorio de archivos para la funcionalidad /archivo <nombre>
ARCHIVOS_DIR = os.path.join(os.path.dirname(__file__), "archivos")
os.makedirs(ARCHIVOS_DIR, exist_ok=True)


def procesar_mensaje(mensaje: str) -> str:
    """
    Valida el mensaje recibido y genera la respuesta correspondiente.
    Comandos disponibles:
      - /hora: Retorna la hora actual del servidor.
      - /archivo <nombre>: Retorna el contenido de un archivo de texto.
      - /salir: Solicita la desconexión del cliente.
    Maneja excepciones de I/O de archivos de manera segura.
    """
    mensaje = mensaje.strip()

    # Validación de mensaje vacío
    if not mensaje:
        return "[ERROR] Mensaje vacío no permitido."

    # Comando de salida
    if mensaje == "/salir":
        return "__CERRAR__"

    # Comando de hora actual
    if mensaje == "/hora":
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[SERVIDOR] Hora actual: {ahora}"

    # Comando de lectura de archivo
    if mensaje.startswith("/archivo"):
        partes = mensaje.split(maxsplit=1)
        if len(partes) < 2:
            return "[ERROR] Uso correcto: /archivo <nombre_archivo.txt>"
        
        nombre_archivo = partes[1].strip()
        ruta = os.path.join(ARCHIVOS_DIR, nombre_archivo)

        # Prevención básica de Path Traversal (evita accesos tipo ../../)
        if os.path.basename(ruta) != nombre_archivo:
            return "[ERROR] Nombre de archivo no válido por motivos de seguridad."

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            return f"[ARCHIVO: {nombre_archivo}]\n{contenido}"
        except FileNotFoundError:
            return f"[ERROR] El archivo '{nombre_archivo}' no existe en el servidor."
        except PermissionError:
            return f"[ERROR] Permisos insuficientes para leer '{nombre_archivo}'."
        except UnicodeDecodeError:
            return f"[ERROR] El archivo '{nombre_archivo}' no es una cadena de texto UTF-8 válida."
        except OSError as e:
            return f"[ERROR] Error de lectura de archivo en servidor: {e}"

    # Respuesta por defecto para mensajes comunes
    return f"[SERVIDOR] Recibido: {mensaje}"


def atender_cliente(cliente_socket: socket.socket, direccion: tuple):
    """
    Atiende la comunicación interactiva con un cliente conectado.
    Maneja desconexiones limpias (0 bytes / FIN) y desconexiones forzadas (ConnectionResetError / RST).
    """
    print(f"[CONEXION] Cliente conectado exitosamente desde {direccion}")
    try:
        while True:
            try:
                # --------------------------------------------------------------
                # CASO DE ERROR 1 (SERVIDOR): Desconexión ordenada vs forzada
                # --------------------------------------------------------------
                # recv() se bloquea esperando datos desde la capa de transporte TCP.
                datos = cliente_socket.recv(BUFFER_SIZE)

                # CIERRE ORDENADO: Cuando el cliente llama a socket.close(), TCP envía un paquete FIN.
                # En Python socket, la recepción de FIN se manifiesta cuando recv() retorna b"" (0 bytes).
                if not datos:
                    print(f"[INFO] El cliente {direccion} cerró la conexión ordenadamente (FIN recibido / 0 bytes).")
                    break

                mensaje = datos.decode("utf-8", errors="replace")
                print(f"[MENSAJE] {direccion} -> {mensaje}")

                # Procesar la lógica del mensaje
                respuesta = procesar_mensaje(mensaje)

                # Si el usuario solicitó /salir
                if respuesta == "__CERRAR__":
                    try:
                        cliente_socket.send("[SERVIDOR] Confirmando cierre de sesión... Bye!".encode("utf-8"))
                    except (ConnectionResetError, BrokenPipeError):
                        pass
                    print(f"[INFO] Cliente {direccion} solicitó desconexión mediante /salir.")
                    break

                # Envío de respuesta al cliente a través del socket TCP
                cliente_socket.send(respuesta.encode("utf-8"))

            # CAÍDA FORZADA: El cliente cerró la aplicación bruscamente (ej. mató el proceso, apagó el PC o cayó la red).
            # El SO del cliente responde con un paquete RST (Reset).
            except ConnectionResetError:
                print(f"[ADVERTENCIA] Conexión reiniciada abruptamente por el cliente {direccion} (ConnectionResetError / RST).")
                break

            # CAÑERÍA ROTA: Se intenta escribir en un socket que la otra parte ya cerró.
            except BrokenPipeError:
                print(f"[ADVERTENCIA] Cañería rota (BrokenPipeError) al intentar enviar a {direccion}. Socket cerrado.")
                break

            # Errores generales de socket
            except socket.error as e:
                print(f"[ERROR SOCKET] Error en la comunicación TCP con cliente {direccion}: {e}")
                break

            # Captura de seguridad para cualquier otra excepción no prevista
            except Exception as e:
                print(f"[ERROR INESPERADO] Error en procesamiento del cliente {direccion}: {e}")
                break

    finally:
        # --------------------------------------------------------------
        # CASO DE ERROR 4 (SERVIDOR): Cierre garantizado de socket cliente
        # --------------------------------------------------------------
        # El bloque 'finally' asegura que, sin importar la razón de salida (éxito o error),
        # los recursos del socket individual del cliente se liberen adecuadamente.
        try:
            cliente_socket.close()
        except OSError:
            pass
        print(f"[DESCONEXION] Socket y recursos del cliente {direccion} liberados de forma segura.\n")


def iniciar_servidor():
    """
    Inicializa el socket servidor, realiza bind(), listen() y bucle de aceptado.
    Maneja errores de puerto en uso (OSError) e interrupción por teclado (KeyboardInterrupt).
    """
    servidor_socket = None
    try:
        # socket(): Crear socket IPv4 (AF_INET) y TCP (SOCK_STREAM)
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # SO_REUSEADDR permite reutilizar la dirección/puerto inmediatamente tras reiniciar el servidor
        # (evita quedar bloqueado por el estado TIME_WAIT del protocolo TCP).
        servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # --------------------------------------------------------------
        # CASO DE ERROR 2 (SERVIDOR): Puerto ya en uso (OSError)
        # --------------------------------------------------------------
        # bind() asocia el socket a la IP y Puerto especificados.
        # Si otro proceso ya utiliza ese puerto, el SO rechaza la operación arrojando OSError.
        servidor_socket.bind((HOST, PORT))
        
        # listen(): Habilita el socket para recibir conexiones entrantes (cola de espera = 5)
        servidor_socket.listen(5)
        print(f"[INICIO] Servidor TCP listo y escuchando en {HOST}:{PORT}")

        # Bucle principal de aceptación de conexiones
        while True:
            print("[ESPERA] Esperando conexión entrante de algún cliente...")
            try:
                # accept() bloquea la ejecución hasta que se completa el Handshake TCP de 3 vías con un cliente
                cliente_socket, direccion = servidor_socket.accept()
                
                # Delegar la atención del cliente conectado
                atender_cliente(cliente_socket, direccion)

            # --------------------------------------------------------------
            # CASO DE ERROR 3 (SERVIDOR): Parada manual por consola (Ctrl+C)
            # --------------------------------------------------------------
            # Si el usuario presiona Ctrl+C mientras el servidor espera en accept(),
            # se eleva KeyboardInterrupt para ir al bloque de parada principal y cerrar todo ordenadamente.
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"[ERROR ACCEPT] Ocurrió un problema al aceptar la conexión: {e}")

    except OSError as e:
        # Captura específica si el puerto ya está en uso (WinError 10048 en Windows o EADDRINUSE en Linux)
        if e.errno == errno.EADDRINUSE or "10048" in str(e):
            print(f"[ERROR CRÍTICO] El puerto {PORT} ya está en uso por otra aplicación (Address already in use).")
        else:
            print(f"[ERROR OS] Error de sistema operativo al iniciar socket del servidor: {e}")

    except KeyboardInterrupt:
        print("\n[APAGADO] Servidor detenido manualmente desde consola (KeyboardInterrupt / Ctrl+C).")

    except Exception as e:
        print(f"[ERROR CRÍTICO] Excepción no controlada en el servidor: {e}")

    finally:
        # --------------------------------------------------------------
        # CASO DE ERROR 4 (SERVIDOR): Cierre garantizado del socket principal
        # --------------------------------------------------------------
        if servidor_socket:
            print("[LIMPIEZA] Cerrando el socket principal del servidor...")
            try:
                servidor_socket.close()
            except OSError as e:
                print(f"[ERROR] Error al cerrar socket principal: {e}")
        print("[SERVIDOR] Proceso del servidor finalizado correctamente.")


if __name__ == "__main__":
    iniciar_servidor()

