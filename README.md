# TP1-Intro-a-Distribuidos

## Instalar los requerimientos

```
> pip install -r python3

```
## Para levantar el servidor

```
> cd src/lib
> python start-server.py -h
usage: start-server [-h] [-v | -q] [-H ADDR] [-p PORT] [-s DIRPATH]
<command description > optional arguments:
-h, --help -v, --verbose -q, --quiet -H, --host -p, --port -s, --storage
show this help message and exit increase output verbosity decrease output verbosity service IP address
service port storage dir path

Por ejemplo:

> cd src/lib
> python3 start-server.py -H localhost -p 8080 -s destination
```

## Para cargar un archivo (cliente)

```
> cd src/lib
> python upload.py -h
usage: upload [-h] [-v | -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME] [-sr SELECT_REPEAT]
<command description > optional arguments:
-h, --help -v, --verbose -q, --quiet -H, --host -p, --port -s, --src
-n, --name, -sr, --sel_repeat
show this help message and exit increase output verbosity decrease output verbosity server IP address
server port source file path file name

Por ejemplo:   

> cd src/lib
> python3 upload.py -H localhost -p 12000 -s home/usuario1/Documents -n cancion.mp3 -sr True
> python3 upload.py -H localhost -p 12000 -s home/usuario1/Documents -n cancion.mp3 -sr False
```

## Para descargar un archivo (cliente)

```
> cd src/lib
> python download.py -h
usage: download [-h] [-v | -q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]
<command description > optional arguments:
-h, --help -v, --verbose -q, --quiet -H, --host -p, --port -d, --dst
-n, --name
show this help message and exit increase output verbosity decrease output verbosity server IP address
server port destination file path file name

Por ejemplo:

> cd src/lib
> python3 download.py -H localhost -p 12000 -d destination -n cancion.mp3 -sr True
> python3 download.py -H localhost -p 12000 -d destination -n cancion.mp3 -sr False
```
# Para ajustar la perdida de paquetes
```
$ comcast --packet_loss=10%

Alternativamente:

$ iptables -A INPUT -m statistic --mode random --probability 0.1 -j DROP
$ iptables -A OUTPUT -m statistic --mode random --probability 0.1 -j DROP
```
# Para reiniciar la perdida de paquetes
```
$ comcast --stop

Si se uso el metodo alternativo:

$ tc qdisc del dev eth0 root netem
```
