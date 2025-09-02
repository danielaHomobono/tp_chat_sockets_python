

"""Servidor TCP para chat básico con almacenamiento en SQLite.
- Escucha en localhost:5000
- Recibe mensajes de clientes (una línea por mensaje, UTF-8)
- Guarda: contenido, timestamp, ip_cliente
- Responde al cliente: "Mensaje recibido: <timestamp>"
"""

import socket
import threading
import sqlite3
from datetime import datetime
from contextlib import closing

# ============================
# Configuración del servidor
# ============================
HOST = "127.0.0.1"   
PORT = 5000           
BACKLOG = 8           
DB_PATH = "chat.db" 
ENCODING = "utf-8"  
EOL = "\n"       

# ==================================
# Base de datos: creación e inserción
# ==================================
def init_db(db_path: str) -> None:
    """Crea la tabla 'mensajes' si no existe."""
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    fecha_envio TEXT NOT NULL,
                    ip_cliente TEXT NOT NULL
                )
            """)
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"No se pudo inicializar la DB: {e}") from e

def insert_message(db_path: str, contenido: str, fecha_envio: str, ip_cliente: str) -> None:
    """Inserta un mensaje en la base de datos SQLite."""
    try:
        # Abrir conexión local por hilo; SQLite permite múltiples conexiones
        with sqlite3.connect(db_path, timeout=5) as conn:
            conn.execute(
                "INSERT INTO mensajes (contenido, fecha_envio, ip_cliente) VALUES (?, ?, ?)",
                (contenido, fecha_envio, ip_cliente),
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB] Error insertando mensaje: {e}")
        return False


# ============================
# Networking (socket TCP/IP)
# ============================
def init_server_socket(host: str, port: int, backlog: int) -> socket.socket:
    """Configura el socket servidor TCP/IP y lo deja en listen()."""
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reutilizar la dirección rápido si reiniciamos
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Enlazar y escuchar
        srv.bind((host, port))  
        srv.listen(backlog)
        return srv
    except OSError as e:
        # Típico: puerto ocupado
        raise RuntimeError(f"No se pudo iniciar el socket en {host}:{port}: {e}") from e

def handle_client(conn: socket.socket, addr, db_path: str) -> None:
    """Gestiona un cliente: lee líneas, guarda en DB y responde con acuse."""
    ip_cliente, _ = addr
    print(f"[+] Conexión desde {ip_cliente}")
    try:
        # Usé archivos de texto sobre el socket para leer/escribir por líneas
        with conn:
            # Makefile en modo binario con encoding soportado; newline controla el comportamiento
            with conn.makefile("r", encoding=ENCODING, newline=EOL) as rfile, \
                 conn.makefile("w", encoding=ENCODING, newline=EOL) as wfile:
                for line in rfile:
                    contenido = line.rstrip("\n\r")
                    if contenido == "":
                        # Ignorar líneas vacías
                        continue
                    timestamp = datetime.now().isoformat(timespec="seconds")
                    # Guardar en DB (cada hilo tiene su propia conexión)
                    ok = insert_message(db_path, contenido, timestamp, ip_cliente)
                    if ok:
                        respuesta = f"Mensaje recibido: {timestamp}"
                    else:
                        respuesta = f"Error: No se pudo guardar el mensaje en la base de datos."
                    wfile.write(respuesta + EOL)
                    wfile.flush()
    except (ConnectionResetError, BrokenPipeError):
        print(f"[-] Conexión perdida con {ip_cliente}")
    except Exception as e:
        print(f"[handler] Error con {ip_cliente}: {e}")
    finally:
        print(f"[.] Cliente desconectado: {ip_cliente}")


def serve_forever(server_sock: socket.socket, db_path: str) -> None:
    """Bucle principal de aceptación de clientes (un hilo por cliente)."""
    print(f"Servidor escuchando en {HOST}:{PORT} ... (Ctrl+C para salir)")
    try:
        while True:
            conn, addr = server_sock.accept()
            # Un hilo por cliente; marcamos daemon=True para permitir salida del main
            t = threading.Thread(target=handle_client, args=(conn, addr, db_path), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[!] Interrupción por teclado. Cerrando servidor..." )
    finally:
        try:
            server_sock.close()
        except Exception:
            pass
        print("[✓] Socket cerrado. Hasta luego.")


# ============
# Main script
# ============
if __name__ == "__main__":
    # Inicializar DB
    init_db(DB_PATH)
    # Inicializar socket del servidor
    srv = init_server_socket(HOST, PORT, BACKLOG)
    # Atender clientes
    serve_forever(srv, DB_PATH)
