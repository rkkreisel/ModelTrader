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
        contContract = self.get_contract()
        dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
        log.info("Got Contract: {}".format(dataContract.localSymbol))
        self.app.contract.update(dataContract.localSymbol)

        bars = self.ib.reqHistoricalData(
            contract=dataContract,
            endDateTime="",
            durationStr="1 D",
            barSizeSetting="15 mins",
            whatToShow="TRADES",
            useRTH=False,
            keepUpToDate=True
        )
        print(bars)
        log.info("Got Historical Data Subscription")
        self.app.barUpdateEvent(bars, True)
        bars.updateEvent += self.app.barUpdateEvent

    def get_contract(self):
        contract = self.ib.reqContractDetails(
            ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
        )
        if not contract:
            log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
            sysexit()
        return contract[0].contract


def calculate_cci(bars: BarDataList):
    cci = talib.CCI(
        np.array([bar.high for bar in bars]),
        np.array([bar.low for bar in bars]),
        np.array([bar.close for bar in bars]),
        timeperiod=config.CCI_PERIODS
    )

    average = statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 1):][:-1])
    return cci[-1], average
