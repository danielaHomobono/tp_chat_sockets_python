
TP: Chat Básico Cliente-Servidor con Sockets y SQLite
====================================================

Contenido:
- servidor.py  : servidor TCP concurrente (hilos) que guarda mensajes en SQLite y responde acuses.
- cliente.py   : cliente interactivo que envía múltiples mensajes hasta escribir 'éxito' (o variantes).
- README.md    : este archivo.
- NOTES.txt    : recomendaciones de pruebas y seguridad.

Instrucciones rápidas:
1) Abrí una terminal y ejecutá el servidor:
   python servidor.py
2) En otra terminal ejecutá el cliente:
   python cliente.py
3) Escribí mensajes y verás las respuestas del servidor. Para salir del cliente: 'éxito', 'exito', 'exit' o 'salir'.

DB:
- Se crea automáticamente `chat.db` en la misma carpeta cuando se inicia el servidor.
- Ver la tabla `mensajes` con: sqlite3 chat.db "SELECT * FROM mensajes;"

Notas de diseño (resumen):
- Un hilo por cliente (daemon threads) para atender múltiples clientes.
- Cada handler abre su propia conexión SQLite (para evitar compartir conexiones entre hilos).
- Protocolo: line-oriented UTF-8 text (una línea = un mensaje).
- Manejo de errores y cierres prolijos.
