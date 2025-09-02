

"""Cliente TCP interactivo para el chat básico.
- Se conecta a localhost:5000
- Envía múltiples mensajes, uno por línea
- Muestra el acuse de recibo del servidor
- Sale cuando el usuario escribe: "éxito" (o "exito", "exit", "salir")
"""

import socket

HOST = "127.0.0.1"
PORT = 5000
ENCODING = "utf-8"
EOL = "\n"

def should_exit(texto: str) -> bool:
    """Determina si el usuario quiere finalizar la sesión."""
    if texto is None:
        return True
    key = texto.strip().casefold()
    return key in {"éxito", "exito", "exit", "salir"}

def main():
    # Intentar conectar al servidor
    with socket.create_connection((HOST, PORT)) as sock:
        print(f"Conectado a {HOST}:{PORT}. Escribí mensajes. Para salir: 'éxito'")
        # Usamos file-like para line oriented I/O
        with sock.makefile("r", encoding=ENCODING, newline=EOL) as rfile, \
             sock.makefile("w", encoding=ENCODING, newline=EOL) as wfile:
            while True:
                try:
                    mensaje = input("> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nSaliendo...")
                    break
                if should_exit(mensaje):
                    print("Cerrando cliente..." )
                    break
                if not mensaje:
                    continue  # ignorar vacío

                # Enviar al servidor (una línea por mensaje)
                try:
                    wfile.write(mensaje + EOL)
                    wfile.flush()
                except BrokenPipeError:
                    print("Conexión rota al enviar. Saliendo...")
                    break

                # Leer respuesta del servidor
                respuesta = rfile.readline()
                if not respuesta:
                    print("Servidor cerró la conexión.")
                    break
                print(respuesta.strip())

if __name__ == "__main__":
    try:
        main()
    except ConnectionRefusedError:
        print("No se pudo conectar al servidor. ¿Está corriendo en localhost:5000?")
    except OSError as e:
        print(f"Error de socket: {e}")
