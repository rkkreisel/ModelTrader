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
import tkinter as tk

log = logger.getLogger()

class Algo():
    def __init__(self, ib: IB, app, backTest, backTestStartDateTime,myConnection):
        self.ib = ib
        self.app = app
        self.backTest = backTest
        self.backTestStartDateTime = backTestStartDateTime
        self.myConnection = myConnection
        self.myTest = True
        self.tradeBarCount = 0
        self.STPorTRAIL = "STP"

    def run(self):
        tradeNow, not_finished, pendingShort, pendingLong, pendingSkip, cci_trade, ccibb_trade, crossed, justStartedApp = False, True, False, False, False, False, False, False, True
        self.app.stopMode.update(self.STPorTRAIL)
        pendingCnt = 0
        # any variable that is used within the class will be defined with self
        if justStartedApp:
            #pendingLong, pendingShort, pendingCnt = self.justStartedAppDirectionCheck()
            self.justStartedAppDirectionCheck()
            #if not pendingLong and not pendingShort:
            #    pendingLong, pendingShort, pendingCnt = self.justStartedAppPendingCheck()
            justStartedApp = False
            # do we need to reset pending
            reviewIBTrades = orders.getListOfTrades(self.ib)
            self.app.appStart.update(f"{datetime.now():%m/%d %I:%M:%S}")
        while not_finished:
            log.debug("top of algo run self*************************************************")
            #top of logic - want to check status as we enter a new bar/hour/day/contract
            contContract, contracthours = get_contract(self) #basic information on continuious contact
            tradeContract = self.ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
            #orders.checkForFilledOrders(self.ib,self.myConnection,self)      # If we use cient ID 0 we will get an event on any trades otherwise we need to check here
            open_long, open_short, long_position_qty, short_position_qty, account_qty = orders.countOpenPositions(self.ib,"")   # do we have an open position?
            self.app.shares.update(long_position_qty + short_position_qty)
            dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
            log.debug("Got Contract:{dc} local symbol {ls}".format(dc=dataContract,ls=dataContract.localSymbol))
            self.app.contract.update(dataContract.localSymbol)
            wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d, self.log_time = self.define_times(self.ib)
            #self.update_tk_text("wait_time {w} self.datetime_15 {one} self.datetime_1h {h} self.datetime_1d {d} self.log_time {l} ".format(w=wait_time,one=self.datetime_15,h=self.datetime_1h,d=self.datetime_1d,l=self.log_time))
            log.debug("next datetime for 15 minutes - should be 15 minutes ahead of desired nextqtr{wt} and current time {ct}".format(wt=wait_time,ct=datetime.today()))
            # need to determine if this is normal trading hours or not
            dayNightProfileCCI, dayNightProfileCCIBB = self.duringOrAfterHours(self.ib,contracthours)
            self.ib.waitUntil(wait_time)
            bars_15m = calculations.Calculations(self.ib, dataContract, "2 D", "15 mins", self.datetime_15,False, 0)
            log.debug("15m cci spread: {s}".format(s=bars_15m.cci_ccia_spread))
            log.info("going into calculations - what is the datetime 1h: {d}".format(d=self.datetime_1h))
            if bars_15m.atr < config.ATR_STOP_MIN:
                bars_1h = calculations.Calculations(self.ib, dataContract, "5 D", "1 hour", self.datetime_1h,True, bars_15m.closePrice)
                modBuyStopLossPrice = bars_1h.buyStopLossPrice
                modSellStopLossPrice = bars_1h.sellStopLossPrice
                modTrailStopLoss = (bars_1h.sellStopLossPrice - bars_1h.buyStopLossPrice)/2
                self.update_tk_text("bar 15 less then config")
            else:
                bars_1h = calculations.Calculations(self.ib, dataContract, "5 D", "1 hour", self.datetime_1h,False, 0)
                modBuyStopLossPrice = bars_15m.buyStopLossPrice
                modSellStopLossPrice = bars_15m.sellStopLossPrice
                modTrailStopLoss = (bars_1h.sellStopLossPrice - bars_1h.buyStopLossPrice)/2
                self.update_tk_text("bar 15 greater then config")
            self.app.buyStop.update(modBuyStopLossPrice)
            self.app.sellStop.update(modSellStopLossPrice)
            self.app.trailStop.update(modTrailStopLoss)
            #self.update_tk_text("modSellStopLossPrice: {c} modBuyStopLossPrice: {d}".format(c=modSellStopLossPrice,d=modBuyStopLossPrice))
            bars_1d = calculations.Calculations(self.ib, dataContract, "75 D", "1 day", self.datetime_1d,False, 0)
            self.barsCalcUpdateTK(bars_15m,bars_1h,bars_1d)
            pendingLong, pendingShort, pendingCnt, pendingSkip, tradeNow, tradeAction, crossed = self.crossoverPending(bars_15m,pendingLong,pendingShort,pendingSkip,pendingCnt)
            cci_key, ccibb_key, summ_key = self.build_key_array(tradeAction, bars_15m, bars_1h, bars_1d)
            log.debug("tradeNow: {trade} pendingSkip {skip}".format(trade = tradeNow, skip = pendingSkip))
            log.debug("going into tradenow: {tn}, backtest: {bt}, open long: {ol} and short: {os}".format(tn=tradeNow, bt=self.backTest, ol=open_long, os=open_long))
            #handeling existing position
            self.app.logicOpenLong.update(open_long)
            self.app.logicOpenShort.update(open_short)
            self.app.logictradeNow.update(tradeNow)
            self.app.logicspread.update("{:.2f}".format(bars_15m.cci_ccia_spread))
            updated = self.update_tk(bars_15m, bars_1h, bars_1d)
            if crossed and (open_long or open_short) and not (pendingLong or pendingShort):    # need to close stp and open positions
                log.debug("crossed and not pending so lets close stp and open positions.  Open Long: {ol} open short: {os} pending long: {pl} pending short: {ps}".format(ol=open_long,os=open_short,pl=pendingLong,ps=pendingShort))
                allClosed = orders.closeOutMain(self.ib,tradeContract,False)     # we don't worry about whether we are long or short
                self.update_tk_text(" crossed with open position and not pending ")
            elif (not (pendingLong or pendingShort)) and open_long and tradeAction == "Sell":
                log.debug("Not pending we are open_long and tradeaction is sell so lets close out stp and open positions  Open Long: {ol} open short: {os} pending long: {pl} pending short: {ps}".format(ol=open_long,os=open_short,pl=pendingLong,ps=pendingShort))
                allClosed = orders.closeOutMain(self.ib,tradeContract,False)     # we don't worry about whether we are long or short
                self.update_tk_text(" crossed with long position and tradeAction Sell ")
            elif (not (pendingLong or pendingShort)) and open_short and tradeAction == "Buy":
                log.debug("Not pending we are open_short and tradeaction is buy so lets close out stp and open positions  Open Long: {ol} open short: {os} pending long: {pl} pending short: {ps}".format(ol=open_long,os=open_short,pl=pendingLong,ps=pendingShort))
                allClosed = orders.closeOutMain(self.ib,tradeContract,False)     # we don't worry about whether we are long or short
                self.update_tk_text(" crossed with short position and tradeAction Buy ")
            if tradeNow:
                log.info("tradeNow - Tradeing this bar")
                #self.update_tk_text("tradeNow looking for match ")
                #csv_file1 = csv.reader(open('data/ccibb.csv', "rt"), delimiter = ",")
                #cci_key, ccibb_key = build_key_array(self, tradeAction, bars_15m, bars_1h, bars_1d)
                #for row1 in csv_file1:
                if (tradeAction == "Buy" and bars_1h.cci_over_ccia_tf == 't' and bars_1d.cci_over_ccia_tf == 't') or \
                    (tradeAction == "Buy" and bars_1h.cci_over_ccia_tf == 't' and bars_1d.cci> 100) or \
                    (tradeAction == "Buy" and bars_1h.cci > 100 and bars_1d.cci> 100) or \
                    (tradeAction == "Buy" and bars_1h.cci > 100 and bars_1d.cci_over_ccia_tf == 't') or \
                    (tradeAction == "Sell" and bars_1h.cci_over_ccia_tf == 'f' and bars_1d.cci_over_ccia_tf == 'f') or \
                    (tradeAction == "Sell" and bars_1h.cci_over_ccia_tf == 'f' and bars_1d.cci < -100) or \
                    (tradeAction == "Sell" and bars_1h.cci < -100 and bars_1d.cci < -100) or \
                    (tradeAction == "Sell" and bars_1h.cci < -100 and bars_1d.cci_over_ccia_tf == 'f'):
                    #log.info("we have a match in ccibb.csv")
                    log.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    log.info(" +++++++++++++++++++++++++++++++++++++++++++++++++ TRADING ")
                    log.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    ccibb_trade = True
                    self.tradeBarCount = self.tradeBarCount + 1
                    quantity = 1
                    modBuyStopLossPrice = bars_15m.buyStopLossPriceOpen     # need to set stop loss to open of current bar and not close of prior
                    modSellStopLossPrice = bars_15m.sellStopLossPriceOpen
                    if not self.backTest:
                        #fillStatus = orders.createOrdersMain(self.ib,tradeContract,tradeAction,quantity,dayNightProfileCCI,modBuyStopLossPrice,modSellStopLossPrice,False, modTrailStopLoss, bars_15m.closePrice,self.myConnection)
                        fillStatus = orders.buildOrders(self.ib, self.myConnection, tradeContract, tradeAction, quantity, dayNightProfileCCI, modBuyStopLossPrice,modSellStopLossPrice, modTrailStopLoss, bars_15m.closePrice, "STP")
                        log.debug("logic.CCIbb: order placed, fillStatus: {fs}".format(fs=fillStatus))
                    open_long, open_short, tradenow = False, False, False
                    #status_done = self.row_results(row1,cci_trade,ccibb_trade)
                    break
                else:
                    log.debug("hourly and daily cci_over_ccia is false on one or both")
                    self.app.status1.update("Entry found in CCIBB but not traded.")
                    self.update_tk_text(" ccibbkey not traded ")
                    ccibb_trade = False

                if tradeNow:
                    log.info("not trading this bar")
            # testing orders and trades
            #if self.myTest:
            #    self.myTest = False
            log.info("open_long: {ol} open_short:{os}".format(ol=open_long,os=open_short))
            if not open_long and not open_short:
                log.info("open_long: {ol} open_short:{os}".format(ol=open_long,os=open_short))
                quantity = 1
                modBuyStopLossPrice = bars_15m.buyStopLossPriceOpen     # need to set stop loss to open of current bar and not close of prior
                modSellStopLossPrice = bars_15m.sellStopLossPriceOpen
                fillStatus = orders.buildOrders(self.ib, self.myConnection, tradeContract, tradeAction, quantity, dayNightProfileCCI, modBuyStopLossPrice,modSellStopLossPrice, modTrailStopLoss, bars_15m.closePrice, "STP")
                self.tradeBarCount = self.tradeBarCount + 1
            # end testing
            # wrote_bar_to_csv = helpers.build_csv_bars_row(self.log_time, tradeAction, bars_15m, bars_1h, bars_1d, pendingLong, pendingShort, pendingCnt, tradeNow, ccibb_trade, cci_trade,ccibb_key, cci_key)
            tradenow, cci_trade, ccibb_trade = False, False, False
            if open_long or open_short:
                self.tradeBarCount = self.tradeBarCount + 1
                if self.tradeBarCount > 1 and self.STPorTRAIL == "STP":
                    changed = orders.modifySTPOrder(self.ib,modBuyStopLossPrice,modSellStopLossPrice,bars_15m.closePrice,self.myConnection)
            elif not open_long and not open_short:
                self.tradeBarCount = 0
                if self.STPorTRAIL == "STP":
                    changed = orders.modifySTPOrder(self.ib,modBuyStopLossPrice,modSellStopLossPrice,bars_15m.closePrice,self.myConnection)
            self.app.logicBarCount.update(self.tradeBarCount)

    def define_times(self,ib):
        log.info("TWS time is: {tws} ".format(tws=self.ib.reqCurrentTime()))
        log.info("PTH time is: {st}".format(st=datetime.now()))
        localDateTime = datetime.now()
        log.info("go through datetime.now")
        twsTime = self.ib.reqCurrentTime()
        log.info("twstime first pass")
        twsTime = twsTime.replace(tzinfo=None)
        # twsTimeLocal = twsTime - timedelta(hours=4) #day lights saving time 
        log.info("twstime second pass")
        twsTimeLocal = twsTime - timedelta(hours=5)  #standard time
        log.info("tws time in local time zone format: {t} localDateTime: {ldt} twsTimeLocal: {ttl} ".format(t=twsTimeLocal,ldt=localDateTime,ttl=twsTimeLocal))
        if localDateTime < twsTimeLocal:
            twsDiff = twsTimeLocal- localDateTime
        elif localDateTime > twsTimeLocal:
            twsDiff = localDateTime - twsTimeLocal
        else:
            twsDiff = 0
        log.info("tws to server time diff:{diff} in seconds {s} microsecond {m}".format(diff=twsDiff,s=twsDiff.seconds,m=twsDiff.microseconds))
        if self.backTest:   # added for backtest
            current_time = self.backTestStartDateTime
            current_minute = self.backTestStartDateTime.minute
            self.backTestStartDateTime = current_time + timedelta(minutes=15)
        else:    
            current_time = localDateTime - timedelta(seconds = twsDiff.seconds, microseconds = twsDiff.microseconds) # trying to augment time differences
            current_minute = datetime.now().minute
            log.info("current adjusted time is: {ct} ".format(ct=current_time))
        
        if current_minute < 15:
            #self.datetime_1h = current_time - timedelta(hours=1)
            wait_time = current_time.replace(minute = 15,second=0, microsecond=0) 
            #self.datetime_15 = current_time.replace(minute = 0, second = 0, microsecond=0)
            self.datetime_15 = current_time.replace(minute = 15, second = 0, microsecond=0)
            #rint(" < 15 self.datetime_15 ",self.datetime_15)
        elif current_minute < 30:
            wait_time = current_time.replace(minute = 30,second=0, microsecond=0) 
            #self.datetime_15 = current_time.replace(minute = 15, second=0, microsecond=0)
            self.datetime_15 = current_time.replace(minute = 30, second=0, microsecond=0)
            #rint(" < 30 self.datetime_15 ",self.datetime_15)
        elif current_minute < 45:
            wait_time = current_time.replace(minute = 45,second=0, microsecond=0) 
            #self.datetime_15 = current_time + timedelta(minutes=(30-current_minute+15))
            #self.datetime_15 = current_time + timedelta(minute=45)
            self.datetime_15 =current_time.replace(minute=45,second=0, microsecond=0)
            #rint(" < 45 self.datetime_15 ",self.datetime_15)
        else:
            wait_time = current_time + timedelta(minutes=(60-current_minute))
            wait_time = wait_time.replace(second=0, microsecond=0)
            #self.datetime_15 = current_time + timedelta(minutes=(45-current_minute+15))
            self.datetime_15 = current_time + timedelta(minutes=(60-current_minute))
            self.datetime_15 =self.datetime_15.replace(second=0, microsecond=0)
            #rint("current_time {t}".format(t=current_time))
            #rint(" < 60 self.datetime_15 ",self.datetime_15)
        if self.backTest:    #added for backtest
            wait_time = datetime.now() + timedelta(seconds=3)
            self.log_time = self.backTestStartDateTime
        else:
            self.datetime_1h = current_time
            self.log_time = wait_time
        #self.update_tk_text(" from define times - 1 hour time is: {o}".format(o=self.datetime_1h))
        #log.info("wait time going into difference {wt}".format(wt=wait_time))
        wait_time = wait_time - timedelta(seconds = twsDiff.seconds, microseconds = twsDiff.microseconds) # trying to augment time differences
        wait_time = wait_time + timedelta(seconds = 5) # adding 5 seconds just to address fluctuations from wait set to wait execute
        #log.info("Wait time adjusted for differnces in time between TWS and server is now: {t}".format(t=wait_time))
        #self.datetime_1h = self.datetime_1h.replace(minute=0, second=0, microsecond=0)
        #self.datetime_1d = current_time -  timedelta(days = 1)
        self.datetime_1d = current_time
        self.datetime_1d =self.datetime_1d.replace(hour = 0, minute=0, second=0, microsecond=0)
        self.app.qtrhour.update(f"{wait_time:%m/%d %I:%M:%S}")
        log.info("log time: {lt} wait time: {wt} 1 hour: {one} day: {day}".format(lt = self.log_time,wt=wait_time,one=self.datetime_1h,day=self.datetime_1d))
        return wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d,self.log_time

    def row_results(self, row, cci_trade, ccibb_trade):
        log.info("************************************************")
        log.info("* CCI Trade:          {0:.2f}".format(float(cci_trade)))
        log.info("* CCIbb Trade:        {0:.2f}".format(float(ccibb_trade)))
        log.info("* Do we buy this one: {}".format(row[13]))
        log.info("************************************************")
        return

    def setupsummary(self,summ_key):
        csv_file3 = csv.reader(open('data/setupsummary.csv', "rt"), delimiter = ",")
        log.info("key setupsummary: ".format(summ_key))
        for row3 in csv_file3:
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
        log.debug("crossoverPending:")
        tradeNow, crossed = False, False
        tradeAction = "Sell"
        if bars_15m.cci > bars_15m.ccia:
            tradeAction = "Buy"
        if (bars_15m.cci < bars_15m.ccia and bars_15m.cci_prior > bars_15m.ccia_prior) or \
                (bars_15m.cci > bars_15m.ccia and bars_15m.cci_prior < bars_15m.ccia_prior):
                crossed = True
                
                log.info("crossoverpending: We have crossed ----------^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v")
                if abs(bars_15m.cci - bars_15m.ccia) > config.SPREAD:
                    log.info("crossoverpending: crossed and outside spread")
                    #self.app.spread.update("Good")
                    pendingShort, pendingLong = False, False
                    tradeNow = True
                else:
                    if bars_15m.cci < bars_15m.ccia:
                        pendingShort, pendingLong = True, False
                    else:
                        pendingShort, pendingLong = False, True   
                    #self.app.spread.update("Pending")
                    pendingCnt = 0
                    pendingSkip = True
                    log.info("crossoverpending: crossed but not meet spread requirement, pendingSkip: {skip}, pendingCnt: {cnt}".format(skip = pendingSkip, cnt = pendingCnt))
        log.info("crossoverpending: crossed {cross}, pendingSkip: {skip}, pendingCnt: {cnt}, bars 15cci: {cci}, bars 15ccia: {ccia}, bars15 cci prior: {ccip}, bars15 ccia prior: {cciap}"\
            .format(cross=crossed, skip = pendingSkip, cnt = pendingCnt, cci=bars_15m.cci ,ccia = bars_15m.ccia, ccip = bars_15m.cci_prior,cciap = bars_15m.ccia_prior))
        # deal with existing pending
        if pendingLong and pendingCnt < config.SPREAD_COUNT and bars_15m.cci - bars_15m.ccia > config.SPREAD:
            log.info("crossoverpending: pending long cnt < 3 and > spread")
            pendingLong, pendingSkip, tradeNow = False, False, True
            pendingCnt = 0
        elif pendingShort and pendingCnt < config.SPREAD_COUNT and abs(bars_15m.cci - bars_15m.ccia) > config.SPREAD:
            log.info("crossoverpending: pending short cnt < 3 and > spread")
            pendingShort, pendingSkip, tradeNow = False, False, True
            pendingCnt = 0
        elif (pendingLong or pendingShort) and pendingCnt == config.SPREAD_COUNT:
            log.info("crossoverpending: pending long or short and cnt = 3 stop pending. pendingcnt: {pc} config.spread: {sc}".format(pc=pendingCnt, sc=config.SPREAD_COUNT))
            pendingLong, pendingShort, pendingSkip, tradeNow = False, False, False, True
            pendingCnt = 0
        elif pendingLong or pendingShort:
            pendingCnt += 1
            log.info("crossoverpending: pending continues cnt: {cnt}".format(cnt = pendingCnt))
        log.info("crossoverpending: check post cross and we have tradeNow: {tn}, tradeAction: {ta}, pendingLong: {pl}, pendingShort: {ps}, pendingSkip: {pskip}, pendingCnt: {pc}".format(tn=tradeNow, ta=tradeAction, pl=pendingLong, ps=pendingShort, pskip=pendingSkip, pc=pendingCnt))
        self.app.logicCrossed.update(bool(crossed))
        self.app.logicPendingLong.update(bool(pendingLong))
        self.app.logicPendingShort.update(bool(pendingShort))
        self.app.logicpendingCnt.update(pendingCnt)
        return pendingLong, pendingShort, pendingCnt, pendingSkip, tradeNow, tradeAction, crossed

    def justStartedAppDirectionCheck(self):
        log.info("justStartedAppDirectionCheck: Application just restarted.  Going through our checks")
        # do we need to reverse positions?
        # first check to see if we have positions or open orders.  If not exit otherwise continue
        # Are we positioned in the wrong direction (i.e. long when we should be short?)  If so, we need to close STP and open open trades.
        # not going to take a position at this time.
        # the bars data is the current, not completed, bar so we have to go back to get closed bars.
        #
        # checking for wrong direction
        #
        # check for what we think is open and really is closed.
        # lets first check for open orders and get any mods to the stop done first
        #
        # setup required to perform following functions
        #
        contContract, contracthours = get_contract(self) #basic information on continuious contact
        dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
        wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d, self.log_time = self.define_times(self.ib)
        bars_15m = calculations.Calculations(self.ib, dataContract, "2 D", "15 mins", self.datetime_15, False, 0)
        bars_1h = calculations.Calculations(self.ib, dataContract, "5 D", "1 hour", self.datetime_1h,True, bars_15m.closePrice)
        bars_1d = calculations.Calculations(self.ib, dataContract, "75 D", "1 day", self.datetime_1d,False, 0)
        tradeInfo = self.ib.openOrders()
        #
        # OPEN ORDERS
        #
        #openOrdersCount = orders.countOpenOrders(self.ib,tradeInfo, self.myConnection)
        #self.app.logicopenOrders.update(str(openOrdersCount))
        #now that we know we have an open order we need to update stop order
        #need to calculate stop losses first
        #
        # UPDATE STOPS ON OPEN ORDERS
        #
        if self.STPorTRAIL == "STP":
            changed = orders.modifySTPOrder(self.ib,bars_15m.buyStopLossPrice,bars_15m.sellStopLossPrice,bars_15m.closePrice,self.myConnection)
            self.app.status1.update("Open orders where we changed the stop price is " +  str(changed)) 
        #
        # UPDATE FILLED ORDERS - now that we have open orders stop prices updates - lets make sure we are update on closed orders and trades
        #
        # CHECK FOR FILLED ORDER
        #  PUT THIS BACK
        orders.updateOrdersOnPullViaPermID(self.ib,self.myConnection,self)
        #contContract, contracthours = get_contract(self) #basic information on continuious contact
        #tradeContract = self.ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
        open_long, open_short, long_position_qty, short_position_qty, account_qty = orders.countOpenPositions(self.ib,"")   # do we have an open position - not orders but positions?
        open_today, tradingDayRules, currentTimeFrame = helpers.is_open_today(contracthours)
        wait_time,self.datetime_15,self.datetime_1h,self.datetime_1d, self.log_time = self.define_times(self.ib)
        
        updated = self.update_tk(bars_15m, bars_1h, bars_1d)
        #
        #rint("bars15 cci_third, ccia_third, cci_prior, ccia_prior, cci, ccia",bars_15m.cci_third,bars_15m.ccia_third,bars_15m.cci_prior, bars_15m.ccia_prior, bars_15m.cci, bars_15m.ccia)
        if bars_15m.cci_prior > bars_15m.ccia_prior and open_short and abs(bars_15m.cci - bars_15m.ccia) > config.SPREAD:
            log.info("justStartedAppDirectionCheck: we are in app start up and we need to reverse due to wrong direction")
            #allClosed = orders.closeOutMain(self.ib,tradeContract,True)     # we don't worry about whether we are long or short. just passing the contract, need to add order.  Second false is whether this is an opening order.  it is not
            log.info("justStartedAppDirectionCheck: crossed but not tradeNow so lets close stp and open positions")
        elif bars_15m.cci_prior > bars_15m.ccia_prior and open_short and abs(bars_15m.cci - bars_15m.ccia) <= config.SPREAD:
            return True, False, 1
            log.info("justStartedAppDirectionCheck: we are in app start up and we crossed but not exceed the spread - going pending")
        elif bars_15m.cci_prior < bars_15m.ccia_prior and open_long and abs(bars_15m.cci - bars_15m.ccia) > config.SPREAD:
            log.info("justStartedAppDirectionCheck: we are in app start up and we need to reverse due to wrong direction. Came in long and crossed down > spread")
            #allClosed = orders.closeOutMain(self.ib,tradeContract,True)     # we don't worry about whether we are long or short. just passing the contract, need to add order.  Second false is whether this is an opening order.  it is not
            log.info("justStartedAppDirectionCheck: crossed but not tradeNow so lets close stp and open positions")
        elif bars_15m.cci_prior < bars_15m.ccia_prior and open_long and abs(bars_15m.cci - bars_15m.ccia) <= config.SPREAD:
            return False, True, 1
            log.info("justStartedAppDirectionCheck: we are in app start up and we crossed but not exceed the spread - going pending")
        else:
            log.info("justStartedAppDirectionCheck: we are in app start up and we DO NOT need to reverse due to wrong direction - checking pending")
            log.info("justStartedAppPendingCheck:: bars_15m.prior {ccip} {cciap}, third {ccip3} {cciap3} open long and short {ol} {os}".format(ccip=bars_15m.cci_prior,cciap=bars_15m.ccia_prior,ccip3=bars_15m.cci_third,cciap3=bars_15m.ccia_third,ol=open_long,os=open_short))
            if bars_15m.cci_prior > bars_15m.ccia_prior and abs(bars_15m.cci_prior - bars_15m.ccia_prior) <= config.SPREAD and \
                bars_15m.cci_third < bars_15m.ccia_third and abs(bars_15m.cci_third - bars_15m.ccia_third) > config.SPREAD and \
                not open_long and not open_short:
                return True, False, 1
            elif bars_15m.cci_prior < bars_15m.ccia_prior and abs(bars_15m.cci_prior - bars_15m.ccia_prior) <= config.SPREAD and \
                bars_15m.cci_third > bars_15m.ccia_third and abs(bars_15m.cci_third - bars_15m.ccia_third) > config.SPREAD and \
                not open_long and not open_short:
                return False, True, 1
            else:
                log.info("not going into this session pending")
                return False, False, 0

    def duringOrAfterHours(self,ib, contracthours):
        open_today, tradingDayRules, currentTimeFrame = helpers.is_open_today(contracthours)
        dayNightProfileCCI = "cci_day"
        dayNightProfileCCIBB = "ccibb_day"
        currentHour = datetime.now()
        if currentTimeFrame == "Pre Market Hours" or currentTimeFrame =="After Market Hours":
            dayNightProfileCCI = "cci_night"
            dayNightProfileCCIBB = "ccibb_night"
        log.info("finished tradingrules - dayNightProfileCCI: {cci} and dayNightProfileCCIBB: {ccibb} ".format(cci = dayNightProfileCCI, ccibb = dayNightProfileCCIBB))
        return dayNightProfileCCI, dayNightProfileCCIBB
    
    def update_tk(self,bars_15m, bars_1h, bars_1d):
        self.app.cci15.update(f"{bars_15m.cci:.02f}")        
        self.app.cci15_av.update(f"{bars_15m.ccia:.02f}")
        self.app.atr15.update(f"{bars_15m.atr:.02f}")
        #self.app.cci15.update(f"{categories.categorize_cci_15(bars_15m.cci)}")        
        #self.app.cci15_av.update(f"{categories.categorize_cci_15_avg(bars_15m.ccia)}")
        #self.app.atr15.update(f"{categories.categorize_atr15(bars_15m.atr)}")
        #self.app.bband15_width.update(f"{bars_15m.bband_width:.02f}")
        #self.app.bband15_b.update(f"{bars_15m.bband_b:.02f}")
        #self.app.cci15p.update(f"{bars_15m.bband_b:.02f}")
        self.app.cci15p_av.update(f"{bars_15m.ccia:.02f}")
        self.app.cci1h.update(f"{bars_1h.cci:.02f}")
        self.app.cci1h_av.update(f"{bars_1h.ccia:.02f}")
        self.app.atr1h.update(f"{bars_1h.atr:.02f}")
        #self.app.cci1h.update(f"{categories.categorize_cci_1h(bars_1h.cci)}")
        #self.app.cci1h_av.update(f"{categories.categorize_cci_1h(bars_1h.ccia)}")
        #self.app.atr1h.update(f"{categories.categorize_atr1h(bars_1h.atr)}")
        #self.app.bband1h_width.update(f"{bars_1h.bband_width:.02f}")
        #self.app.bband1h_b.update(f"{bars_1h.bband_b:.02f}")
        self.app.cci1d.update(f"{bars_1d.cci:.02f}")
        self.app.cci1d_av.update(f"{bars_1d.ccia:.02f}")
        self.app.atr1d.update(f"{bars_1d.atr:.02f}")
        #self.app.cci1d.update(f"{categories.categorize_cci_1d(bars_1d.cci)}")
        #self.app.cci1d_av.update(f"{ categories.categorize_cci_1d(bars_1d.ccia)}")
        #self.app.atr1d.update(f"{categories.categorize_atr1d(bars_1d.atr)}")
        #self.app.bband1d_width.update(f"{bars_1d.bband_width:.02f}")
        #self.app.bband1d_b.update(f"{bars_1d.bband_b:.02f}")
        #self.app.status1.update("new bar")
        return

    def update_tk_text(self,insertText):
        self.app.text1.config(state="normal")
        #log.info("date time string ")
        #log.info(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        #stringTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.app.text1.insert(tk.INSERT,datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        self.app.text1.insert(tk.INSERT," ")
        self.app.text1.insert(tk.INSERT,insertText)
        self.app.text1.insert(tk.INSERT,'\n')
        self.app.text1.config(state="disabled")
        self.app.text1.pack()
        return
    
    def build_key_array(self,tradeAction, bars_15m, bars_1h, bars_1d):
            #These has to be in sequential order since insert adds rather than replace.
            cci_key = "long"
            if tradeAction == "Sell":
                cci_key = "short"
            cci_key += categories.categorize_atr15(bars_15m.atr) + categories.categorize_atr1h(bars_1h.atr) + categories.categorize_atr1d(bars_1d.atr) + \
                categories.categorize_cci_15(bars_15m.cci) + categories.categorize_cci_15_avg(bars_15m.ccia) + categories.categorize_cci_1h(bars_1h.ccia) + \
                categories.categorize_cci_1d(bars_1d.ccia) + categories.categorize_spread(bars_15m.cci_ccia_spread)
                #categories.categorize_cci_1d(bars_1d.ccia) + bars_1h.cci_over_ccia_tf + bars_1d.cci_over_ccia_tf + categories.categorize_spread(bars_15m.cci_ccia_spread)
            cci_key_no_spread = "long"
            if tradeAction == "Sell":
                cci_key_no_spread = "short"
            cci_key_no_spread += categories.categorize_atr15(bars_15m.atr) + categories.categorize_atr1h(bars_1h.atr) + categories.categorize_atr1d(bars_1d.atr) + \
                categories.categorize_cci_15(bars_15m.cci) + categories.categorize_cci_15_avg(bars_15m.ccia) + categories.categorize_cci_1h(bars_1h.ccia) + \
                categories.categorize_cci_1d(bars_1d.ccia) 
            #ccibb_key = cci_key_no_spread + categories.categorize_BBW15(bars_15m.bband_width) + categories.categorize_BBb15(bars_15m.bband_b) + categories.categorize_BBW1h(bars_1h.bband_width) + \
            #    categories.categorize_BBb1h(bars_1h.bband_b) + categories.categorize_BBW1d(bars_1d.bband_width) + categories.categorize_BBb1d(bars_1d.bband_b)
            summ_key = categories.categorize_cci_15_avg(bars_15m.ccia) + categories.categorize_cci_1h(bars_1h.ccia) + categories.categorize_cci_1d(bars_1d.ccia) + categories.categorize_spread(bars_15m.cci_ccia_spread)
            #summ_key = categories.categorize_cci_15_avg(bars_15m.ccia) + categories.categorize_cci_1h(bars_1h.ccia) + categories.categorize_cci_1d(bars_1d.ccia) + bars_1h.cci_over_ccia_tf + bars_1d.cci_over_ccia_tf + categories.categorize_spread(bars_15m.cci_ccia_spread)
            #return cci_key, cci_key_no_spread, summ_key
            #self.app.status1.update(cci_key)
            
            return cci_key, cci_key, summ_key

    def barsCalcUpdateTK(self,bars_15m,bars_1h,bars_1d):
        if bars_15m.cci_over_ccia_tf == "t":
            self.app.logic15over.update("Over")
        else:
            self.app.logic15over.update("Under")
        if bars_1h.cci_over_ccia_tf == "t":
            self.app.logic1hover.update("Over")
        elif bars_1h.cci > 100:
            self.app.logic1hover.update("BUY")
        else:
            self.app.logic1hover.update("Under")
        if bars_1d.cci_over_ccia_tf == "t":
            self.app.logic1dover.update("Over")
        elif bars_1d.cci < -100:
            self.app.logic1dover.update("SELL")
        else:
            self.app.logic1dover.update("Under")
        return

def get_contract(client):
    contract = client.ib.reqContractDetails(
        ContFuture(
            symbol=config.SYMBOL, 
            exchange=config.EXCHANGE)
    )
    log.info("contract:{c}".format(c=contract))
    if not contract:
        log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
        sysexit()
    return contract[0].contract, contract[0].tradingHours