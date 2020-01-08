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
        tradeNow, not_finished, pendingShort, pendingLong, pendingSkip, cci_trade, ccibb_trade, crossed, justStartedApp = False, True, False, False, False, False, False, False, True
        pendingCnt = 0
        # any variable that is used within the class will be defined with self
        if justStartedApp:
            pendingLong, pendingShort, pendingCnt = self.justStartedAppDirectionCheck()
            justStartedApp = False
            # do we need to reset pending

        while not_finished:
            log.info("top of algo run self*************************************************")
            if not self.backTest:
                stpSell, stpBuy = orders.countOpenOrders(self.ib) # don't want to execute covering
                log.info("we have the follow number of open stp orders for Sell: {sell} and Buy: {buy} ".format(sell=stpSell, buy=stpBuy))
                #top of logic - want to check status as we enter a new bar/hour/day/contract
            contContract, contracthours = get_contract(self) #basic information on continuious contact
            tradeContract = self.ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
            open_long, open_short, long_position_qty, short_position_qty = orders.countOpenPositions(self.ib)   # do we have an open position?
            open_today = helpers.is_open_today(contracthours)
            dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
            log.debug("Got Contract: {}".format(dataContract.localSymbol))
            self.app.contract.update(dataContract.localSymbol)
            wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d, self.log_time = self.define_times(self.ib)
            log.debug("next datetime for 15 minutes - should be 15 minutes ahead of desired nextqtr{}".format(wait_time))
            #
            # debug 
            #current_time = datetime.now()
            #wait_time = wait_time = current_time.replace(minute = 1,second=0)
            #
            self.ib.waitUntil(wait_time)
            
            log.info("before loop start:{ls}".format(ls=datetime.now()))
            self.ib.loopUntil(condition=self.ib.isConnected())   # rying to fix 1100 error on nightly reset
            log.info("after loop start:{ls}".format(ls=datetime.now()))
            log.debug("requesting info for the following timeframe today: {} ".format(wait_time))
            bars_15m = calculations.Calculations(self.ib, dataContract, "2 D", "15 mins", self.datetime_15)
            bars_1h = calculations.Calculations(self.ib, dataContract, "5 D", "1 hour", self.datetime_1h)
            bars_1d = calculations.Calculations(self.ib, dataContract, "75 D", "1 day", self.datetime_1d)
            pendingLong, pendingShort, pendingCnt, pendingSkip, tradeNow, tradeAction, crossed = self.crossoverPending(bars_15m,pendingLong,pendingShort,pendingSkip,pendingCnt)
            cci_key, ccibb_key, summ_key = build_key_array(tradeAction, bars_15m, bars_1h, bars_1d)
            setsum = self.setupsummary(summ_key)
            log.info("tradeNow: {trade} pendingSkip {skip}".format(trade = tradeNow, skip = pendingSkip))
            log.info("going into tradenow: {tn}, backtest: {bt}, open long: {ol} and short: {os}".format(tn=tradeNow, bt=self.backTest, ol=open_long, os=open_long))
            if crossed: #and (open_long or open_short):    # need to close stp and open positions
                #if pendingLong or pendingShort:
                #    log.info("we have crossed and should close out our positions but we are pending so we are going to wait - check out if this is the right call pendingLong:{pl} pendingShort:{ps}".format(pl=pendingLong,ps=pendingShort))
                #else:
                #    log.info("we have crossed and we are going to close out our positions but we are pending so we are going to wait - check out if this is the right call pendingLong:{pl} pendingShort:{ps}".format(pl=pendingLong,ps=pendingShort))
                allClosed = orders.closeOutMain(self.ib,tradeContract,False)     # we don't worry about whether we are long or short
                log.info("crossed but not tradeNow so lets close stp and open positions")
            if tradeNow:
                log.info("tradeNow - Tradeing this bar {cci} - {ccibb}".format(cci=cci_key,ccibb=ccibb_key))
                csv_file1 = csv.reader(open('data/ccibb.csv', "rt"), delimiter = ",")
                #cci_key, ccibb_key = build_key_array(self, tradeAction, bars_15m, bars_1h, bars_1d)
                for row1 in csv_file1:
                    #print("ccibb row: ",row1[0],row1[13])
                    if ccibb_key == row1[0] and row1[13] == "Y": #13 is winrisk - whether we trade or not
                        #log.info("we have a match in ccibb.csv")
                        log.info("found a match in CCIBB ".format(str(row1[0])))
                        ccibb_trade = True
                        quantity = 2
                        # do we need to close out current order
                        # do we need to close out current stop loss orders?
                        if not self.backTest:
                            fillStatus = orders.createOrdersMain(self.ib,tradeContract,tradeAction,quantity,"ccibb_day",bars_15m.buyStopLossPrice,bars_15m.sellStopLossPrice)
                            log.info("logic.CCIbb: order placed, fillStatus: {fs}".format(fs=fillStatus))
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
                            fillStatus = orders.createOrdersMain(self.ib,tradeContract,tradeAction,quantity,"cci_day",bars_15m.buyStopLossPrice,bars_15m.sellStopLossPrice)
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

    def define_times(self,ib):
        # This whole block is trying to deal with the time differences between the server and TWS gateway.
        # we have noticed a 1 second drift and it impacts our data calls
        log.info("TWS time is: {tws} ".format(tws=self.ib.reqCurrentTime()))
        log.info("PTH time is: {st}".format(st=datetime.now()))
        #log.info("ib time min:{min}".format(min=self.ib.reqCurrentTime().minute))
        #log.info("ib time second:{min}".format(min=self.ib.reqCurrentTime().second))
        #
        localDateTime = datetime.now()
        twsTime = self.ib.reqCurrentTime()
        twsTime = twsTime.replace(tzinfo=None)
        #twsTime = twsTime.astimezone(timezone('America/New_York'))
        twsTimeLocal = twsTime - timedelta(hours=5)
        log.info("tws time in local time zone format: {t} ".format(t=twsTimeLocal))
        twsDiff = localDateTime - twsTimeLocal 
        log.info("tws to server time diff:{diff} ".format(diff=twsDiff))
        newWait = localDateTime + timedelta(seconds=twsDiff)
        log.info("additional delay in wait time added says wait time should be:{w}".format(w=newWait))
