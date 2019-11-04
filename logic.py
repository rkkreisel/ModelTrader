import statistics
from sys import exit as sysexit

from ib_insync import IB
from ib_insync.contract import ContFuture, Contract 
from ib_insync.objects import BarDataList
import talib
import numpy as np
from datetime import datetime, timedelta
import config
import logger
import csv
import categories
import helpers
import orders
import calculations

log = logger.getLogger()

class Algo():
    def __init__(self, ib: IB, app, backTest, backTestStartDateTime):
        self.ib = ib
        self.app = app
        self.backTest = backTest
        self.backTestStartDateTime = backTestStartDateTime

    def run(self):
        """ Execute the algorithm """
        # check for command line arguments
        # key_arr = ['blank','ATR15','ATR1','ATRD','CCI15','CCIA15','CCIA1h','CCIA1d','BBW15','BBb15','BBW1h','BBb1h','BBW1d','BBb1d']
        tradeNow, not_finished, pendingShort, pendingLong, pendingSkip, cci_trade, ccibb_trade, crossed = False, True, False, False, False, False, False, False
        pendingCnt = 0
        # any variable that is used within the class will be defined with self
        while not_finished:
            print ("top of algo run self*************************************************")
            if not self.backTest:
                stpSell, stpBuy = orders.findOpenOrders(self.ib,False) # don't want to execute covering
                log.info("we have the follow number of open stp orders for Sell: {sell} and Buy: {buy} ".format(sell=stpSell, buy=stpBuy))
                #top of logic - want to check status as we enter a new bar/hour/day/contract
            contContract, contracthours = get_contract(self) #basic information on continuious contact
            tradeContract = self.ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
            open_long, open_short, long_position_qty, short_position_qty = self.have_position(self.ib.positions())   # do we have an open position?
            open_today = helpers.is_open_today(contracthours)
            dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
            log.debug("Got Contract: {}".format(dataContract.localSymbol))
            self.app.contract.update(dataContract.localSymbol)
            wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d, self.log_time = self.define_times()
            log.debug("next datetime for 15 minutes - should be 15 minutes ahead of desired nextqtr{}".format(wait_time))
            #
            # debug 
            #current_time = datetime.now()
            #wait_time = wait_time = current_time.replace(minute = 1,second=0)
            #
            self.ib.waitUntil(wait_time)
            log.debug("requesting info for the following timeframe today: {} ".format(wait_time))
            bars_15m = calculations.Calculations(self.ib, dataContract, "2 D", "15 mins", self.datetime_15)
            bars_1h = calculations.Calculations(self.ib, dataContract, "5 D", "1 hour", self.datetime_1h)
            bars_1d = calculations.Calculations(self.ib, dataContract, "75 D", "1 day", self.datetime_1d)
            pendingLong, pendingShort, pendingCnt, pendingSkip, tradeNow, tradeAction, crossed = self.crossoverPending(bars_15m,pendingLong,pendingShort,pendingSkip,pendingCnt)
            cci_key, ccibb_key, summ_key = build_key_array(tradeAction, bars_15m, bars_1h, bars_1d)
            setsum = self.setupsummary(summ_key)
            log.info("tradeNow: {trade} pendingSkip {skip}".format(trade = tradeNow, skip = pendingSkip))
            print("going into tradenow, backtest, open long and short",tradeNow, self.backTest, open_short,open_long)
            if crossed and (open_long or open_short) and not tradeNow:    # need to close stp and open positions
                allClosed = orders.closeOutSTPandPosition(self.ib,tradeContract)
                log.info("crossed but not tradeNow so lets close stp and open positions")
            if tradeNow:
                if tradeAction == "BUY" and open_short and not self.backTest:
                    #quantity = 2
                    MarketOrderId = orders.coverOrders(self.ib,tradeContract,"BUY",short_position_qty,"cci_day")
                    open_short = False
                elif tradeAction == "SELL" and open_long and not self.backTest:
                    #quantity = 2
                    MarketOrderId = orders.coverOrders(self.ib,tradeContract,"SELL",long_position_qty,"cci_day")
                    open_long = False
                log.info("tradeNow - Tradeing this bar {cci} - {ccibb}".format(cci=cci_key,ccibb=ccibb_key))
                csv_file1 = csv.reader(open('data/ccibb.csv', "rt"), delimiter = ",")
                #cci_key, ccibb_key = build_key_array(self, tradeAction, bars_15m, bars_1h, bars_1d)
                for row1 in csv_file1:
                    #print("ccibb row: ",row1[0],row1[13])
                    if ccibb_key == row1[0] and row1[13] == "Y": #13 is winrisk - whether we trade or not
                        log.info("we have a match in ccibb.csv")
                        log.info("found a match in CCIBB ".format(str(row1[0])))
                        ccibb_trade = True
                        quantity = 2
                        # do we need to close out current order
                        # do we need to close out current stop loss orders?
                        if not backTest:
                            MarketOrderId, StopLossId, ParentOrderID = orders.buildOrders(self.ib,tradeContract,tradeAction,quantity,"ccibb_day",bars_15m.stoplossprice)
                            log.info("order placed, parentID: {}".format(ParentOrderID))
                        open_long, open_short, tradenow = False, False, False
                        status_done = self.row_results(row1,cci_trade,ccibb_trade)
                        break
                    elif ccibb_key == row1[0] and row1[13] == "N":
                        log.info("Entry found in CCIBB but not traded.  See if this changes")
                        ccibb_trade = False
                csv_file2 = csv.reader(open('data/cci.csv', "rt"), delimiter = ",")
                for row2 in csv_file2:
                    #print("cci   row: ",row2[0],row2[13])
                    if cci_key == row2[0] and row2[13] == "Y":
                        log.info("we have a match in cci.csv - tradeAction".format(tradeAction))
                        #log.info("found a match in CCI {}".format(str(row2[0])))
                        cci_trade = True
                        quantity = 2
                        if not self.backTest:
                            MarketOrderId, StopLossId, ParentOrderID = orders.buildOrders(self.ib,tradeContract,tradeAction,quantity,"cci_day",bars_15m.stoplossprice)
                        open_long, open_short, tradenow = False, False, False
                        status_done = self.row_results(row2,cci_trade,ccibb_trade)
                        break
                    elif cci_key == row2[0] and row2[13] == "N":
                        log.info("Entry found in CCI but not traded.  See if this changes")
                        cci_trade = True
                if tradeNow:
                    log.info("we did not find a match in either CCI or CCI BB")
            #csv_row_add = helpers.build_csv_bars_row(","+(''.join(key_arr))+","+(''.join(key_arr[0:8]))+","+str(cci_trade)+","+str(ccibb_trade)+","+str(pendingLong)+","+str(pendingShort),True)
            wrote_bar_to_csv = helpers.build_csv_bars_row(self.log_time, tradeAction, bars_15m, bars_1h, bars_1d, pendingLong, pendingShort, pendingCnt, tradeNow, ccibb_trade, cci_trade,ccibb_key, cci_key)
            tradenow, cci_trade, ccibb_trade = False, False, False

    def define_times(self):
        if self.backTest:   # added for backtest
            current_time = self.backTestStartDateTime
            current_minute = self.backTestStartDateTime.minute
            self.backTestStartDateTime = current_time + timedelta(minutes=15)
            print("current time, backteststartdatetime",current_time,self.backTestStartDateTime)
        else:    
            current_time = datetime.now()
            current_minute = datetime.now().minute
        #print("now ",current_time)
        #print("minute ",current_minute)
        if current_minute < 15:
            wait_time = current_time.replace(minute = 15,second=0) 
            self.datetime_15 = current_time.replace(minute = 30, second = 0)
        elif current_minute < 30:
            wait_time = current_time.replace(minute = 30,second=0) 
            self.datetime_15 = current_time.replace(minute = 45, second=0)
        elif current_minute < 45:
            wait_time = current_time.replace(minute = 45,second=0) 
            self.datetime_15 = current_time + timedelta(minutes=(45-current_minute+15))
            self.datetime_15 =self.datetime_15.replace(second=0)
        else:
            wait_time = current_time + timedelta(minutes=(60-current_minute))
            wait_time = wait_time.replace(second=0)
            self.datetime_15 = current_time + timedelta(minutes=(60-current_minute+15))
            self.datetime_15 =self.datetime_15.replace(second=0)
        if self.backTest:    #added for backtest
            wait_time = datetime.now() + timedelta(seconds=3)
            self.log_time = self.backTestStartDateTime
        else:
            self.log_time = wait_time
        print("wait time -> ",wait_time)
        self.datetime_1h = self.log_time.replace(minute=0)
        self.datetime_1d = current_time -  timedelta(days = 1)
        self.datetime_1d =self.datetime_1d.replace(hour = 0, minute=0, second=0)
        return wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d,self.log_time

    def row_results(self, row, cci_trade, ccibb_trade):
        log.info("************************************************")
        log.info("* CCI Trade:          {}".format(cci_trade))
        log.info("* CCIbb Trade:        {}".format(ccibb_trade))
        log.info("* Do we buy this one: {}".format(row[13]))
        log.info("* Profit:             {}".format(row[5]))
        log.info("* Winning %:          {}%".format(row[11]))
        log.info("* Risk:               {}%".format(row[12]))
        log.info("* Previous Order:     {}".format(row[6]))
        log.info("* Previous Wins:      {}".format(row[7]))
        log.info("* Rank (0-100)s:      {}".format(row[31]))
        log.info("************************************************")
        return

    def have_position(self,positions):
        position_long_tf = False
        position_short_tf = False
        x = 0
        long_position_qty, short_position_qty = 0, 0
        print("positions --> ",positions)
        while x < len(positions):
            if (positions[x][1].symbol) == "ES":
                if positions[x][2] > 0:
                    long_position_qty += positions[x][2]
                    position_long_tf = True
                elif positions[x][2] < 0:
                    short_position_qty += positions[x][2]
                    position_short_tf = True
            x += + 1
        log.info("Have a position: long qty: {lqty} and short qty: {sqty} ".format(lqty = long_position_qty,sqty = short_position_qty))    
        return position_long_tf, position_short_tf, long_position_qty, short_position_qty 

    def setupsummary(self,summ_key):
        csv_file3 = csv.reader(open('data/setupsummary.csv', "rt"), delimiter = ",")
        log.debug("key setupsummary: ".format(summ_key))
        for row3 in csv_file3:
            #print("setupsummary   row: ",row3[4])
            if summ_key == row3[4]:
                log.info("++++++++++++++++++++++++++++++++++++")
                log.info("join key:     {}".format(summ_key))
                log.info("CCI Long %  : {}".format(row3[7]))
                log.info("CCI Profit  : {}".format(row3[9]))
                log.info("CCI Win%    : {}".format(row3[12]))
                log.info("CCIbb Long %: {}".format(row3[15]))
                log.info("CCIbb Profit: {}".format(row3[17]))
                log.info("CCIbb Win%  : {}".format(row3[20]))
                log.info("Rank (0-100): {}".format(row3[21]))
                log.info("-------------------------------------")
                break
        return

    def crossoverPending(self, bars_15m, pendingLong, pendingShort, pendingSkip, pendingCnt):   # this is from excel macro.  Changes here should be changed there as well.
        tradeNow, crossed = False, False
        tradeAction = "CASH"
        if (bars_15m.cci < bars_15m.ccia and bars_15m.cci_prior > bars_15m.ccia_prior) or \
                (bars_15m.cci > bars_15m.ccia and bars_15m.cci_prior < bars_15m.ccia_prior):
                crossed = True
                log.info("We have crossed ----------^v")
                if abs(bars_15m.cci - bars_15m.ccia) > config.SPREAD:
                    log.info("crossed and outside spread")
                    tradeNow = True
                    tradeAction = "BUY"
                    if bars_15m.cci < bars_15m.ccia:
                        tradeAction = "SELL"
                else:
                    if bars_15m.cci < bars_15m.ccia:
                        pendingShort, pendingLong = True, False
                    else:
                        pendingShort, pendingLong = False, True   
                    pendingCnt = 0
                    pendingSkip = True
                    log.info("crossed but not meet spread requirement, pendingSkip: {skip}, pendingCnt: {cnt}".format(skip = pendingSkip, cnt = pendingCnt))
        log.info("crossed {cross}, pendingSkip: {skip}, pendingCnt: {cnt}".format(cross=crossed, skip = pendingSkip, cnt = pendingCnt))
        # deal with existing pending
        if pendingLong and pendingCnt < config.SPREAD_COUNT and bars_15m.cci - bars_15m.ccia > config.SPREAD:
            log.info("pending long cnt < 3 and > spread")
            pendingLong, pendingSkip, tradeNow = False, False, True
            pendingCnt = 0
        elif pendingShort and pendingCnt < config.SPREAD_COUNT and abs(bars_15m.cci - bars_15m.ccia) > config.SPREAD:
            log.info("pending short cnt < 3 and > spread")
            pendingShort, pendingSkip, tradeNow = False, False, True
            pendingCnt = 0
        elif (pendingLong or pendingShort) and pendingCnt == config.SPREAD_COUNT:
            print("pending long or short and cnt = 3 stop pending ",pendingCnt, config.SPREAD_COUNT)
            pendingLong, pendingShort, pendingSkip, tradeNow = False, False, False, True
            pendingCnt = 0
        elif pendingLong or pendingShort:
            pendingCnt += 1
            log.info("pending continues cnt: {cnt}".format(cnt = pendingCnt))
        print("check post cross and we have tradeNow, tradeAction, pendingLong, pendingShort, pendingSkip, pendingCnt",tradeNow, tradeAction, pendingLong, pendingShort, pendingSkip, pendingCnt)
        return pendingLong, pendingShort, pendingCnt, pendingSkip, tradeNow, tradeAction, crossed
        
