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
    def __init__(self, ib: IB, app):
        self.ib = ib
        self.app = app

    def run(self):
        """ Execute the algorithm """
        key_arr = ['blank','ATR15','ATR1','ATRD','CCI15','CCIA15','CCIA1h','CCIA1d','BBW15','BBb15','BBW1h','BBb1h','BBW1d','BBb1d']
        tradenow, not_finished, pendingShort, pendingLong, pendingSkip, cci_trade, ccibb_trade = False, True, False, False, False, False, False
        pendingCnt = 0
        while not_finished:
            print ("top of algo run self*************************************************")
            #top of logic - want to check status as we enter a new bar/hour/day/contract
            contContract, contracthours = get_contract(self) #basic information on continuious contact
            tradeContract = self.ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
            open_long, open_short, position_qty = self.have_position(self.ib.positions())   # do we have an open position?
            open_today = helpers.is_open_today(contracthours)
            dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
            log.debug("Got Contract: {}".format(dataContract.localSymbol))
            #pnl = self.ib.pnl()
            #log.debug("account names: {}".format(self.ib.managedAccounts()))
            #log.info("PNL : {PNL} ".format(PNL=self.ib.pnl("all")))
            self.app.contract.update(dataContract.localSymbol)
            wait_time, datetime_15, datetime_1h, datetime_1d = self.define_times()
            log.debug("next datetime for 15 minutes - should be 15 minutes ahead of desired nextqtr{}".format(wait_time))
            self.ib.waitUntil(wait_time)
            self.app.qtrhour.update(wait_time)
            log.debug("requesting info for the following timeframe today: {} ".format(wait_time))
            #
            #start of study
            #
            bars_15m = calculations.Calculations(self.ib)
            bars_15m.run(dataContract, datetime_15,"2 D", "15 mins")
            print("bars_15m ",bars_15m)
            bars_1h = calculations.Calculations.run(self.ib, dataContract, datetime_1h, "5 D", "1 hour")
            bars_1d = calculations.Calculations.run(self.ib, dataContract, datetime_1d, "75 D", "1 day")
            setsum = self.setupsummary(key_arr)
            pendingLong, pendingShort, pendingCnt, pendingSkip, tradeNow = self.crossoverPending(bars_15m,pendingLong,pendingShort,pendingSkip,pendingCnt)
            log.info("tradeNow: {trade}".format(trade = tradeNow))
            #
            # starting trade logic
            #
            # test buy
            if bars_15m.tradeNow:
                log.info("Tradeing this bar {}".format(str(''.join(key_arr))," - ",''.join(key_arr[0:8])))
                csv_file1 = csv.reader(open('data/ccibb.csv', "rt"), delimiter = ",")
                cci_key, ccibb_key == key_array(bars_15m, bars_1h, bars_1d)
                for row1 in csv_file1:
                    print("ccibb row: ",row1[0],row1[13])
                    if ccibb_key == row1[0] and row1[13] == "Y": #13 is winrisk - whether we trade or not
                        quantity = 2
                        log.info("we have a match in ccibb.csv")
                        log.info("found a match in CCIBB ".format(str(row1[0])))
                        ccibb_trade = True
                        if open_long or open_short:
                            quantity = 4
                        ParentOrderID = orders.buildOrders(self.ib,tradeContract,tradeAction,quantity,"ccibb_day",stoplossprice)
                        log.info("order placed, parentID: {}".format(ParentOrderID))
                        open_long, open_short, tradenow = False, False, False
                        status_done = self.row_results(row1,cci_trade,ccibb_trade)
                        break
                    elif ccibb_key == row1[0] and row1[13] == "N":
                        log.info("Entry found in CCIBB but not traded.  See if this changes")
                csv_file2 = csv.reader(open('data/cci.csv', "rt"), delimiter = ",")
                for row2 in csv_file2:
                    print("cci   row: ",row2[0],row2[13])
                    if cci_key == row2[0] and row2[13] == "Y":
                        quantity = 2
                        log.info("we have a match in cci.csv - tradeAction".format(tradeAction))
                        log.info("found a math in CCI {}".format(str(row2[0])))
                        if open_long or open_short:
                            quantity = 4
                        ParentOrderID = orders.buildOrders(self.ib,tradeContract,tradeAction,quantity,"cci_day",stoplossprice)
                        open_long, open_short, tradenow = False, False, False
                        status_done = self.row_results(row2,cci_trade,ccibb_trade)
                        break
                    elif cci_key == row2[0] and row2[13] == "N":
                        log.info("Entry found in CCI but not traded.  See if this changes")
                if tradeNow:
                    log.info("we did not find a match")
                if open_long or open_short:
                    quantity = 2
                    ParentOrderID = orders.buildOrders(self.ib,tradeContract,tradeAction,quantity,"ccibb_day",stoplossprice)
                    open_long, open_short = False, False
            csv_row_add = helpers.build_csv_bars_row(","+(''.join(key_arr))+","+(''.join(key_arr[0:8]))+","+str(cci_trade)+","+str(ccibb_trade)+","+str(pendingLong)+","+str(pendingShort),True)
            
            
            tradenow, cci_trade, ccibb_trade = False, False, False

    def log_value(self, label,cci,avg,cci_prior, averageh,atr,bband_width,bband_b):
        log.info(label.format(datetime.now()))
        log.info("CCI:      {} ".format(cci))
        log.info("CCIA      {} ".format(avg))
        log.info("CCIP      {} ".format(cci_prior))
        log.info("CCIPA:    {} ".format(averageh))
        log.info("ATR:      {} ".format(atr))
        log.info("bband w:  {} ".format(bband_width))
        log.info("bband p:  {} ".format(bband_b))
        return True

    def define_times(self):
        current_time = datetime.now()
        current_minute = datetime.now().minute
        #print("now ",current_time)
        #print("minute ",current_minute)
        if current_minute < 15:
            wait_time = current_time.replace(minute = 15,second=0) 
            datetime_15 = current_time.replace(minute = 30, second = 0)
        elif current_minute < 30:
            wait_time = current_time.replace(minute = 30,second=0) 
            datetime_15 = current_time.replace(minute = 45, second=0)
        elif current_minute < 45:
            wait_time = current_time.replace(minute = 45,second=0) 
            datetime_15 = current_time + timedelta(minutes=(45-current_minute+15))
            datetime_15 = datetime_15.replace(second=0)
        else:
            wait_time = current_time + timedelta(minutes=(60-current_minute))
            wait_time = wait_time.replace(second=0)
            datetime_15 = current_time + timedelta(minutes=(60-current_minute+15))
            datetime_15 = datetime_15.replace(second=0)
        datetime_1h = wait_time.replace(minute=0)
        datetime_1d = current_time -  timedelta(days = 1)
        datetime_1d = datetime_1d.replace(hour = 0, minute=0, second=0)
        return wait_time, datetime_15, datetime_1h, datetime_1d

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
        position_qty = 0
        print("positions: ",positions)
        while x < len(positions):
            if (positions[x][1].symbol) == "ES":
                position_qty = positions[x][2]
                if (position_qty) > 0:
                    position_long_tf, position_short_tf = True, False
                elif (position_qty) < 0:
                    position_long_tf, position_short_tf = False, True
                else:
                    position_long_tf, position_short_tf = False, False
                log.info("Have a position: {position} and qty {qty} ".format(position = positions[x][1].symbol,qty=positions[x][2]))
                break
            x += + 1
        return position_long_tf, position_short_tf, position_qty 

    def setupsummary(self,key_arr):
        csv_file3 = csv.reader(open('data/setupsummary.csv', "rt"), delimiter = ",")
        log.debug("key setupsummary: ".format(str(''.join(key_arr[5:8]))))
        for row3 in csv_file3:
            #print("setupsummary   row: ",row3[4])
            if ((''.join(key_arr[5:8])) == row3[4]):
                log.info("join key: {}".format(''.join(key_arr[5:8])))
                log.info("CCI Long %  : {}".format(row3[7]))
                log.info("CCI Profit  : {}".format(row3[9]))
                log.info("CCI Win%    : {}".format(row3[12]))
                log.info("CCIbb Long %: {}".format(row3[15]))
                log.info("CCIbb Profit: {}".format(row3[17]))
                log.info("CCIbb Win%  : {}".format(row3[20]))
                log.info("Rank (0-100): {}".format(row3[21]))
                break
        return
    def crossoverPending(self, bars_15m,pendingLong, pendingShort, pendingSkip, pendingCnt):   # this is from excel macro.  Changes here should be changed there as well.
        tradeNow = False
        if (bars_15m.cci < bars_15m.ccia and bars_15m.ccip > bars_15m.cciap) or \
                (bars_15m.cci > bars_15m.ccia and bars_15m.ccip < bars_15m.cciap):
                tradeNow = True
        if pendingLong and pendingCnt < config.SPREAD_COUNT and bars_15m.cci - bars_15m.ccia > config.SPREAD:
            pendingLong, pendingSkip = False, False
            pendingCnt = 0
        elif pendingShort and pendingCnt < config.SPREAD_COUNT and abs(bars_15m.cci - bars_15m.ccia) > config.SPREAD:
            pendingShort, pendingSkip = False, False
            pendingCnt = 0
        elif pendingLong or pendingShort and pendingCnt == config.SPREAD_COUNT:
            pendingLong, pendingShort, pendingSkip = False, False, False
            pendingCnt = 0
        elif pendingLong or pendingShort:
            pendingCnt += 1
        return pendingLong, pendingShort, pendingCnt, pendingSkip, tradeNow 
        
