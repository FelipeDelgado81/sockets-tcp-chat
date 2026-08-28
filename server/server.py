import socket
import datetime
import os

HOST = "127.0.0.1"
PORT = 5050
BUFFER_SIZE = 1024

ARCHIVOS_DIR = os.path.join(os.path.dirname(__file__), "archivos")
os.makedirs(ARCHIVOS_DIR, exist_ok=True)


def procesar_mensaje(mensaje: str) -> str:
    """
    Valida el mensaje recibido y genera la respuesta correspondiente.
    Soporta comandos: /hora, /archivo <nombre>, /salir
    """
    mensaje = mensaje.strip()

    if not mensaje:
        return "[ERROR] mensaje vacio no permitido"

    if mensaje == "/salir":
        return "__CERRAR__"

    if mensaje == "/hora":
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[SERVIDOR] hora actual: {ahora}"

    if mensaje.startswith("/archivo"):
        partes = mensaje.split(maxsplit=1)
        if len(partes) < 2:
            return "[ERROR] Uso: /archivo <nombre_archivo.txt>"
        nombre_archivo = partes[1].strip()
        ruta = os.path.join(ARCHIVOS_DIR, nombre_archivo)
        if not os.path.isfile(ruta):
            return f"[ERROR] el archivo '{nombre_archivo}' no existe en el servidor"
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        return f"[ARCHIVO:{nombre_archivo}]\n{contenido}"

    return f"[SERVIDOR] Recibido: {mensaje}"


def iniciar_servidor():
    # socket(): se crea el socket TCP
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind(): asocia el socket a la ip y puerto definido
    servidor_socket.bind((HOST, PORT))
    # listen(): pone el socket a esperar conexiones
    servidor_socket.listen(1)
    print(f"[INICIO] servidor escuchando en {HOST}:{PORT}")

    while True:
        print("[ESPERA] esperando conexion del cliente..")
        # accept(): espera una conexion y obtiene el socket y direccion del cliente
        cliente_socket, direccion = servidor_socket.accept()
        print(f"[CONEXION] cliente conectado desde {direccion}")

        atender_cliente(cliente_socket, direccion)

        cliente_socket.close()
        print(f"[DESCONEXION] conexion con {direccion} finalizada\n")


def atender_cliente(cliente_socket, direccion):
    while True:
        # recv(): recibe datos enviado por el cliente
        datos = cliente_socket.recv(BUFFER_SIZE)

        if not datos:
            print(f"[INFO] cliente {direccion} cerro la conexion")
            break

        mensaje = datos.decode("utf-8", errors="replace")
        print(f"[MENSAJE] {direccion} -> {mensaje}")

        respuesta = procesar_mensaje(mensaje)

        if respuesta == "__CERRAR__":
            # send(): envia un mensaje la cliente para confirmar el cierre
            cliente_socket.send("[SERVIDOR] cerrando conexion".encode("utf-8"))
            break

        # send(): envia la respuesta al cliente
        cliente_socket.send(respuesta.encode("utf-8"))


if __name__ == "__main__":
    iniciar_servidor()