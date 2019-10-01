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

log = logger.getLogger()


class Algo():
    def __init__(self, ib: IB, app):
        self.ib = ib
        self.app = app

    def run(self):
        """ Execute the algorithm """
        key_arr = ['blank','ATR15','ATR1','ATRD','CCI15','CCIA15','CCIA1h','CCIA1d','BBW15','BBb15','BBW1h','BBb1h','BBW1d','BBb1d']
        tradenow = False
        not_finished = True
        pendingshort = False
        pendinglong = False      # this is when the cross over is not wide enough
        PendingLongCnt = 0
        PendingShortCnt = 0
        tradenow = False
        cci_trade = False
        ccibb_trade = False
        while not_finished:
            print ("top of algo run self*************************************************")
            #top of logic - want to check status as we enter a new bar/hour/day/contract
            crossed = False
            contContract, contracthours = get_contract(self) #basic information on continuious contact
            #i NEW
            tradeContract = self.ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
            open_long, open_short, position_qty = self.have_position(self.ib.positions())   # do we have an open position?
            open_today = helpers.is_open_today(contracthours)
            dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
            log.debug("Got Contract: {}".format(dataContract.localSymbol))
            #pnl = self.ib.pnl()
            log.debug("account names: {}".format(self.ib.managedAccounts()))
            log.info("PNL : {PNL} ".format(PNL=self.ib.pnl("all")))
            self.app.contract.update(dataContract.localSymbol)
            wait_time, datetime_15, datetime_1h, datetime_1d = self.define_times()
            log.debug("next datetime for 15 minutes - should be 15 minutes ahead of desired nextqtr{}".format(wait_time))
            self.ib.waitUntil(wait_time)
            self.app.qtrhour.update(wait_time)
            log.debug("requesting info for the following timeframe today: {} ".format(wait_time))
            #
            #start of study
            #
            bars_15m = self.get_bars_data(dataContract,"2 D","15 mins",datetime_15)
            print("bar data close: ",bars_15m[-1].close)
            x = np.array(bars_15m)
            log.debug("15 min bars {}".format(str(bars_15m[-1])))
            cci, avg, cci_prior, averageh, cci3 = calculate_cci(bars_15m)
            atr, atrprior =  calculate_atr(bars_15m)
            bband_width, bband_b,bband_width_prior, bband_b_prior = calculate_bbands(bars_15m)
            logged_it = self.log_value("Starting 15 minutes", cci,avg,cci_prior, averageh,atr,bband_width,bband_b)
            qtrtime = datetime.now()
            print("stop loss = ",round(bars_15m[-1].close + (atr *2)*4,0)/4)
            if cci > avg and cci_prior < averageh:
                crossed = True
                tradenow = True
                csv_row = "'"+str(datetime.now())+",'long'"
                key_arr[0] = "long"
                tradeAction = "BUY"
                stoplossprice = round(bars_15m[-1].close - (atr * 2)*4,0)/4
            elif cci < avg and cci_prior > averageh:
                crossed = True
                tradenow = True
                csv_row = "'"+str(datetime.now())+",'short'"
                key_arr[0] = "short"
                tradeAction = "SELL"
                stoplossprice = round(bars_15m[-1].close + (atr * 2)*4,0)/4
            else:
                csv_row = "'"+str(datetime.now())+",'cash'"
                crossed = False
                tradenow = False
                stoplossprice = 0
                stoploss = 0
            if abs(cci - avg) > config.SPREAD:
                log.info("Pending ".format(cci-avg))
                pendinglong = True
                pendingshort = True
            csv_header = "Date,Status,Crossed,CCI15,CCIA15,CCI15P,CCIA15P,ATR15,BBw15,BBB15"
            csv_row += ",'"+str(crossed)+"',"+str(cci)+","+str(avg)+","+str(cci_prior)+","+str(averageh)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            key_arr[1] = categories.categorize_atr15(atr)
            key_arr[4] = categories.categorize_cci_15(cci)
            key_arr[5] = categories.categorize_cci_15_avg(avg)
            key_arr[8] = categories.categorize_BBW15(bband_width)
            key_arr[9] = categories.categorize_BBb15(bband_b)
            #
            #1 hour data 
            #
            log.debug("next datetime for 1 hour - should be 1 hour behind current hour {}".format(datetime_1h))
            bars_1h = self.get_bars_data(dataContract,"5 D","1 hour",datetime_1h)
            cci, avg, cci_prior, averageh, cci3 = calculate_cci(bars_1h)
            log.debug("bars_1h {}".format(str(bars_1h[-1])))
            atr,atrprior = calculate_atr(bars_1h)
            bband_width, bband_b,bband_width_prior, bband_b_prior = calculate_bbands(bars_1h)
            csv_row += ","+str(cci)+","+str(avg)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            csv_header += ",CCI1h,CCIA1h,ATR1h,BBW1h,BBB1h"
            key_arr[2] = categories.categorize_atr1h(atr)
            key_arr[6] = categories.categorize_cci_1h(avg)
            key_arr[10] = categories.categorize_BBW1h(bband_width)
            key_arr[11] = categories.categorize_BBb1h(bband_b)
            #logged_it = self.log_value("Starting 1 hour", cci,avg,cci_prior, averageh,atr,bband_width,bband_b)
            qtrtime = datetime.now()
            
            log.debug("requesting info for the following timeframe today: nextday: ".format(datetime_1d))
            bars_1d = self.get_bars_data(dataContract,"75 D","1 day",datetime_1d)
            log.debug("1d min bars {}".format(str(bars_1d[-1])))
            cci, avg, cci_prior, averageh, cci3 = calculate_cci(bars_1d)
            atr, atrprior = calculate_atr(bars_1d)
            bband_width, bband_b,bband_width_prior, bband_b_prior = calculate_bbands(bars_1d)
            csv_row += ","+str(cci)+","+str(avg)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            csv_header += ",CCI1d,CCIA1d,ATR1d,BBB1d,BBW1d"
            key_arr[3] = categories.categorize_atr1d(atr)
            key_arr[7] = categories.categorize_cci_1d(avg)
            key_arr[12] = categories.categorize_BBW1d(bband_width)
            key_arr[13] = categories.categorize_BBb1d(bband_b)
            #logged_it = self.log_value("Starting 1 Day", cci,avg,cci_prior, averageh,atr,bband_width,bband_b)
            qtrtime = datetime.now()
            setsum = self.setupsummary(key_arr)
            log.info("tradenow: {trade}".format(trade = tradenow))
            #
            # starting trade logic
            #
            # test buy
            if tradenow:
                log.info("Tradeing this bar {}".format(str(''.join(key_arr))," - ",''.join(key_arr[0:8])))
                csv_file1 = csv.reader(open('data/ccibb.csv', "rt"), delimiter = ",")
                for row1 in csv_file1:
                    #print("ccibb row: ",row1[0])
                    if ((''.join(key_arr)) == row1[0]):
                            log.info("we have a match in ccibb.csv")
                            log.info("found a match in CCIBB ".format(str(row1[0])))
                            ccibb_trade = True
                            ParentOrderID = orders.buildOrders(self.ib,tradeContract,tradeAction,2,"ccibb_day",stoplossprice)
                            log.info("order placed, parentID: {}".format(ParentOrderID))
                            tradenow = False
                            status_done = self.row_results(row1,cci_trade,ccibb_trade)
                            break
                csv_file2 = csv.reader(open('data/cci.csv', "rt"), delimiter = ",")
                for row2 in csv_file2:
                    #print("cci   row: ",row2[0])
                    if ((''.join(key_arr[0:8])) == row2[0]):
                            log.info("we have a match in cci.csv")
                            log.info("found a math in CCI {}".format(str(row2[0])))
                            ParentOrderID = orders.buildOrders(self.ib,tradeContract,tradeAction,2,"cci_day",stoplossprice)
                            cci_trade = True
                            tradenow = False
                            status_done = self.row_results(row2,cci_trade,ccibb_trade)
                            break
                log.info("did we find a match?  If true than no {match}".format(match = tradenow))
            csv_row += ","+(''.join(key_arr))+","+(''.join(key_arr[0:8]))+","+str(cci_trade)+","+str(ccibb_trade)+","+str(pendinglong)+","+str(pendingshort)
            csv_header += ",CCIbbKey,CCIKey,CCI Trade,CCIbbTrade,PendingLong, PendingShort"
            with open('data/hist15.csv', mode='a') as hist15:
                histwriter = csv.writer(hist15, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                histwriter.writerow([csv_header])
                histwriter.writerow([csv_row])
            tradenow = False
            cci_trade = False
            ccibb_trade = False

    def get_bars_data(self, contract, bardur, tframe,bar_datetime):
        log.debug("inputs to request hist for get bars - {}".format(bar_datetime))
        return self.ib.reqHistoricalData(
                contract=contract,
                endDateTime=bar_datetime,
                durationStr=bardur,
                barSizeSetting=tframe,
                whatToShow="TRADES",
                useRTH=False,
                keepUpToDate=False
        )
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
        #print("wait time",wait_time)
        #print("datetime_15 ",datetime_15)
        #print("datetime_1h",datetime_1h)
        #print("datetime_1d",datetime_1d)
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
                    position_long_tf = True
                    position_short_tf = False
                elif (position_qty) < 0:
                    position_long_tf = False
                    position_short_tf = True
                else:
                    position_long_tf = False
                    position_short_tf = False
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
    def crossoverPending(self):



        return
def calculate_cci(bars: BarDataList):
    cci = talib.CCI(
        np.array([bar.high for bar in bars]),
        np.array([bar.low for bar in bars]),
        np.array([bar.close for bar in bars]),
        timeperiod=config.CCI_PERIODS
    )
    average = statistics.mean(cci[-config.CCI_AVERAGE_PERIODS:])
    averageh = statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 1):][:-1])
    return cci[-1], average, cci[-2], averageh, cci[-3]

