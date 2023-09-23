import logging


def get_logger(verbose, quiet):
    """Niveles de log
    Nivel por default: info
    Con verbose: debug
    Quiet: error

    Orden creciente: DEBUG, INFO, WARNING, ERROR. (muestra para la derecha desde el nivel en el que estoy)
    """
    if verbose:
        level = logging.INFO
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.WARNING
    logging.basicConfig(format="%(message)s", level=level)
    return logging.getLogger()