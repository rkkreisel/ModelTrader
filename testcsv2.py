import csv
import sys
import datetime

key = "Trade(contract=Contract(secType='CONTFUT', conId=334144679, symbol='ES', lastTradeDateOrContractMonth='20191220', multiplier='50', exchange='GLOBEX', currency='USD', localSymbol='ESZ9', tradingClass='ES'), order=Order(orderId=204, action='SELL', totalQuantity=2, orderType='MKT', transmit=False, faProfile='cci_day', conditions=[], softDollarTier=SoftDollarTier()), orderStatus=OrderStatus(status='PendingSubmit'), fills=[], log=[TradeLogEntry(time=datetime.datetime(2019, 11, 15, 2, 0, 0, 528416, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='')]),204,PendingSubmit updatedOrders[x1]: Trade(contract=Future(conId=334144679, symbol='ES', lastTradeDateOrContractMonth='20191220', right='?', multiplier='50', exchange='GLOBEX', currency='USD', localSymbol='ESZ9', tradingClass='ES', comboLegs=[]), order=Order(orderId=205, permId=1938982782, action='BUY', totalQuantity=2, orderType='STP', lmtPrice=0.0, auxPrice=3101.75, tif='DAY', ocaGroup='1938982781', ocaType=3, rule80A='0', trailStopPrice=3101.75, faProfile='cci_day', openClose='C', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, clearingIntent='IB', orderComboLegs=[], adjustedOrderType='None', conditions=[], softDollarTier=SoftDollarTier(), dontUseAutoPriceForHedge=True), orderStatus=OrderStatus(status='PreSubmitted', remaining=2.0, permId=1938982782, whyHeld='locate,trigger'), fills=[], log=[TradeLogEntry(time=datetime.datetime(2019, 11, 15, 11, 35, 38, 757972, tzinfo=datetime.timezone.utc), status='PreSubmitted', message='')])"

#csv_file = csv.reader(open('data/testcsv.csv', "rt"), delimiter="\t")
#csv_row = key + '\t' + "Open" + '\t' + "12345"
with open('data/testcsv.csv', 'a', newline='') as positionsCSV:
	fieldnames = ['Order','Order_ID','Order_Status']
	histwriter = csv.DictWriter(positionsCSV, fieldnames = fieldnames)
	
	histwriter.writeheader()
	histwriter.writerow({'Order': key, 'Order_ID': '12345', 'Order_Status': 'PendingSubmit'})


with open('data/testcsv.csv', newline ='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row['Order'],'\n', row['Order_ID'],'\n', row['Order_Status'])
		

#for row in csv_file:
    #print(row[0])
#    if key == row[0]:
 #       print("match: ",row[0])
  #      break
#key = "longATR15:LATR1:AATRD:ACCI15:ILCCIA15:UCCIA1h:IUCCIA1d:O"
#csv_file = csv.reader(open('data/testcsv.csv', "rt"))
#for row in csv_file:
#    splitrow = row.split("\t")
#    print(row)
#    print("row split ",row.split('\t'))
    #print(row[1])
    #print(row[2])



#with open('employee_file.csv', mode='a') as employee_file:
#    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

 #   employee_writer.writerow(['John Smith', 'Accounting', 'November'])
  #  employee_writer.writerow(['Erica Meyers', 'IT', 'March'])
   # employee_writer.writerow([test])


orderInfo = "Trade(contract=Contract(secType='CONTFUT', conId=334144679, symbol='ES', lastTradeDateOrContractMonth='20191220', multiplier='50', exchange='GLOBEX', currency='USD', localSymbol='ESZ9', tradingClass='ES'), order=Order(orderId=157, action='SELL', totalQuantity=2, orderType='MKT', transmit=False, faProfile='cci_day', conditions=[], softDollarTier=SoftDollarTier()), orderStatus=OrderStatus(status='PendingSubmit'), fills=[], log=[TradeLogEntry(time=datetime.datetime(2019, 11, 21, 20, 45, 0, 583844, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='')])"

with open('data/orders.csv', mode='a', newline = '') as ordersCSV:
            fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled']
            histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)

            histwriter.writeheader()
            histwriter.writerow({'Order_Id': orderInfo.order.orderId, 'Order': orderInfo.order, 'Status': orderInfo.orderStatus.status, 'Date_Pending': '1/1/20', 'Date_Cancel