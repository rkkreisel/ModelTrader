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
        tradenow = False
        cci_trade = False
        ccibb_trade = False
        while not_finished:
            print ("top of algo run self")
            crossed = False
            self.app.crossover.update(crossed)
            contContract = get_contract(self)
            dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
            log.info("Got Contract: {}".format(dataContract.localSymbol))
            self.app.contract.update(dataContract.localSymbol)
            wait_time, datetime_15, datetime_1h, datetime_1d = self.define_times()
            log.info("next datetime for 15 minutes - should be 15 minutes ahead of desired nextqtr{}".format(wait_time))
            #
            #nextqtr = datetime.now().minute + 1
            #print ("we manually overwrote start time")
            #print (nextqtr)
            #
            self.ib.waitUntil(wait_time)
            # 15 Minute Data
            self.app.qtrhour.update(wait_time)
            log.info("requesting info for the following timeframe today: {} ".format(wait_time))
            bars_15m = self.get_bars_data(dataContract,"2 D","15 mins",datetime_15)
            x = np.array(bars_15m)
            log.info("15 min bars {}".format(bars_15m[-1]))
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
            #key_arr = []
            if (cci > cci_prior and cci_prior < cci3) or (cci < cci_prior and cci_prior > cci3):
                crossed = True
                tradenow = True
                csv_row = "'"+str(datetime.now())+",'long'"
                key_arr[0] = "long"
            else:
                crossed = True
                tradenow = True
                csv_row = "'"+str(datetime.now())+",'short'"
                key_arr[0] = "short"
            csv_row += ",'"+str(crossed)+"',"+str(cci)+","+str(avg)+","+str(cci_prior)+","+str(averageh)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            print(key_arr)
            key_arr[1] = categories.categorize_atr15(atr)
            key_arr[4] = categories.categorize_cci_15(cci)
            key_arr[5] = categories.categorize_cci_15_avg(avg)
            key_arr[8] = categories.categorize_BBW15(bband_width)
            key_arr[9] = categories.categorize_BBb15(bband_b)
            stat = "check crossed status"

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
            log.info("next datetime for 1 hour - should be 1 hour behind current hour {}".format(datetime_1h))
            bars_1h = self.get_bars_data(dataContract,"5 D","1 hour",datetime_1h)
            cci, avg, cci_prior, averageh, cci3 = calculate_cci(bars_1h)
            log.info("bars_1h {}".format(bars_1h[-1]))
            atr,atrprior = calculate_atr(bars_1h)
            bband_width, bband_b,bband_width_prior, bband_b_prior = calculate_bbands(bars_1h)
            csv_row += ","+str(cci)+","+str(avg)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            key_arr[2] = categories.categorize_atr1h(atr)
            key_arr[6] = categories.categorize_cci_1h(avg)
            key_arr[10] = categories.categorize_BBW1h(bband_width)
            key_arr[11] = categories.categorize_BBb1h(bband_b)
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
            
            log.info("requesting info for the following timeframe today: nextday: ".format(datetime_1d))
            bars_1d = self.get_bars_data(dataContract,"75 D","1 day",datetime_1d)
            log.info("1d min bars {}".format(bars_1d[-1]))
            cci, avg, cci_prior, averageh, cci3 = calculate_cci(bars_1d)
            atr, atrprior = calculate_atr(bars_1d)
            bband_width, bband_b,bband_width_prior, bband_b_prior = calculate_bbands(bars_1d)
            csv_row += ","+str(cci)+","+str(avg)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            key_arr[3] = categories.categorize_atr1d(atr)
            key_arr[7] = categories.categorize_cci_1d(avg)
            key_arr[12] = categories.categorize_BBW1d(bband_width)
            key_arr[13] = categories.categorize_BBb1d(bband_b)
            log.info("starting 1H ")
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
            if tradenow:
                csv_file = csv.reader(open('data/ccibb.csv', "rt"), delimiter = "'")
                for row in csv_file:
                    if (''.join(key_arr)) == row[0]:
                            print("we have a match in ccibb.csv")
                            print("found a match in CCIBB ",row)
                            status_done = self.row_results(self, row)
                            ccibb_trade = True
                csv_file = csv.reader(open('data/cci.csv', "rt"), delimiter = "'")
                for row in csv_file:
                    if (''.join(key_arr[0:7])) == row[0]:
                            print("we have a match in cci.csv")
                            print("found a math in CCI ",row)
                            status_done = self.row_results(self, row)
                            cci_trade = True
            csv_row += ","+(''.join(key_arr))+","+str(ccibb_trade)+","+str(ccibb_trade)
            with open('data/hist15.csv', mode='a') as hist15:
                histwriter = csv.writer(hist15, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                histwriter.writerow([csv_row])
            print ("*******************************************key array comming *************************")
            print (''.join(key_arr))
            log.info("key array {}".format(key_arr))
            #key_arr.clear()
            tradenow = False
            cci_trade = False
            ccibb_trade = False
            print ("end of run self **********************************************************************************************")

    def get_bars_data(self, contract, bardur, tframe,bar_datetime):
        log.info ("inputs to request hist for get bars - {}".format(bar_datetime))
        return self.ib.reqHistoricalData(
                contract=contract,
                endDateTime=bar_datetime,
                durationStr=bardur,
                barSizeSetting=tframe,
                whatToShow="TRADES",
                useRTH=False,
                keepUpToDate=False
        )
    
    def define_times(self):
        current_time = datetime.now()
        current_minute = datetime.now().minute
        print("now ",current_time)
        print("minute ",current_minute)
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
        #datetime_1h = wait_time - timedelta(hours = 1)
        datetime_1h = wait_time.replace(minute=0)
        datetime_1d = current_time -  timedelta(days = 1)
        datetime_1d = datetime_1d.replace(hour = 0, minute=0, second=0)
        print("wait time",wait_time)
        print("datetime_15 ",datetime_15)
        print("datetime_1h",datetime_1h)
        print("datetime_1d",datetime_1d)
        return wait_time, datetime_15, datetime_1h, datetime_1d

    def row_results(self, row):
        log.info("Do we buy this one: {}".format)(row[13])
        log.info("Winning %: {}".format(row[11]))
        log.info("Previous Order: {}".format(row[6]))
        log.info("Previous Wins: {}".format(row[7]))
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
    #print (cci)
    #bars_debug = np.array(bars)
    #log.info("bars : %b" % bars)
    #log.debug("cci array: {} ".format(cci))
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


