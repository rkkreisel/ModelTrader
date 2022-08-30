from datetime import datetime
from constants import MarketDataTypes

VERSION = "0.1"

LOGFILE = "log/modeltrader_{}.log".format(datetime.now().strftime('%Y%m%d_%H%M'))
LOGFILE_ENABLED = True

HOST = "127.0.0.1"
PORT = 55555
CLIENTID = 0

SYMBOL = "ES"
EXCHANGE = "GLOBEX"

# Type of Market Data To Stream.
DATATYPE = MarketDataTypes.LIVE

NORMAL_TRADING_HOURS = "1700-1515,1530-1600"
DAY_TRADING_HOURS = "0930"
NIGHT_TRADING_HOURS = "1500"    # 1 hour prior to day close.  DOn't want to start position 1 hour prior to close if not night trader

CCI_PERIODS = 34
CCI_AVERAGE_PERIODS = 8

ATR_PERIODS = 14

BBAND_PERIODS = 20
BBAND_STDDEV =2

SMA_PERIODS = 20

SPREAD = 15
SPREAD_COUNT = 3

ATR_STOP_MIN = 5

hostname = 'localhost'
username = 'postgres'
password = 'rkk7879'
database = 'ModelTrader'

fact_15min = 'fifteenmin'
fact_hourly = 'hourly'
fact_daily = 'daily'
dim_15min = 'fifteenmindim'
dim_hourly = 'hourlydim'
dim_daily = 'dailydim'