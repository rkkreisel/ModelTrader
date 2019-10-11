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
#import csv
import categories
#import helpers
#import orders

log = logger.getLogger()


class Calculations(bar_duration, bar_size, datetime_period):
    def __init__(self, ib: IB, bar_duration, bar_size_15m:
        self.ib = ib
        self.bar_duration = bar_duration
        self.bar_size = bar_size
        self.bar_size_15m
        #bar duration must be something like 2 D, 5 D, 75 D
        #bar size must be something like 15 mins, 1 hour, 1 day

    def run(self):
        """ Execute the calculations """
        
        bars_period = self.get_bars_data(dataContract,bar_duration,bar_size,datetime_period)
        print("bar data close: ",bars_15m[-1].close)
        x = np.array(bars_15m)
        log.debug("bars {}".format(bar_duration,bar_size,str(bars_15m[-1])))
        cci, ccia, cci_prior, ccia_prior = calculate_cci(bars_period)
        atr =  calculate_atr(bars_15m)
        bband_width, bband_b = calculate_bbands(bars_15m)
        logged_it = self.log_value("Starting ", bar_size, cci,ccia,cci_prior, ccia_prior,atr,bband_width,bband_b)
        print("stop loss = ",round((bars_15m[-1].close + (atr *2))*4,0)/4)
        if bar_size == "15 mins":
            if cci > ccia and cci_prior < ccia_prior:
                crossed, tradenow = True, True
                csv_row = "'"+str(datetime.now())+",'long'"
                key_arr[0] = "long"
                tradeAction = "BUY"
                stoplossprice = round((bars_15m[-1].close - (atr * 2))*4,0)/4
            elif cci < avg and cci_prior > averageh:
                crossed, tradenow = True, True
                csv_row = "'"+str(datetime.now())+",'short'"
                key_arr[0] = "short"
                tradeAction = "SELL"
                stoplossprice = round((bars_15m[-1].close + (atr * 2))*4,0)/4
            else:
                csv_row = "'"+str(datetime.now())+",'cash'"
                crossed, tradenow = False, False
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
        elif bar_size == "1 hour":
            csv_row += ","+str(cci)+","+str(avg)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            csv_header += ",CCI1h,CCIA1h,ATR1h,BBW1h,BBB1h"
            key_arr[2] = categories.categorize_atr1h(atr)
            key_arr[6] = categories.categorize_cci_1h(avg)
            key_arr[10] = categories.categorize_BBW1h(bband_width)
            key_arr[11] = categories.categorize_BBb1h(bband_b)
        elif bar_size == "1 day":            
            csv_row += ","+str(cci)+","+str(avg)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            csv_header += ",CCI1d,CCIA1d,ATR1d,BBB1d,BBW1d"
            key_arr[3] = categories.categorize_atr1d(atr)
            key_arr[7] = categories.categorize_cci_1d(avg)
            key_arr[12] = categories.categorize_BBW1d(bband_width)
            key_arr[13] = categories.categorize_BBb1d(bband_b)
            qtrtime = datetime.now()
            setsum = self.setupsummary(key_arr)
            log.info("tradenow: {trade}".format(trade = tradenow))
        
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
        #widthprior = (up[-2] - low[-2]) / sma[-2] * 100
        #percentbprior = (bars[-2].close - low[-2]) / (up[-2] - low[-2]) * 100
        return width, percentb