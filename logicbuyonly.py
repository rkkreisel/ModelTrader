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
            tradeContract = self.ib.qualifyContracts(contContract)   # gives all the details of a contract so we can trade it
            print("contract non 0 ",tradeContract)
            print("")
            print("contract with 0 ",tradeContract[0])
            ParentOrderID = orders.buildOrders(self.ib,tradeContract[0],"BUY",1,"ccibb_day",3000)
            not_finished = False

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
                break
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
