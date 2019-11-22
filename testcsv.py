import csv
import sys
import datetime


orderInfo = "Trade(contract=Contract(secType='CONTFUT', conId=334144679, symbol='ES', lastTradeDateOrContractMonth='20191220', multiplier='50', exchange='GLOBEX', currency='USD', localSymbol='ESZ9', tradingClass='ES'), order=Order(orderId=157, action='SELL', totalQuantity=2, orderType='MKT', transmit=False, faProfile='cci_day', conditions=[], softDollarTier=SoftDollarTier()), orderStatus=OrderStatus(status='PendingSubmit'), fills=[], log=[TradeLogEntry(time=datetime.datetime(2019, 11, 21, 20, 45, 0, 583844, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='')])"
print(orderInfo.order())
print("/n orderinf0 \n")
print(orderInfo.log)
print("orderid {a} order {b} order status {c}".format(a=orderInfo.orderStatus.status,b=orderStatus.status,c=orderInfo.orderStatus.status))

with open('data/orders.csv', mode='a', newline = '') as ordersCSV:
            fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled']
            histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)

            histwriter.writeheader()
            histwriter.writerow({'Order_Id': str(orderInfo.order.orderId), 'Order': orderInfo, 'Status': orderInfo.orderStatus.status, 'Date_Pending': '1/1/20', 'Date_Cancelled': '1/1/20', 'Date_Filler': '1/1/20'})

#key = "shortATR15:AATR1:AATRD:ACCI15:OCCIA15:OCCIA1h:ILCCIA1d:ILBBW15:HBBb15:TBBW1h:ABBb1h:OBBW1d:HBBb1d:T"

#csv_file = csv.reader(open('data/ccibb.csv', "rt"), delimiter=",")
#for row in csv_file:
#    #print(row[0])
#    if key == row[0]:
#        print("match: ",row[0])
#        break
#key = "longATR15:LATR1:AATRD:ACCI15:ILCCIA15:UCCIA1h:IUCCIA1d:O"
#csv_file = csv.reader(open('data/cci.csv', "rt"), delimiter=",")
#for row in csv_file:
#    #print(row[0])
#    if key == row[0]:
#        print("match ***********************************************************************************: ",row[0])
#        break




#with open('employee_file.csv', mode='a') as employee_file:
#    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

 #   employee_writer.writerow(['John Smith', 'Accounting', 'November'])
  #  employee_writer.writerow(['Erica Meyers', 'IT', 'March'])
   # employee_writer.writerow([test])