#        if twsDiff.hour < 5:
        #f localDateTime.second < twsDiff.second:
        #    secondDiff = (locatDateTime.second + 60) - twsDiff.second
        ###    print("second diff ",secondDiff)
         #   minuteDiff = (locatDateTime.minute - 1) - twsDiff.minute
         #   print("minuteDiff ",minuteDiff)
        #else:
        #    secondDiff = locatDateTime.second - twsDiff.second
        #    print("second diff ",secondDiff)
        #    minuteDiff = locatDateTime.minute - twsDiff.minute
        #    print("minuteDiff ",minuteDiff)
        #current_time + timedelta(minute=minuteDiff,second=secondDiff)
        if self.backTest:   # added for backtest
            current_time = self.backTestStartDateTime
            current_minute = self.backTestStartDateTime.minute
            self.backTestStartDateTime = current_time + timedelta(minutes=15)
            print("current time, backteststartdatetime",current_time,self.backTestStartDateTime)
        else:    
            current_time = datetime.now() + timedelta(seconds=5) #manually trying to augment time differences
            current_minute = datetime.now().minute
        log.info("currnet time: {ct} ".format(ct=current_time))
        if current_minute < 15:
            self.datetime_1h = current_time - timedelta(hours=1)
            wait_time = current_time.replace(minute = 15,second=0, microsecond=0) 
            self.datetime_15 = current_time.replace(minute = 30, second = 0, microsecond=0)
        elif current_minute < 30:
            wait_time = current_time.replace(minute = 30,second=0, microsecond=0) 
            self.datetime_15 = current_time.replace(minute = 45, second=0, microsecond=0)
        elif current_minute < 45:
            wait_time = current_time.replace(minute = 45,second=0, microsecond=0) 
            self.datetime_15 = current_time + timedelta(minutes=(45-current_minute+15))
            self.datetime_15 =self.datetime_15.replace(second=0, microsecond=0)
        else:
            wait_time = current_time + timedelta(minutes=(60-current_minute))
            wait_time = wait_time.replace(second=0, microsecond=0)
            self.datetime_15 = current_time + timedelta(minutes=(60-current_minute+15))
            self.datetime_15 =self.datetime_15.replace(second=0, microsecond=0)
        if self.backTest:    #added for backtest
            wait_time = datetime.now() + timedelta(seconds=3)
            self.log_time = self.backTestStartDateTime
        else:
            self.datetime_1h = current_time
            self.log_time = wait_time
        #print("wait time -> ",wait_time)
        #self.datetime_1h = self.log_time - timedelta(hours=1)
        self.datetime_1h = self.datetime_1h.replace(minute=0, second=0, microsecond=0)
        self.datetime_1d = current_time -  timedelta(days = 1)
        self.datetime_1d =self.datetime_1d.replace(hour = 0, minute=0, second=0, microsecond=0)
        log.info("log time: {lt} wait time: {wt} 1 hour: {one} day: {day}".format(lt = self.log_time,wt=wait_time,one=self.datetime_1h,day=self.datetime_1d))
        return wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d,self.log_time

    def row_results(self, row, cci_trade, ccibb_trade):
        log.info("************************************************")
        log.info("* CCI Trade:          {0:.2f}".format(float(cci_trade)))
        log.info("* CCIbb Trade:        {0:.2f}".format(float(ccibb_trade)))
        log.info("* Do we buy this one: {}".format(row[13]))
        log.info("* Profit:             {0:,.2f}".format(float(row[5])))
        log.info("* Winning %:          {0:.2f}%".format(float(row[11])*100))
        log.info("* Risk:               {0:.2f}%".format(float(row[12])))
        log.info("* Previous Order:     {}".format(row[6]))
        log.info("* Previous Wins:      {}".format(row[7]))
        log.info("* Rank (0-100)s:      {0:.2f}".format(float(row[31])))
        log.info("************************************************")
        return

    def setupsummary(self,summ_key):
        csv_file3 = csv.reader(open('data/setupsummary.csv', "rt"), delimiter = ",")
        log.debug("key setupsummary: ".format(summ_key))
        for row3 in csv_file3:
            #print("setupsummary   row: ",row3[4])
            if summ_key == row3[4]:
                log.info("++++++++++++++++++++++++++++++++++++")
                log.info("join key:     {}".format(summ_key))
                log.info("CCI Long %  : {0:.2f}".format(float(row3[7])*100))
                log.info("CCI Profit  : {0:,.2f}".format(float(row3[9])))
                log.info("CCI Win%    : {0:.2f}".format(float(row3[12])))
                log.info("CCIbb Long %: {0:.2f}".format(float(row3[15])*100))
                log.info("CCIbb Profit: {0:,.2f}".format(float(row3[17])))
                log.info("CCIbb Win%  : {0:.2f}".format(float(row3[20])*100))
                log.info("Rank (0-100): {0:.2f}".format(float(row3[21])))
                log.info("-------------------------------------")
                break
        return

    def crossoverPending(self, bars_15m, pendingLong, pendingShort, pendingSkip, pendingCnt):   # this is from excel macro.  Changes here should be changed there as well.
        tradeNow, crossed = False, False
        tradeAction = "Sell"
        if bars_15m.cci > bars_15m.ccia:
            tradeAction = "Buy"
        if (bars_15m.cci < bars_15m.ccia and bars_15m.cci_prior > bars_15m.ccia_prior) or \
                (bars_15m.cci > bars_15m.ccia and bars_15m.cci_prior < bars_15m.ccia_prior):
                crossed = True
                log.info("We have crossed ----------^v")
                if abs(bars_15m.cci - bars_15m.ccia) > config.SPREAD:
                    log.info("crossed and outside spread")
                    tradeNow = True
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

    def justStartedAppDirectionCheck(self):
        log.info("justStartedAppDirectionCheck: Application just restarted.  Going through our checks")
        # do we need to reverse positions?
        # first check to see if we have positions or open orders.  If not exit otherwise continue
        # Are we positioned in the wrong direction (i.e. long when we should be short?)  If so, we need to close STP and open open trades.
        # not going to take a position at this time.
        # the bars data is the current, not completed, bar so we have to go back to get closed bars.
        
        contContract, contracthours = get_contract(self) #basic information on continuious contact
        tradeContract = self.ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
        open_long, open_short, long_position_qty, short_position_qty = orders.countOpenPositions(self.ib)   # do we have an open position - not orders but positions?
        open_today = helpers.is_open_today(contracthours)
        wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d, self.log_time = self.define_times(self.ib)
        dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
        bars_15m = calculations.Calculations(self.ib, dataContract, "2 D", "15 mins", self.datetime_15)
        #print("bars15 cci_third, ccia_third, cci_prior, ccia_prior, cci, ccia",bars_15m.cci_third,bars_15m.ccia_third,bars_15m.cci_prior, bars_15m.ccia_prior, bars_15m.cci, bars_15m.ccia)
        if (bars_15m.cci_prior > bars_15m.ccia_prior and open_short) or (bars_15m.cci_prior < bars_15m.ccia_prior and open_long):
            log.info("we are in app start up and we need to reverse due to wrong direction")
            allClosed = orders.closeOutMain(self.ib,tradeContract,True)     # we don't worry about whether we are long or short. just passing the contract, need to add order
            log.info("crossed but not tradeNow so lets close stp and open positions")
        else:
            log.info("we are in app start up and we DO NOT need to reverse due to wrong direction")
        # now check if we should be pending on restart
        
        if (bars_15m.cci_four > bars_15m.ccia_four and bars_15m.cci_third < bars_15m.ccia_third and bars_15m.cci_prior < bars_15m.ccia_prior and \
        abs(bars_15m.cci_third - bars_15m.ccia_third) < config.SPREAD and abs(bars_15m.cci_prior - bars_15m.ccia_prior) < config.SPREAD) or \
        (bars_15m.cci_four < bars_15m.ccia_four and bars_15m.cci_third > bars_15m.ccia_third and bars_15m.cci_prior > bars_15m.ccia_prior and \
        abs(bars_15m.cci_third - bars_15m.ccia_third) < config.SPREAD and abs(bars_15m.cci_prior - bars_15m.ccia_prior) < config.SPREAD):
            log.info("we are in a second leg pending situation on start up")
            if bars_15m.cci_prior > bars_15m.ccia_prior:
                return True, False, 2
            else:
                return False, True, 2
        elif (bars_15m.cci_third > bars_15m.ccia_third and bars_15m.cci_prior < bars_15m.ccia_prior and abs(bars_15m.cci_prior - bars_15m.ccia_prior) < config.SPREAD) or \
        (bars_15m.cci_third < bars_15m.ccia_third and bars_15m.cci_prior > bars_15m.ccia_prior and abs(bars_15m.cci_prior - bars_15m.ccia_prior) < config.SPREAD):
            log.info("we are in a first leg pending situation on start up")
            if bars_15m.cci_prior > bars_15m.ccia_prior:
                return True, False, 1
            else:
                return False, True, 1
        else:
            log.info("we are not in an exiting pending pattern")
            return False, False, 0
        
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
    if tradeAction == "Sell":
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