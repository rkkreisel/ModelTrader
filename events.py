from logger import getLogger

log = getLogger()


def registerEvents(ib):
    ib.connectedEvent += connectEvent
    ib.disconnectedEvent += disconnectedEvent


def connectEvent():
    log.info("Connected.")


def disconnectedEvent():
    log.info("Disconnected from TWS.")