def get_contract(client):
    contract = client.ib.reqContractDetails(
        ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
    )
    if not contract:
        log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
        sysexit()
    return contract[0].contract, contract[0].tradingHours

def key_array(bars_15m, bars_1h, bars_1d):
    #15m
    key_arr[1] = categories.categorize_atr15(bars_15m.atr)
    key_arr[4] = categories.categorize_cci_15(bars_15m.cci)
    key_arr[5] = categories.categorize_cci_15_avg(bars_15m.ccia)
    key_arr[8] = categories.categorize_BBW15(bars_15m.bband_width)
    key_arr[9] = categories.categorize_BBb15(bars_15m.bband_b)
    #hour
    key_arr[2] = categories.categorize_atr1h(bars_1h.atr)
    key_arr[6] = categories.categorize_cci_1h(bars_1h.ccia)
    key_arr[10] = categories.categorize_BBW1h(bars_1h.bband_width)
    key_arr[11] = categories.categorize_BBb1h(bars_1h.bband_b)
    #day
    key_arr[3] = categories.categorize_atr1d(bars_1d.atr)
    key_arr[7] = categories.categorize_cci_1d(bars_1d.ccia)
    key_arr[12] = categories.categorize_BBW1d(bars_1d.bband_width)
    key_arr[13] = categories.categorize_BBb1d(bars_1d.bband_b)
    ccibb_key = ''.join(key_arr)
    cci_key = ''.join(key_arr[0:8])
    return ccibb_key, cci_key 
