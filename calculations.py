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
        self.lowPrice = 0
        self.highPrice = 0
        self.ATRBuyStopLossAmount = 0
        self.ATRSellStopLossAmount = 0
        self.run()
  
        """ Execute the calculations """
    def run(self):
        self.ib.disconnect()
        self.ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
        bars_period = self.get_bars_data()
        if self.bar_duration == "75 D":
            log.info("self datetime_period: {dtp}   ".format(dtp=bars_period))
        fullDateIndex = 1
        if self.bar_duration == "15 mins":
            log.debug("self datetime_period: {dtp} means we want through: {tb} and bars_period: {bp} and len bars_period: {lbp}  ".format(tb=self.datetime_period - timedelta(minutes=15),dtp=self.datetime_period,bp=bars_period,lbp=len(bars_period)))
            log.debug("**************************************************************************************15 mins last datetime: {d}".format(d=bars_period[-1].date))
            foundDate = False
            for fullDateIndex in range(1,5):
                #rint("x is now {x}".format(x=fullDateIndex))
                if bars_period[-fullDateIndex].date == self.datetime_period - timedelta(minutes=15):
                    #rint("Date found in index: {i}".format(i=-fullDateIndex))
                    foundDate = True
                    break
            if not foundDate:
                log.debug("calculations - the date your requesting is not in the bars_period data from IB.  Could be during market closed hours")
        self.closePrice = bars_period[-1].close
        self.lowPrice = bars_period[-1].low
        self.highPrice = bars_period[-1].high
        log.debug("close 0 and close -1 {c1} or {c2}".format(c1=bars_period[0].close,c2=bars_period[-1].close))
        self.cci, self.ccia, self.cci_prior, self.ccia_prior, self.cci_third, self.ccia_third, self.cci_four, self.ccia_four, self.cci_over_ccia_tf, self.cci_ccia_spread = self.calculate_cci(bars_period,fullDateIndex)
        log.debug("Bars we asked for through this date: {d} and the last entry was: {l}".format(d=self.datetime_period,l=bars_period[-1].date))
        self.atr =  self.calculate_atr(bars_period)
        self.bband_width, self.bband_b = self.calculate_bbands(bars_period)
        temp = self.atr*4
        if self.getNewClose:
            log.info("getting newclose.  self.atr: {natr} self.bar15minclose: {bclose} bar duration: {bd}".format(natr=self.atr,bclose=self.bar15MinClose,bd=self.bar_duration))
            self.sellStopLossPrice = round((self.bar15MinClose + self.atr)*4,0)/4
            self.buyStopLossPrice = round((self.bar15MinClose - self.atr)*4,0)/4
        else:
            log.info("NOT getting newclose.  self.atr: {natr} self.high: {high} self.low: {low} bar duration: {bd}".format(natr=self.atr,high=self.highPrice,low=self.lowPrice,bd=self.bar_duration))
            #self.sellStopLossPrice = round((self.closePrice + self.atr)*4,0)/4
            #self.buyStopLossPrice = round((self.closePrice - self.atr)*4,0)/4
            self.sellStopLossPrice = round((self.highPrice + self.atr)*4,0)/4
            self.buyStopLossPrice = round((self.lowPrice - self.atr)*4,0)/4
            
        self.ATRBuyStopLossAmount = round((self.atr*4),0)/4
        self.ATRSellStopLossAmount = round((self.atr*4),0)/4
        log.info("Calculation: {bs} getNewClose: {gnc} bar15minclose: {c} buystop: {b} sellstop: {s} atrbuy: {ab} atrsell: {aas} close price: {cp}".format(bs=self.bar_size,gnc=self.getNewClose,c=self.bar15MinClose,b=self.buyStopLossPrice,s=self.sellStopLossPrice,ab=self.ATRBuyStopLossAmount,aas=self.ATRSellStopLossAmount,cp=self.closePrice))

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
        log.debug("inputs to request hist for get bars - duration: {d} bar size: {bs} and period: {p}".format(d=self.bar_duration, bs=self.bar_size, p=self.datetime_period))
        return self.ib.reqHistoricalData(
                contract=self.dataContract,
                endDateTime=self.datetime_period,
                durationStr=self.bar_size,
                barSizeSetting=self.bar_duration,
                whatToShow="TRADES",
                useRTH=False,
                keepUpToDate=False
        )
    
    def calculate_cci(self, bars, fullDateIndex):
        cci = talib.CCI(
            np.array([bar.high for bar in bars]),
            np.array([bar.low for bar in bars]),
            np.array([bar.close for bar in bars]),
            timeperiod=config.CCI_PERIODS
        )
        #ccia =          statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 0):])
        #ccia_prior =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 1):-1])
        #ccia_third =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 2):-2])
        #ccia_four =     statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 3):-3])
        #rint("fulldate range",-fullDateIndex)
        ccia=[0] * 10
        ccia[0]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 9):-9])
        ccia[1]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 8):-8])
        ccia[2]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 7):-7])
        ccia[3]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 6):-6])
        ccia[4]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 5):-5])
        ccia[5]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 4):-4])
        ccia[6]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 3):-3])
        ccia[7]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 2):-2])
        ccia[8]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 1):-1])
        ccia[9]    =    statistics.mean(cci[-(config.CCI_AVERAGE_PERIODS + 0):])
        if cci[-fullDateIndex] > ccia[-fullDateIndex]:
            cci_over_ccia_tf = "t"
        else:
            cci_over_ccia_tf = "f"
        #log.info("cci: {cci}".format(cci=abs(cci[-fullDateIndex])))
        #log.info("ccia: {ccibb}".format(ccibb=ccia[-fullDateIndex]))
        cci_ccia_spread = abs(cci[-fullDateIndex] - ccia[-fullDateIndex])
        log.debug("first and last CCI {i1} {i2}".format(i1=cci[-8],i2=cci[-1]))
        return cci[-fullDateIndex],ccia[-fullDateIndex], cci[-fullDateIndex-1], ccia[-fullDateIndex-1], cci[-fullDateIndex-2], ccia[-fullDateIndex-2], cci[-fullDateIndex-3], ccia[-fullDateIndex-3],cci_over_ccia_tf,cci_ccia_spread

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
        log.debug(label.format(datetime.now()))
        log.debug("CCI:      {0:.2f} ".format(float(self.cci)))
        log.debug("CCIA      {0:.2f} ".format(float(self.ccia)))
        log.debug("CCIP      {0:.2f} ".format(float(self.cci_prior)))
        log.debug("CCIPA:    {0:.2f} ".format(float(self.ccia_prior)))
        log.debug("ATR:      {0:.2f} ".format(float(self.atr)))
        log.debug("bband w:  {0:.2f} ".format(float(self.bband_width)))
        log.debug("bband p:  {0:.2f} ".format(float(self.bband_b)))
        return True