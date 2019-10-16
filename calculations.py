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
import helpers
#import orders

log = logger.getLogger()


class Calculations():
    def __init__(self, ib: IB, dataContract, bar_size, bar_duration, datetime_period):
        self.ib = ib
        self.dataContract = dataContract
        self.bar_size = bar_size
        self.bar_duration = bar_duration
        self.datetime_period = datetime_period
#        self.cci = cci
 #       self.ccia = ccia
  #      self.cci_prior = ccia_prior
   #     self.ccia_prior = ccia_prior
    #    self.atr = atr
     #   self.bband_width = bband_width
      #  self.bband_b = bband_b
        self.run()
  
        """ Execute the calculations """
    def run(self):    
        csv_row_sum = ""
        print("bar_duration, bar size date time ",self.dataContract, self.bar_duration, self.bar_size, self.datetime_period)
        bars_period = self.get_bars_data(self.dataContract, self.bar_duration, self.bar_size, self.datetime_period)
        print("bar data close: ",bars_period[-1].close)
        x = np.array(bars_period)
        log.debug("bars {bars} ".format(bars=bars_period))
        self.cci, self.ccia, self.cci_prior, self.ccia_prior = self.calculate_cci(bars_period)
        self.atr =  self.calculate_atr(bars_period)
        self.bband_width, self.Rbband_b = self.calculate_bbands(bars_period)
        logged_it = self.log_value("Starting ", cci, ccia, cci_prior, ccia_prior, atr, bband_width, bband_b)
        print("atr and bar size",atr,bar_size)
        if bar_size == "15 mins":
            if cci > ccia and cci_prior < ccia_prior:
                crossed, tradenow = True, True
                csv_row_sum = helpers.build_csv_bars_row("'"+str(datetime.now())+",'long'",False, True, csv_row_sum)
                #key_arr[0] = "long"
                tradeAction = "BUY"
                stoplossprice = round((bars_period[-1].close - (atr * 2))*4,0)/4
            elif cci < ccia and cci_prior > ccia_prior:
                crossed, tradenow = True, True
                csv_row_sum = helpers.build_csv_bars_row("'"+str(datetime.now())+",'short'",False, False, csv_row_sum)
                #key_arr[0] = "short"
                tradeAction = "SELL"
                stoplossprice = round((bars_period[-1].close + (atr * 2))*4,0)/4
            else:
                csv_row_sum = helpers.build_csv_bars_row("'"+str(datetime.now())+",'cash'",False, False, csv_row_sum)
                crossed, tradenow = False, False
                stoplossprice = 0
                stoploss = 0
            if abs(cci - ccia) > config.SPREAD:
                log.info("Pending ".format(cci-ccia))
                pendinglong = True
                pendingshort = True
            log.info("Stop loss set > ".format(stoplossprice))
            
    def get_bars_data(self, dataContract, bar_duration, bar_size, datetime_period):
        log.debug("inputs to request hist for get bars - {}".format(bar_duration, bar_size, datetime_period))
        return self.ib.reqHistoricalData(
                contract=dataContract,
                endDateTime=datetime_period,
                durationStr=bar_duration,
                barSizeSetting=bar_size,
                whatToShow="TRADES",
                useRTH=False,
                keepUpToDate=False
        )
    
    def calculate_cci(self, bars):
        cci = talib.CCI(
            np.array([bar.high for bar in bars]),
            np.array([bar.low for bar in bars]),
            np.array([bar.close for bar in bars]),
            timeperiod=config.CCI_PERIODS
        )
        ccia = statistics.mean(cci[-config.CCI_AVERAGE_PERIODS:])
        ccia_prior = statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 1):][:-1])
        return cci[-1], ccia, cci[-2], ccia_prior

    def calculate_atr(self, bars):
        atr =  talib.ATR(
            np.array([bar.high for bar in bars]),
            np.array([bar.low for bar in bars]),
            np.array([bar.close for bar in bars]),
            timeperiod=config.ATR_PERIODS
        )
        return atr[-1], atr[-2]

    def calculate_bbands(self, bars):
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

    def log_value(self, label, cci, ccia, cci_prior, ccia_prior, atr, bband_width, bband_b):
        log.info(label.format(datetime.now()))
        log.info("CCI:      {} ".format(cci))
        log.info("CCIA      {} ".format(ccia))
        log.info("CCIP      {} ".format(cci_prior))
        log.info("CCIPA:    {} ".format(ccia_prior))
        log.info("ATR:      {} ".format(atr))
        log.info("bband w:  {} ".format(bband_width))
        log.info("bband p:  {} ".format(bband_b))
        return True