def get_contract(client):
    contract = client.ib.reqContractDetails(
        ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
    )
    if not contract:
        log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
        sysexit()
    return contract[0].contract, contract[0].tradingHours

def build_key_array(tradeAction, bars_15m, bars_1h, bars_1d):
    #These has to be in sequential order since insert adds rather than replace.
    cci_key = "long"
    if tradeAction == "SELL":
        cci_key = "short"
    #key_arr.append[1,"test"] 
    cci_key += categories.categorize_atr15(bars_15m.atr) + categories.categorize_atr1h(bars_1h.atr) + categories.categorize_atr1d(bars_1d.atr) + \
        categories.categorize_cci_15(bars_15m.cci) + categories.categorize_cci_15_avg(bars_15m.ccia) + categories.categorize_cci_1h(bars_1h.ccia) + \
        categories.categorize_cci_1d(bars_1d.ccia)
    ccibb_key = cci_key + categories.categorize_BBW15(bars_15m.bband_width) + categories.categorize_BBb15(bars_15m.bband_b) + categories.categorize_BBW1h(bars_1h.bband_width) + \
        categories.categorize_BBb1h(bars_1h.bband_b) + categories.categorize_BBW1d(bars_1d.bband_width) + categories.categorize_BBb1d(bars_1d.bband_b)
    summ_key = categories.categorize_cci_15_avg(bars_15m.ccia) + categories.categorize_cci_1h(bars_1h.ccia) + categories.categorize_cci_1d(bars_1d.ccia)
    #print("cci and ccibb key",cci_key, ccibb_key)
    return cci_key, ccibb_key, summ_key
