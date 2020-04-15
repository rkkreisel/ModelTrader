from ib_insync import IB
from ib_insync.order import Order
from ib_insync.contract import ContFuture, Future
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

buyPrice = '2770.75'

contContract = ib.reqContractDetails(ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE))
tradeContract = contContract[0].contract
print("tradecontract ",tradeContract)
print("")
#contract = ib.Future(symbol = contract.symbol)
#print("contract for symbol",contract)
print("")
openOrdersList = ib.openOrders()
#print("contract",contract)
print("open orders",openOrdersList)
print("open orders",ib.openTrades())
print("open trades ",ib.trades())
print("orders ",ib.orders())
print("length of orders ",len(openOrdersList))
x = 0
# not sure we need to differentiate between buy or sell stop orders below
while x < len(openOrdersList):
    #symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,openOrdersList[x])
    #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
    #log.info("closeOpenOrder: - we have open order records: opendOrderId: {ooi} orderType: {ot} ".format(ooi=orderId, ot=orderType))
    print(" blank ")
    #print("closeOpenOrder: closing all open orders - currently working on: ",openOrdersList[x])
    #trademkt = ib.cancelOrder(openOrdersList[x])            # don't need to place order when cancelling
    #print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
    print("----------------------- TRADEMKT ---------------: ",openOrdersList)
    #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
    #orderId, orderType, action, quantity = orders.parseOrderString(ib,openOrdersList)      
    #checkOrderStatus = updateCanceledOpenOrders(ib, orderId, trademkt)   # update each order that we cancelled
    print("action ",openOrdersList[x].action)
    if openOrdersList[x].action == "BUY" and openOrdersList[x].orderType == "STP":
        openOrdersList[x].auxPrice = 2750.75
        print("new auxPrice",openOrdersList[x].auxPrice)
        openOrder = openOrdersList[x]
        print("type openOrder ",type(openOrder))
        print("")
        #print("type contract ",type(contract))
        print("")
        print("open Order ",openOrder)
        ib.placeOrder(tradeContract,openOrder)
        #openOrdersList

    x += 1
    print(" x is ",x)