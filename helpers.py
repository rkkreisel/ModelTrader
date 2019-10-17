"""
    ModelTrader Helper Functions
"""
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from re import compile as compile_re
from ib_insync.contract import Contract
import csv
import config


def is_open_today(contracthours: Contract):
    # a return of NONE is when the market is not opern for the given day
    """ Parse contract Trading Hours to Check if Valid Trading Day"""
    date_re = compile_re(r"([0-9]{8}):([0-9]+)-([0-9]{8}):([0-9]+)")
    days = contracthours.split(";")                         #parse the list
    today = datetime.today().strftime("%Y%m%d")             #today in fomat matching the list
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y%m%d")
    #print("yesterday: ",yesterday)
    #print("today:     ",today)
    #print("tomorrow:  ",tomorrow)
    hours = []

    for day in days:
        match = date_re.match(day)
        #print("date re: ",date_re.match(day))
        if not match: continue
        if match.group(1) not in [today, yesterday]: continue
        if match.group(3) not in [today, yesterday]: continue
        hours += ["{0}-{1}".format(match.group(2), match.group(4))]

    today_hours = ",".join(hours)
    print("todays trading hours are: ",today_hours)

    csv_file = csv.reader(open('data/tradinghours.csv', "rt"), delimiter = ",")
    hours_found = False
    for row in csv_file:
        if today_hours == row[0]:
            hours_found = True
            break
    if not hours_found:
        with open('data/tradinghours.csv', mode='a') as tradehours:
            histwriter = csv.writer(tradehours, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            histwriter.writerow([today_hours])
        
    if today_hours == config.NORMAL_TRADING_HOURS:
        return True
    return False

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

def build_csv_bars_row(wait_time, tradeAction, bars_15m, bars_1h, bars_1d, pendingLong, pendingShort, pendingCnt, tradeNow):
    #csv_header = "Time,Status,Crossed,CCI15,CCIA15,CCI15P,CCIA15P,ATR15,BBw15,BBB15"
    csv_header = 'wait_time,tradeAction,'
    csv_header += 'bars_15m.cci,bars_15m.ccia,bars_15m.atr,bars_15m.bband_width,bars_15m.bband_b,'
    csv_header += 'bars_1h.cci,bars_1h.ccia,bars_1h.atr,bars_1h.bband_width,bars_1h.bband_b,'
    csv_header += 'bars_1d.cci,bars_1d.ccia,bars_1d.atr,bars_1d.bband_width,bars_1d.bband_b,'
    csv_header += 'tradeAction,tradeNow,pendingLong,pendingShort,pendingCnt'
    csv_row = "'"+str(wait_time) + ',' + tradeAction + ','
    csv_row += str(bars_15m.cci) + ',' + str(bars_15m.ccia) + ',' + str(bars_15m.atr + ','+str(bars_15m.bband_width) +','+str(bars_15m.bband_b) + ','
    csv_row += str(bars_1h.cci) + ',' + str(bars_1h.ccia) + ',' + str(bars_1h.atr + ','+str(bars_1h.bband_width) +','+str(bars_1h.bband_b) + ','
    csv_row += str(bars_1d.cci) + ',' + str(bars_1d.ccia) + ',' + str(bars_1d.atr + ','+str(bars_1d.bband_width) +','+str(bars_1d.bband_b) + ','
    csv_row += tradeAction + ',' + tradeNow +','+ str(pendingLong) +','+ str(pendingShort) +','+ str(pendingCnt)
    with open('data/hist15.csv', mode='a') as hist15:
            histwriter = csv.writer(hist15, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            histwriter.writerow([csv_header])
            histwriter.writerow([csv_row])
    return True