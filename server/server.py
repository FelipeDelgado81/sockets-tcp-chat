import socket

HOST = "127.0.0.1"
PORT = 5050
BUFFER_SIZE = 1024


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

        datos = cliente_socket.recv(BUFFER_SIZE)
        if datos:
            cliente_socket.send(datos)

        cliente_socket.close()


if __name__ == "__main__":
    iniciar_servidor()