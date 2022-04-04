"""
    ModelTrader Helper Functions
"""
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, date, time
#import datetime
from re import compile as compile_re
from ib_insync.contract import Contract
import csv
import config
import os
import logger

log = logger.getLogger()

def is_open_today(contracthours: Contract):
    # a return of NONE is when the market is not opern for the given day
    """ Parse contract Trading Hours to Check if Valid Trading Day"""
    #rint("contract hours",contracthours)
    date_re = compile_re(r"([0-9]{8}):([0-9]+)-([0-9]{8}):([0-9]+)")
    #rint("date_re: ",date_re)
    days = contracthours.split(";")                         #parse the list
    today = datetime.today().strftime("%Y%m%d")             #today in fomat matching the list
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y%m%d")
    hours = []
    tradingDayType, tradingDayRules, currentTimeFrame = checkDayType(today)
    log.debug("Trading date: {td} day type: {dt}".format(td=today,dt=tradingDayType))
    for day in days:
        match = date_re.match(day)
        #rint("date re: ",date_re.match(day))
        if not match: continue
        if match.group(1) not in [today, yesterday]: continue
        if match.group(3) not in [today, yesterday]: continue
        hours += ["{0}-{1}".format(match.group(2), match.group(4))]

    today_hours = ",".join(hours)
    log.debug("todays trading hours are: {th}".format(th=today_hours))

    #csv_file = csv.reader(open('data/tradinghours.csv', "rt"), delimiter = ",")
    #hours_found = False
    #for row in csv_file:
    #    if today_hours == row[0]:
    #        hours_found = True
    #        break
    #if not hours_found:
    #    with open('data/tradinghours.csv', mode='a') as tradehours:
    #        histwriter = csv.writer(tradehours, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #        histwriter.writerow([today_hours])
        
    if today_hours == config.NORMAL_TRADING_HOURS:
        return True, tradingDayRules, currentTimeFrame
    return False, tradingDayRules, currentTimeFrame

def checkDayType(checkDate):
    log.debug("checkDayTYpe: {c}".format(c=checkDate))
    with open('data/tradingday.csv', 'r') as csvfile:
        header = ['Today','DayType']
        reader = csv.DictReader(csvfile, fieldnames = header, delimiter = ',')
        #reader = csv.DictReader(csvfile)
        dayType = False
        for row in reader:
            log.debug("checkDate: {cd} today: {t} DayType {dt}".format(cd=checkDate,t=row['Today'],dt=row['DayType']))
            if checkDate == row['Today']: 
                log.debug("we have a match in tradingday.csv: {td}".format(td=row['DayType']))
                dayType = row['DayType']
                break
    currentTimeFrame = "Pre Market Hours"
    if dayType != False:
        with open('data/tradingdayrules.csv', 'r') as csvfile:
            header = ['Today','DayStartHour','DayStartMin','DayStopHour','DayStopMin','NightStartPreHour','NightStartPreMin','NightStopPreHour','NightStopPreMin','NightStartPostHour','NightStartPostMin','NightStopPostHour','NightStopPostMin']
            reader = csv.DictReader(csvfile, fieldnames = header, delimiter = ',')
            for row in reader:
                log.debug("Today: {to} row {t}".format(to=row['Today'],t=row))
                if dayType == row['Today']: 
                    #rint("Today ",row['Today'])
                    #rint("DayStartHour ",row['DayStartHour'])
                    #rint("DayStartMin ",row['DayStartMin'])
                    #rint("DayStopHour ",row['DayStopHour'])
                    #rint("DayStopMin ",row['DayStopMin'])
                    #rint("'NightStartPreHour' ",row['NightStartPreHour'])
                    #rint("'NightStartPreMin' ", row['NightStartPreMin'])
                    #rint("'NightStopPreHour' ",row['NightStopPreHour'])
                    #rint("'NightStopPreMin' ",row['NightStopPreMin'])
                    #rint("'NightStartPostHour' ",row['NightStartPostHour'])
                    #rint("'NightStartPostMin' ", row['NightStartPostMin'])
                    #rint("'NightStopPostHour' ",row['NightStopPostHour'])
                    #rint("'NightStopPostMin' ",row['NightStopPostMin'])
                    log.debug("we have a match in tradingdayrules.csv: {td}".format(td=row))
                    #
                    nightPreStart = datetime.now()
                    nightPreStart = nightPreStart.replace(hour=int(row['NightStartPreHour']),minute=int(row['NightStartPreMin']))
                    nightPreStop = datetime.now()
                    nightPreStop = nightPreStop.replace(hour=int(row['NightStopPreHour']),minute=int(row['NightStopPreMin']))
                    currentTimeFrame = ""
                    if datetime.now() >= nightPreStart and datetime.now() <= nightPreStop:
                        currentTimeFrame = "Pre Market Hours"
                    #
                    dayStart = datetime.now()
                    dayStart = dayStart.replace(hour=int(row['DayStartHour']),minute=int(row['DayStopMin']))
                    dayStop = datetime.now()
                    dayStop = dayStop.replace(hour=int(row['DayStopHour']),minute=int(row['DayStopMin']))
                    if datetime.now() >= dayStart and datetime.now() <= dayStop:
                        currentTimeFrame = "Market Hours"
                    #
                    nightPostStart = datetime.now()
                    nightPostStart = nightPostStart.replace(hour=int(row['NightStartPostHour']),minute=int(row['NightStartPostMin']))
                    nightPostStop = datetime.now()
                    nightPostStop = nightPostStop.replace(hour=int(row['NightStopPostHour']),minute=int(row['NightStopPostMin']))
                    if datetime.now() >= nightPostStart and datetime.now() <= nightPostStop:
                        currentTimeFrame = "After Market Hours"
                    log.debug("Market hours are currently: {d}".format(d=currentTimeFrame))
                    dayTypeRules = row
                    break    
    return dayType, row, currentTimeFrame

