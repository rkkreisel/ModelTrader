import statistics
from sys import exit as sysexit

from ib_insync import IB
from ib_insync.contract import ContFuture
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
        contract = self.get_contract()
        tradeContract = self.ib.qualifyContracts(contract.contract)[0]
        log.info("Got Trading Contract: {}".format(tradeContract.localSymbol))
        self.app.contract.update(tradeContract.localSymbol)

        bars = self.ib.reqHistoricalData(
            contract=contract.contract,
            endDateTime="",
            durationStr="1 D",
            barSizeSetting="15 mins",
            whatToShow="TRADES",
            useRTH=False,
            keepUpToDate=True
        )
        log.info("Got Historical Data Subscription")
        bars.updateEvent += self.app.barUpdateEvent

        ticks = self.ib.reqTickByTickData(
            contract=contract.contract,
            tickType="Last",
            numberOfTicks=0,
            ignoreSize=True
        )
        ticks.updateEvent += self.app.tickUpdateEvent

        log.info("Got Ticker Subscription")

    def get_contract(self):
        contract = self.ib.reqContractDetails(
            ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
        )
        if not contract:
            log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
            sysexit()
        else:
            return contract[0]


def calculate_cci(bars: BarDataList):
    cci = talib.CCI(
        np.array([bar.high for bar in bars]),
        np.array([bar.low for bar in bars]),
        np.array([bar.close for bar in bars]),
        timeperiod=config.CCI_PERIODS
    )

    average = statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 1):][:-1])
    return cci[-1], average
