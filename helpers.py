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

def build_csv_bars_row(csv_row,IsEOF, IsBOF):
    if IsBOF:
        csv_row_sum = csv_row
    else:
        
        csv_row_sum += csv_row
    csv_header = "Date,Status,Crossed,CCI15,CCIA15,CCI15P,CCIA15P,ATR15,BBw15,BBB15"
    csv_header += ",CCI1h,CCIA1h,ATR1h,BBW1h,BBB1h"
    csv_header += ",CCI1d,CCIA1d,ATR1d,BBB1d,BBW1d"
    csv_header += ",CCIbbKey,CCIKey,CCI Trade,CCIbbTrade,pendingLong, pendingShort"
    if IsEOF:
        with open('data/hist15.csv', mode='a') as hist15:
                histwriter = csv.writer(hist15, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                histwriter.writerow([csv_header])
                histwriter.writerow([csv_row])
    return