def calculate_atr(bars):
    atr =  talib.ATR(
        np.array([bar.high for bar in bars]),
        np.array([bar.low for bar in bars]),
        np.array([bar.close for bar in bars]),
        timeperiod=config.ATR_PERIODS
    )
    return atr[-1], atr[-2]

def calculate_bbands(bars):
    up, mid, low = talib.BBANDS(
        np.array([bar.close for bar in bars]),
        timeperiod=config.BBAND_PERIODS,
        nbdevup=config.BBAND_STDDEV,
        nbdevdn=config.BBAND_STDDEV,
        matype=talib.MA_Type.SMA # Wilder Moving Average
    )
    sma = talib.SMA(np.array([bar.close for bar in bars]), timeperiod=config.SMA_PERIODS)
    width = (up[-1] - low[-1]) / sma[-1] * 100
    percentb = (bars[-1].close - low[-1]) / (up[-1] - low[-1]) * 100
    widthprior = (up[-2] - low[-2]) / sma[-2] * 100
    percentbprior = (bars[-2].close - low[-2]) / (up[-2] - low[-2]) * 100
    return width, percentb, widthprior, percentbprior

def get_contract(client):
    contract = client.ib.reqContractDetails(
        ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
    )
    if not contract:
        log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
        sysexit()
    return contract[0].contract, contract[0].tradingHours
