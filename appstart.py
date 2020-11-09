"""
    ModelTrader Helper Functions
"""
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from re import compile as compile_re
from ib_insync.contract import Contract
import csv
import config
import os
import logger

log = logger.getLogger()

def justStartedAppDirectionCheck(self):
        log.debug("justStartedAppDirectionCheck: Application just restarted.  Going through our checks")
        # do we need to reverse positions?
        # first check to see if we have positions or open orders.  If not exit otherwise continue
        # Are we positioned in the wrong direction (i.e. long when we should be short?)  If so, we need to close STP and open open trades.
        # not going to take a position at this time.
        # the bars data is the current, not completed, bar so we have to go back to get closed bars.
        
        contContract, contracthours = logic.get_contract(self) #basic information on continuious contact
        tradeContract = self.ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
        open_long, open_short, long_position_qty, short_position_qty, account_qty = orders.countOpenPositions(self.ib,"")   # do we have an open position - not orders but positions?
        open_today, tradingDayRules = helpers.is_open_today(contracthours)
        wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d, self.log_time = self.define_times(self.ib)
        dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
        bars_15m = calculations.Calculations(self.ib, dataContract, "2 D", "15 mins", self.datetime_15, False, 0)
        #rint("bars15 cci_third, ccia_third, cci_prior, ccia_prior, cci, ccia",bars_15m.cci_third,bars_15m.ccia_third,bars_15m.cci_prior, bars_15m.ccia_prior, bars_15m.cci, bars_15m.ccia)
        if (bars_15m.cci_prior > bars_15m.ccia_prior and open_short) or (bars_15m.cci_prior < bars_15m.ccia_prior and open_long):
            log.debug("justStartedAppDirectionCheck: we are in app start up and we need to reverse due to wrong direction")
            allClosed = orders.closeOutMain(self.ib,tradeContract,True)     # we don't worry about whether we are long or short. just passing the contract, need to add order.  Second false is whether this is an opening order.  it is not
            log.debug("justStartedAppDirectionCheck: crossed but not tradeNow so lets close stp and open positions")
        else:
            log.debug("justStartedAppDirectionCheck: we are in app start up and we DO NOT need to reverse due to wrong direction")
        # now check if we should be pending on restart
        
        if (bars_15m.cci_four > bars_15m.ccia_four and bars_15m.cci_third < bars_15m.ccia_third and bars_15m.cci_prior < bars_15m.ccia_prior and \
        abs(bars_15m.cci_third - bars_15m.ccia_third) < config.SPREAD and abs(bars_15m.cci_prior - bars_15m.ccia_prior) < config.SPREAD) or \
        (bars_15m.cci_four < bars_15m.ccia_four and bars_15m.cci_third > bars_15m.ccia_third and bars_15m.cci_prior > bars_15m.ccia_prior and \
        abs(bars_15m.cci_third - bars_15m.ccia_third) < config.SPREAD and abs(bars_15m.cci_prior - bars_15m.ccia_prior) < config.SPREAD):
            log.debug("justStartedAppDirectionCheck: we are in a second leg pending situation on start up")
            if bars_15m.cci_prior > bars_15m.ccia_prior:
                return True, False, 2
            else:
                return False, True, 2
        elif (bars_15m.cci_third > bars_15m.ccia_third and bars_15m.cci_prior < bars_15m.ccia_prior and abs(bars_15m.cci_prior - bars_15m.ccia_prior) < config.SPREAD) or \
        (bars_15m.cci_third < bars_15m.ccia_third and bars_15m.cci_prior > bars_15m.ccia_prior and abs(bars_15m.cci_prior - bars_15m.ccia_prior) < config.SPREAD):
            log.debug("justStartedAppDirectionCheck: we are in a first leg pending situation on start up")
            if bars_15m.cci_prior > bars_15m.ccia_prior:
                return True, False, 1
            else:
                return False, True, 1
        else:
            log.debug("justStartedAppDirectionCheck: we are not in an exiting pending pattern")
            return False, False, 0