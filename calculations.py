import statistics
from sys import exit as sysexit

#from ib_insync import IB
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
    def __init__(self, ib, dataContract, bar_size, bar_duration, datetime_period, getNewClose, bar15MinClose):
        self.ib = ib
        self.dataContract = dataContract
        self.bar_size = bar_size
        self.bar_duration = bar_duration
        self.datetime_period = datetime_period
        self.getNewClose = getNewClose
        self.bar15MinClose = bar15MinClose
        self.buyStopLossPrice = 0
        self.sellStopLossPrice = 0
        self.atr = 0
        self.closePrice = 0
        self.ATRBuyStopLossAmount = 0
        self.ATRSellStopLossAmount = 0
        self.run()
  
        """ Execute the calculations """
    def run(self):    
        bars_period = self.get_bars_data()
        #log.info("self datetime_period: {dtp} and bars_period: {bp}".format(dtp=self.datetime_period,bp=bars_period))
        self.closePrice = bars_period[-1].close
        #log.info("close 0 and close -1 {c1} or {c2}".format(c1=bars_period[0].close,c2=bars_period[-1].close))
        self.cci, self.ccia, self.cci_prior, self.ccia_prior, self.cci_third, self.ccia_third, self.cci_four, self.ccia_four = self.calculate_cci(bars_period)
        self.atr =  self.calculate_atr(bars_period)
        self.bband_width, self.bband_b = self.calculate_bbands(bars_period)
        temp = self.atr*4
        if self.getNewClose:
            self.sellStopLossPrice = round((self.bar15MinClose + self.atr)*4,0)/4
            self.buyStopLossPrice = round((self.bar15MinClose - self.atr)*4,0)/4
        else:
            self.sellStopLossPrice = round((self.closePrice + self.atr)*4,0)/4
            self.buyStopLossPrice = round((self.closePrice - self.atr)*4,0)/4
            
        self.ATRBuyStopLossAmount = round((self.atr*4),0)/4
        self.ATRSellStopLossAmount = round((self.atr*4),0)/4
        log.debug("Calculation: {bs} getNewClose: {gnc} bar15minclose: {c} buystop: {b} sellstop: {s} atrbuy: {ab} atrsell: {aas} close price: {cp}".format(bs=self.bar_size,gnc=self.getNewClose,c=self.bar15MinClose,b=self.buyStopLossPrice,s=self.sellStopLossPrice,ab=self.ATRBuyStopLossAmount,aas=self.ATRSellStopLossAmount,cp=self.closePrice))

        if self.bar_size == "15 mins":
            if self.self.cci > self.ccia and self.cci_prior < self.ccia_prior:
                crossed, tradenow = True, True
                tradeAction = "Buy"
            elif self.cci <self.ccia and self.cci_prior > self.ccia_prior:
                crossed, tradenow = True, True
                tradeAction = "Sell"
            else:
                crossed, tradenow = False, False
                self.buyStopLossPrice = 0
                self.sellStopLossPrice = 0
            if abs(self.cci - self.ccia) > config.SPREAD:
                log.debug("Pending ".format(cci-ccia))
                pendinglong = True
                pendingshort = True
            log.debug("calculations: Buy Stop loss set:{sl} sell stop loss: {stp} close was: {c}".format(sl=self.buyStopLossPrice,stp=self.sellStopLossPrice,c=bars_period[-1].close))
            
    def get_bars_data(self):
        log.debug("inputs to request hist for get bars - {}".format(self.bar_duration, self.bar_size, self.datetime_period))
        return self.ib.reqHistoricalData(
                contract=self.dataContract,
                endDateTime=self.datetime_period,
                durationStr=self.bar_size,
                barSizeSetting=self.bar_duration,
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
        for x in range(3):
            #rint("x bar size and cci value: {xv} {v} {bs} ".format(xv=x,v=cci[-x],bs=self.datetime_period))
            startx = (config.CCI_AVERAGE_PERIODS + (x + 0))
            stopx = (x + 0)
            #rint("stop/startx ",startx,stopx)
            #rint("cci value {v}".format(v=cci[-startx:][:-stopx]))
            #rint("cci ",cci)
        #log.info("high {a} lasthigh {l} ".format(a=np.array([bar.high for bar in bars]),l=bars[-1].high))
        #log.info(" ")
        #log.info("low {a} lastlow {l}".format(a=np.array([bar.low for bar in bars]),l=bars[-1].low))
        #log.info(" ")
        #log.info("close {a} last close {l}".format(a=np.array([bar.close for bar in bars]),l=bars[-1].close))
        #log.info("high ",np.array([bar.high for bar in bars]))
        ccia =          statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 1):][:-1])
        ccia_prior =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 2):][:-2])
        ccia_third =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 3):][:-3])
        ccia_four =     statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 4):][:-4])
        log.info("first and last CCI {i1} {i2}".format(i1=cci[-33],i2=cci[-1]))
        return cci[-2],ccia, cci[-3], ccia_prior, cci[-4], ccia_third, cci[-5], ccia_four

    def calculate_atr(self, bars):
        atr =  talib.ATR(
            np.array([bar.high for bar in bars]),
            np.array([bar.low for bar in bars]),
            np.array([bar.close for bar in bars]),
            timeperiod=config.ATR_PERIODS
        )
        return atr[-1]

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
        return width, percentb

    def log_value(self, label):
        log.info(label.format(datetime.now()))
        log.info("CCI:      {0:.2f} ".format(float(self.cci)))
        log.info("CCIA      {0:.2f} ".format(float(self.ccia)))
        log.info("CCIP      {0:.2f} ".format(float(self.cci_prior)))
        log.info("CCIPA:    {0:.2f} ".format(float(self.ccia_prior)))
        log.info("ATR:      {0:.2f} ".format(float(self.atr)))
        log.info("bband w:  {0:.2f} ".format(float(self.bband_width)))
        log.info("bband p:  {0:.2f} ".format(float(self.bband_b)))
        return True
