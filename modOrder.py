from ib_insync import IB
from ib_insync.contract import ContFuture, Contract 
from ib_insync.objects import BarDataList
import datetime
import asyncio
import time
import categories
import orders
import config
import logger
import logic
from indicator import Indicator

ib = IB()
ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID)

buyPrice = '3023.25'

contract = ib.reqContractDetails(
        ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
    )

openOrdersList = ib.openOrders()
print("contract",contract)
print("open orders",openOrdersList)
print("length of orders ",len(openOrdersList))
x = 0
# not sure we need to differentiate between buy or sell stop orders below
while x < len(openOrdersList):
    #symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,openOrdersList[x])
    #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
    #log.info("closeOpenOrder: - we have open order records: opendOrderId: {ooi} orderType: {ot} ".format(ooi=orderId, ot=orderType))
    print(" blank ")
    print("closeOpenOrder: closing all open orders - currently working on: ",openOrdersList[x])
    #trademkt = ib.cancelOrder(openOrdersList[x])            # don't need to place order when cancelling
    #print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
    print("----------------------- TRADEMKT ---------------: ",openOrdersList)
    #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
    #orderId, orderType, action, quantity = orders.parseOrderString(ib,openOrdersList)      
    #checkOrderStatus = updateCanceledOpenOrders(ib, orderId, trademkt)   # update each order that we cancelled
    print("action ",openOrdersList[x].order.action)
    #if openOrdersList[x].order.action = "SELL"
        #openOrdersList

    x += 1
    print(" x is ",x)