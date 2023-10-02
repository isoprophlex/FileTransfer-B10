# FileTransfer-B10

Este trabajo práctico se plantea como objetivo la comprensión y la puesta en práctica de los conceptos y herramientas
necesarias para la implementación de un protocolo RDT. Para lograr este objetivo, se deberá desarrollar una aplicación
de arquitectura cliente-servidor que implemente la funcionalidad de transferencia de archivos mediante las siguientes
operaciones:

· *UPLOAD*: Transferencia de un archivo del cliente hacia el servidor

· *DOWNLOAD*: Transferencia de un archivo del servidor hacia el cliente

Dada las diferentes operaciones que pueden realizarse entre el cliente y el servidor, se requiere del diseño e implementación de un protocolo de aplicación básico que especifique los mensajes intercambiados entre los distintos procesos.

Participantes:
- Amigo, Nicolas
- Bravo, Nicolas
- Cuppari, Franco
- Ledesma, Dylan

# Ejemplo de Ejecucion
'''
# Seteo de perdida de paquetes con perdida 10%
comcast --packet-loss=10%

# Inicio de server en localhost
python start-server.py -H 127.0.0.1 -p 3000 -s CARPETA

# En otra consola inicio de clientes
python upload.py -H 127.0.0.1 -p 3000 -s FILEPATH -n FILENAME -sr true
python download.py -H 127.0.0.1 -p 3000 -s FILEPATH -n FILENAME -sr true
'''
