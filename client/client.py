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
    print("escribe un mensaje, o usa /hora, /archivo <nombre>, /salir\n")

    while True:
        mensaje = input("tu: ")

        # send(): envía el mensaje del usuario al servidor
        cliente_socket.send(mensaje.encode("utf-8"))

        # recv(): espera y recibe la respuesta del servidor
        datos = cliente_socket.recv(BUFFER_SIZE)
        if not datos:
            print("[INFO] el servidor cerro la conexion")
            break

        respuesta = datos.decode("utf-8", errors="replace")
        print(respuesta)

        if mensaje.strip() == "/salir":
            break

    cliente_socket.close()


if __name__ == "__main__":
    iniciar_cliente()