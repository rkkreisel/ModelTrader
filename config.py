from datetime import datetime

from constants import MarketDataTypes

VERSION = "0.1"

LOGFILE = "modeltrader_{}.log".format(datetime.now().strftime('%Y%m%d_%H%M'))
LOGFILE_ENABLED = False

HOST = "127.0.0.1"
PORT = 55555
CLIENTID = 4

SYMBOL = "ES"
EXCHANGE = "GLOBEX"

# Type of Market Data To Stream.
DATATYPE = MarketDataTypes.LIVE
