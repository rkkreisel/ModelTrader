import statistics
from sys import exit as sysexit

from ib_insync import IB
from ib_insync.contract import ContFuture, Contract
from ib_insync.objects import BarDataList
import talib
import numpy as np

import config
import logger

log = logger.getLogger()


class Algo():
    def __init__(self, ib: IB, app):
        self.ib = ib
        self.app = app

    def run(self):
        """ Execute the algorithm """
        contContract = get_contract(self)
        dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
        log.info("Got Contract: {}".format(dataContract.localSymbol))
        self.app.contract.update(dataContract.localSymbol)

        # 15 Minute Data
        bars_15m = self.get_bars_15m(dataContract)
        self.app. barupdateEvent_15m(bars_15m, True)
        bars_15m.updateEvent += self.app.barupdateEvent_15m
        log.info("Got 15m data subscription")



    def get_bars_15m(self, contract):
        return self.ib.reqHistoricalData(
            contract=contract,
            endDateTime="",
            durationStr="2 D",
            barSizeSetting="15 mins",
            whatToShow="TRADES",
            useRTH=False,
            keepUpToDate=True
        )

def calculate_cci(bars: BarDataList):
    cci = talib.CCI(
        np.array([bar.high for bar in bars]),
        np.array([bar.low for bar in bars]),
        np.array([bar.close for bar in bars]),
        timeperiod=config.CCI_PERIODS
    )

    average = statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 1):][:-1])
    return cci[-1], average

def calculate_atr(bars):
    atr =  talib.ATR(
        np.array([bar.high for bar in bars]),
        np.array([bar.low for bar in bars]),
        np.array([bar.close for bar in bars]),
        timeperiod=config.ATR_PERIODS
    )
    return atr[-1]

def calculate_bbands(bars):
    up, mid, low = talib.BBANDS(
        np.array([bar.close for bar in bars]),
        timeperiod=config.BBAND_PERIODS,
        nbdevup=config.BBAND_STDDEV,
        nbdevdn=config.BBAND_STDDEV,
        matype=talib.MA_Type.WMA # Wilder Moving Average
    )
    sma = talib.SMA(np.array([bar.close for bar in bars]), timeperiod=config.SMA_PERIODS)
    width = (up[-1] - low[-1]) / sma[-1]
    percentb = (bars[-1].close - low[-1]) / (up[-1] - low[-1])
    return width, percentb

def get_contract(client):
    contract = client.ib.reqContractDetails(
        ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
    )
    if not contract:
        log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
        sysexit()
    return contract[0].contract


