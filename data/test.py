import csv


status = "PendingSubit"
orderId = 12345
orderdet = "Trade(contract=Contract(secType='CONTFUT', conId=334144679, symbol='ES', lastTradeDateOrContractMonth='20191220', multiplier='50', exchange='GLOBEX', currency='USD', localSymbol='ESZ9', tradingClass='ES'), order=Order(orderId=425, action='BUY', totalQuantity=2, orderType='MKT', transmit=False, faProfile='cci_day', conditions=[], softDollarTier=SoftDollarTier()), orderStatus=OrderStatus(status='PendingSubmit'), fills=[], log=[TradeLogEntry(time=datetime.datetime(2019, 11, 13, 21, 15, 1, 363994, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='')])"
csv_row = str(orderdet) + ',' + str(orderId) + ',' + str(status)
with open('orders.csv', mode='a') as tradesCSV:
                        histwriter = csv.writer(tradesCSV, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        histwriter.writerow([csv_row])