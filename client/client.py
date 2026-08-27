import socket

HOST = "127.0.0.1"  
PORT = 5050
BUFFER_SIZE = 1024


def iniciar_cliente():
    # socket(): crea el socket TCP del lado cliente
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect(): intenta conectarse al servidor mediante TCP
    cliente_socket.connect((HOST, PORT))
    print(f"[CONEXION] conectado al servidor {HOST}:{PORT}")

    mensaje = input("tu: ")
    cliente_socket.send(mensaje.encode("utf-8"))

    datos = cliente_socket.recv(BUFFER_SIZE)
    print(datos.decode("utf-8"))

    cliente_socket.close()


if __name__ == "__main__":
    iniciar_cliente()