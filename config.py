from datetime import datetime

from constants import MarketDataTypes

VERSION = "0.1"

LOGFILE = "modeltrader_{}.log".format(datetime.now().strftime('%Y%m%d_%H%M'))
LOGFILE_ENABLED = True

HOST = "127.0.0.1"
PORT = 55555
CLIENTID = 6

SYMBOL = "ES"
EXCHANGE = "GLOBEX"

# Type of Market Data To Stream.
DATATYPE = MarketDataTypes.LIVE



CCI_PERIODS = 34
CCI_AVERAGE_PERIODS = 8

ATR_PERIODS = 14

BBAND_PERIODS = 20
BBAND_STDDEV =2

SMA_PERIODS = 20