import statistics
from sys import exit as sysexit

from ib_insync import IB
from ib_insync.contract import ContFuture, Contract
from ib_insync.objects import BarDataList
import talib
import numpy as np
from datetime import *
import config
import logger
import csv

log = logger.getLogger()


class Algo():
    def __init__(self, ib: IB, app):
        self.ib = ib
        self.app = app

    def run(self):
        """ Execute the algorithm """
        not_finished = True
        while not_finished:
            print ("top of algo run self")
            crossed = False 
            self.app.crossover.update(crossed)
            contContract = get_contract(self)
            dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
            log.info("Got Contract: {}".format(dataContract.localSymbol))
            self.app.contract.update(dataContract.localSymbol)
        
            # my add
            nextday = datetime.now().day 
            nexthour = datetime.now().hour 
            if datetime.now().minute < 15:
                nextqtr = 15
                getqtr = 30
            elif datetime.now().minute < 30:
                nextqtr = 30
                getqtr = 45
            elif datetime.now().minute < 45:
                 nextqtr = 45
                 getqtr = 0
            else:
                nexthour = nexthour + 1
                nextqtr = 0
                getqtr = 15
            test=(datetime(int(date.today().year),int(date.today().month),int(nextday),int(nexthour),int(getqtr),int(0)))
            print ("nextqtr and getqtr")
            print (nextqtr)
            print (getqtr)
            log.info("next datetime for 15 minutes - should be 15 minutes ahead of desired nextqtr{}".format(test))
            #
            #nextqtr = datetime.now().minute + 1
            #print ("we manually overwrote start time")
            #print (nextqtr)
            #
            self.ib.waitUntil(time(hour=nexthour,minute=nextqtr))
            # 15 Minute Data
            self.app.qtrhour.update(datetime.now())
            print(datetime.now())
            log.info("requesting info for the following timeframe today: {} nexthour: {} minutes: {}".format(date.today().day,nexthour,getqtr))
            bars_15m = self.get_bars_data(dataContract,"2 D","15 mins",date.today().day,nexthour + 1,getqtr)
            x = np.array(bars_15m)
            log.debug("15 min bars {}".format(bars_15m))
            #sef.app. barupdateEvent_15m(baas_15m, True)
            #aars_15m.updateEvent += self.app.barupdateEvent_15m
            log.info("Got 15m data subscription")
            cci, avg, cci_prior, averageh, cci3 = calculate_cci(bars_15m)
            atr, atrprior =  calculate_atr(bars_15m)
            bband_width, bband_b,bband_width_prior, bband_b_prior = calculate_bbands(bars_15m)
            log.info("starting 15 minutes".format(datetime.now()))
            log.info("CCI:      {} ".format(cci))
            log.info("CCIA      {} ".format(avg))
            log.info("CCIP      {} ".format(cci_prior))
            log.info("CCIPA:    {} ".format(averageh))
            log.info("ATR:      {} ".format(atr))
            log.info("bband w:  {} ".format(bband_width))
            log.info("bband p:  {} ".format(bband_b))
            qtrtime = datetime.now()
            if (cci > cci_prior and cci_prior < cci3) or (cci < cci_prior and cci_prior > cci3):
                crossed = True
                csv_row = "'"+str(datetime.now())+",'long'"
            else:
                crossed = False
                csv_row = "'"+str(datetime.now())+",'short'"
            csv_row += ",'"+str(crossed)+"',"+str(cci)+","+str(avg)+","+str(cci_prior)+","+str(averageh)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            print(csv_row)
            stat = "check crossed statau"
            #print("printing self app ********************************************")
            #print(Indicator.data)
            self.app.status1.update(stat)
            self.app.crossover.update(crossed)
            self.app.cci15.update(f"{cci:.02f}")
            self.app.cci15_av.update(f"{avg:.02f}")
            self.app.cci15p_av.update(f"{averageh:.02f}")
            self.app.cci15p.update(f"{cci_prior:.02f}")
            self.app.atr15.update(f"{atr:.02f}")
            self.app.bband15_width.update(f"{bband_width:.04f}")
            self.app.bband15_b.update(f"{bband_b:.04f}")
            self.app.qtrhour.update(qtrtime)
            
            
            #1 hour data 
            test=(datetime(int(date.today().year),int(date.today().month),int(nextday),int(nexthour),int(getqtr),int(0)))
            log.info("next datetime for 1 hour - should be 1 hour behind current hour {}".format(test))
            bars_1h = self.get_bars_data(dataContract,"5 D","1 hour",date.today().day,nexthour,0)
            cci, avg, cci_prior, averageh, cci3 = calculate_cci(bars_1h)
            log.debug("bars_1h {}".format(bars_1h))
            atr,atrprior = calculate_atr(bars_1h)
            bband_width, bband_b,bband_width_prior, bband_b_prior = calculate_bbands(bars_1h)
            csv_row += ","+str(cci)+","+str(avg)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            log.info("starting 1H ")
            log.info("CCI       {} ".format(cci))
            log.info("CCIA:     {} ".format(avg))
            log.info("ATR:      {} ".format(atr))
            log.info("bband w:  {} ".format(bband_width))
            log.info("bband p:  {} ".format(bband_b))
            qtrtime = datetime.now()
            self.app.cci1h.update(f"{cci:.02f}")
            self.app.cci1h_av.update(f"{avg:.02f}")
            self.app.bband1h_b.update(f"{bband_b:.04f}")
            self.app.bband1h_width.update(f"{bband_width:.04f}")
            self.app.atr1h.update(f"{atr:.02f}")
            
            bars_1d = self.get_bars_data(dataContract,"75 D","1 day",nextday - 1, 0 ,0)
            log.debug("1d min bars {}".format(bars_1d))
            cci, avg, cci_prior, averageh, cci3 = calculate_cci(bars_1d)
            atr, atrprior = calculate_atr(bars_1d)
            bband_width, bband_b,bband_width_prior, bband_b_prior = calculate_bbands(bars_1d)
            csv_row += ","+str(cci)+","+str(avg)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            log.info("starting 1D ")
            log.info("CCIP      {} ".format(cci))
            log.info("CCIPA:    {} ".format(avg))
            log.info("ATR:      {} ".format(atr))
            log.info("bband w:  {} ".format(bband_width))
            log.info("bband p:  {} ".format(bband_b))
            qtrtime = datetime.now()
            qtrtime = datetime.now()
            self.app.cci1d.update(f"{cci:.02f}")
            self.app.cci1d_av.update(f"{avg:.02f}")
            self.app.bband1d_b.update(f"{bband_b:.04f}")
            self.app.bband1d_width.update(f"{bband_width:.04f}")
            self.app.atr1d.update(f"{atr:.02f}")
            with open('data/hist15.csv', mode='a') as hist15:
                histwriter = csv.writer(hist15, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                histwriter.writerow([csv_row])
    
    print ("end of run self")
    def get_bars_data(self, contract, bardur, tframe,nextday, nexthour, nextqtr):
        log.info ("inputs to request hist for get bars - {}/{}/{} {}:{}".format(date.today().year,date.today().month,nextday,nexthour,nextqtr))
        return self.ib.reqHistoricalData(
                contract=contract,
                endDateTime=datetime(int(date.today().year),int(date.today().month),int(nextday),int(nexthour),int(nextqtr),int(0)),
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
    #print (cci)
    #bars_debug = np.array(bars)
    #log.info("bars : %b" % bars)
    log.debug("cci array: {} ".format(cci))
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
    return contract[0].contract


