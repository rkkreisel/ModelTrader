from re import compile as compile_re
from datetime import datetime, timedelta

contracthours = "20191225:1700-20191226:1515;20191226:1530-20191226:1600;20191226:1700-20191227:1515;20191227:1530-20191227:1600;20191228:CLOSED;20191229:1700-20191230:1515;20191230:1530-20191230:1600;20191230:1700-20191231:1515;20191231:1530-20191231:1600;20200101:1700-20200102:1515;20200102:1530-20200102:1600;20200102:1700-20200103:1515;20200103:1530-20200103:1600;20200104:CLOSED;20200105:1700-20200106:1515;20200106:1530-20200106:1600;20200106:1700-20200107:1515;20200107:1530-20200107:1600;20200107:1700-20200108:1515;20200108:1530-20200108:1600;20200108:1700-20200109:1515;20200109:1530-20200109:1600;20200109:1700-20200110:1515;20200110:1530-20200110:1600;20200111:CLOSED;20200112:1700-20200113:1515;20200113:1530-20200113:1600;20200113:1700-20200114:1515;20200114:1530-20200114:1600;20200115:1700-20200116:1515;20200116:1530-20200116:1600;20200116:1700-20200117:1515;20200117:1530-20200117:1600;20200118:CLOSED;20200119:1700-20200120:1515;20200120:1530-20200120:1600;20200120:1700-20200121:1515;20200121:1530-20200121:1600;20200122:1700-20200123:1515;20200123:1530-20200123:1600;20200123:1700-20200124:1515;20200124:1530-20200124:1600;20200125:CLOSED;20200126:1700-20200127:1515;20200127:1530-20200127:1600;20200127:1700-20200128:1515;20200128:1530-20200128:1600;20200129:CLOSED"
#print("contract hours",contracthours)
date_re = compile_re(r"([0-9]{8}):([0-9]+)-([0-9]{8}):([0-9]+)")
#print("date_re: ",date_re)
days = contracthours.split(";")                         #parse the list
today = datetime.today().strftime("%Y%m%d")             #today in fomat matching the list
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y%m%d")
print("yesterday: ",yesterday)
print("today:     ",today)
print("tomorrow:  ",tomorrow)
hours = []

for day in days:
#    print("day",day)
    match = date_re.match(day)
    print("date re: ",date_re.match(day))
    if not match: continue
    if match.group(1) not in [today, yesterday]: continue
    if match.group(3) not in [today, yesterday]: continue
    hours += ["{0}-{1}".format(match.group(2), match.group(4))]

    with open('data/TradingTimesTable.csv', mode='a', newline = '') as csvFile:
        fieldnames = ['Date','Open','RegularHours','AfterHours']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        histwriter.writeheader()
        histwriter.writerow({'Order_Id': orderId, 'Order': orderInfo, 'Status': status, 'Date_Pending': time, 'Date_Cancelled': '1/1/20', 'Date_Filled': datetime.now()})


    with open('data/TradingTimesTable.csv', newline ='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
