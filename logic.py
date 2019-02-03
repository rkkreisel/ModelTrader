from sys import exit as sysexit

from ib_insync import IB
from ib_insync.contract import ContFuture

import config
import logger

log = logger.getLogger()


class Algo():
    def __init__(self, ib: IB):
        self.ib = ib

    def run(self):
        """ Execute the algorithm """
        contract = self.get_contract()
        tradeContract = self.ib.qualifyContracts(contract.contract)[0]
        log.info("Got Trading Contract: {}".format(tradeContract.localSymbol))

    def get_contract(self):
        contract = self.ib.reqContractDetails(
            ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
        )
        if not contract:
            log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
            sysexit()
        else:
            return contract[0]
