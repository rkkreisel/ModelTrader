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
        pendinglong = False
        tradenow = False
        cci_trade = False
        ccibb_trade = False
        while not_finished:
            print ("top of algo run self")
            #top of logic - want to check status as we enter a new bar/hour/day/contract
            crossed = False
            self.app.crossover.update(crossed)
            contContract, contracthours = get_contract(self)
            # NEW
            tradeContract = self.ib.qualifyContracts(contContract)   # gives all the details of a contract so we can trade it
            #print("fully qualified trading Contract: ",tradeContract)
            positions = self.ib.positions()
            open = self.have_position(positions)
            open_today = helpers.is_open_today(contracthours)
            dataContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol=contContract.localSymbol)
            log.info("Got Contract: {}".format(dataContract.localSymbol))
            self.app.contract.update(dataContract.localSymbol)
            wait_time, datetime_15, datetime_1h, datetime_1d = self.define_times()
            log.info("next datetime for 15 minutes - should be 15 minutes ahead of desired nextqtr{}".format(wait_time))
            #
            # starting the analysis section
            #
            self.ib.waitUntil(wait_time)
            #
            # 15 Minute Data
            #
            self.app.qtrhour.update(wait_time)
            log.info("requesting info for the following timeframe today: {} ".format(wait_time))
            bars_15m = self.get_bars_data(dataContract,"2 D","15 mins",datetime_15)
            x = np.array(bars_15m)
            log.info("15 min bars {}".format(bars_15m[-1]))
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
            if cci > avg and cci_prior < averageh:
                crossed = True
                print("crossed long",crossed)
                tradenow = True
                csv_row = "'"+str(datetime.now())+",'long'"
                key_arr[0] = "long"
            elif cci < avg and cci_prior > averageh:
                crossed = True
                tradenow = True
                print("crossed short",crossed)
                csv_row = "'"+str(datetime.now())+",'short'"
                key_arr[0] = "short"
            else:
                csv_row = "'"+str(datetime.now())+",'cash'"
                crossed = False
                tradenow = False
                print("NOT CROSSED ",crossed)
            print("csv row crossed ",csv_row)
            #if abs(cci - avg) > config.SPREAD:
            #    pending = True
            csv_header = "Date,Status,Crossed,CCI15,CCIA15,CCI15P,CCIA15P,ATR15,BBw15,BBB15"
            csv_row += ",'"+str(crossed)+"',"+str(cci)+","+str(avg)+","+str(cci_prior)+","+str(averageh)+","+str(atr)+","+str(bband_width)+","+str(bband_b)
            print("csv row 15",csv_row)
            key_arr[1] = categories.categorize_atr15(atr)
            key_arr[4] = categories.categorize_cci_15(cci)
            key_arr[5] = categories.categorize_cci_15_avg(avg)
            key_arr[8] = categories.categorize_BBW15(bband_width)
            key_arr[9] = categories.categorize_BBb15(bband_b)
            stat = "check crossed status"

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
            print("csv row 1 hour ",csv_row)
            csv_header += ",CCI1h,CCIA1h,ATR1h,BBW1h,BBB1h"
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
            print("csv row daily ",csv_row)
            csv_header += ",CCI1d,CCIA1d,ATR1d,BBB1d,BBW1d"
            key_arr[3] = categories.categorize_atr1d(atr)
            key_arr[7] = categories.categorize_cci_1d(avg)
            key_arr[12] = categories.categorize_BBW1d(bband_width)
            key_arr[13] = categories.categorize_BBb1d(bband_b)
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
            print("tradenow: ",tradenow)
            if tradenow:
                print("Tradeing this bar ",(''.join(key_arr))," - ",''.join(key_arr[0:8]))
                csv_file1 = csv.reader(open('data/ccibb.csv', "rt"), delimiter = ",")
                for row1 in csv_file1:
                    print("ccibb row: ",row1[0])
                    if ((''.join(key_arr)) == row1[0]):
                            log.info("we have a match in ccibb.csv")
                            print("found a match in CCIBB ",row1[0])
                            ccibb_trade = True
                            tradenow = False
                            status_done = self.row_results(row1,cci_trade,ccibb_trade)
                            break
                csv_file2 = csv.reader(open('data/cci.csv', "rt"), delimiter = ",")
                for row2 in csv_file2:
                    print("cci row: ",row2[0])
                    if ((''.join(key_arr[0:8])) == row2[0]):
                            print("we have a match in cci.csv")
                            print("found a math in CCI ",row2[0])
                            cci_trade = True
                            tradenow = False
                            status_done = self.row_results(row2,cci_trade,ccibb_trade)
                            break
            print("did we find a match?  If true than no ",tradenow)
            csv_row += ","+(''.join(key_arr))+","+(''.join(key_arr[0:8]))+","+str(cci_trade)+","+str(ccibb_trade)+","+str(pendinglong)+","+str(pendingshort)
            csv_header += ",CCIbbKey,CCIKey,CCI Trade,CCIbbTrade,Pending Long, Pending Short"
            print("csv row right before csv write ",csv_row)
            with open('data/hist15.csv', mode='a') as hist15:
                histwriter = csv.writer(hist15, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                #histwriter.writerow([csv_header])
                #histwriter.writerow([csv_row])
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
        datetime_15 = current_time.replace(minute = 45, second=0)
        if current_minute < 15:
            wait_time = current_time.replace(minute = 15,second=0) 
            datetime_15 = current_time.replace(minute = 30, second = 0)
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
        print("wait time",wait_time)
        print("datetime_15 ",datetime_15)
        print("datetime_1h",datetime_1h)
        print("datetime_1d",datetime_1d)
        return wait_time, datetime_15, datetime_1h, datetime_1d

    def row_results(self, row, cci_trade, ccibb_trade):
        print("************************************************")
        print("* CCI Trade:          ",cci_trade)
        print("* CCIbb Trade:        ",ccibb_trade)
        print("* Do we buy this one: ",row[13])
        print("* Profit:             ",row[5])
        print("* Winning %:          ",row[11]*100)
        print("* Risk:               ",row[12]*100)
        print("* Previous Order:     ",row[6])
        print("* Previous Wins:      ",row[7])
        print("************************************************")
        return

    def have_position(self,positions):
        position_tf = False
        print("positions",positions)
        x = 0
        while x < len(positions):
            if (positions[x][1].symbol) == "ES": 
                position_tf = True 
                break
            x += + 1
        return position_tf 

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
        percentb = (bars[-1].close - low[-1]) / (up[-1] - low[-1]) * 100
        widthprior = (up[-2] - low[-2]) / sma[-2] * 100
        percentbprior = (bars[-2].close - low[-2]) / (up[-2] - low[-2]) * 100
    return width, percentb, widthprior, percentbprior