def parseAdvisorConfig(xml):
    """ Get # Of Contracts from Current Advisor Profile """
    root = ET.fromstring(xml)
    profileTag = None
    for profile in  root.getchildren():
        for attrib in profile.getchildren():
            if attrib.tag == 'name':
                if attrib.text.lower() == config.ALLOCATION_PROFILE.lower():
                   profileTag = profile
    if not profileTag: return None

    allocations = None
    for attrib in profileTag.getchildren():
        if attrib.tag == "ListOfAllocations":
            allocations = attrib
    if not allocations: return None 
    
    amount = 0
    for allocation in allocations.getchildren():
        for attrib in allocation:
             if attrib.tag == "amount":
                 amount += int(float(attrib.text))
    return amount

def build_csv_bars_row(wait_time, tradeAction, bars_15m, bars_1h, bars_1d, pendingLong, pendingShort, pendingCnt, tradeNow, ccibb_trade, cci_trade, ccibb_key, cci_key):
    #csv_header = "Time,Status,Crossed,CCI15,CCIA15,CCI15P,CCIA15P,ATR15,BBw15,BBB15"
    if os.stat("data/hist15.csv").st_size < 50:
        csv_header = 'wait_time,tradeAction,'
        csv_header += 'bars_15m.cci,bars_15m.ccia,bars_15m.atr,bars_15m.bband_width,bars_15m.bband_b,'
        csv_header += 'bars_1h.cci,bars_1h.ccia,bars_1h.atr,bars_1h.bband_width,bars_1h.bband_b,'
        csv_header += 'bars_1d.cci,bars_1d.ccia,bars_1d.atr,bars_1d.bband_width,bars_1d.bband_b,'
        csv_header += 'tradeNow,pendingLong,pendingShort,pendingCnt,curr_spread,prior_spread,'
        csv_header += 'ccibb_trade,cci_trade,ccibb_key, cci_key'
        with open('data/hist15.csv', mode='a') as hist15:
            histwriter = csv.writer(hist15, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            histwriter.writerow([csv_header])
    csv_row = str(wait_time) + ',' + tradeAction + ','
    csv_row += str(bars_15m.cci) + ',' + str(bars_15m.ccia) + ',' + str(bars_15m.atr) + ',' + str(bars_15m.bband_width) + ',' + str(bars_15m.bband_b) + ','
    csv_row += str(bars_1h.cci)  + ',' + str(bars_1h.ccia) + ',' + str(bars_1h.atr) + ',' + str(bars_1h.bband_width) + ',' + str(bars_1h.bband_b) + ','
    csv_row += str(bars_1d.cci)  + ',' + str(bars_1d.ccia) + ',' + str(bars_1d.atr) + ',' + str(bars_1d.bband_width) + ',' + str(bars_1d.bband_b) + ','
    csv_row += str(tradeNow) +','+ str(pendingLong) +','+ str(pendingShort) + ',' + str(pendingCnt) + ','
    csv_row += str(abs(bars_15m.cci-bars_15m.ccia)) + ',' + str(abs(bars_15m.cci_prior-bars_15m.ccia_prior)) + ',' + str(ccibb_trade) + ',' + str(cci_trade) + ','
    csv_row += str(ccibb_key) + ',' + str(cci_key)
    with open('data/hist15.csv', mode='a') as hist15:
            histwriter = csv.writer(hist15, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            histwriter.writerow([csv_row])
    return True

def isNaN(num):
    return num != num