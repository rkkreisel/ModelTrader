""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants

def buildOrders(ib, tradeContract, action, quantity, cciProfile):

    #parentId = ib.client.getReqId()

    #if action == "BUY":
    #    entryPrice = price + config.ENTRY_SPREAD
    #    bracketAction = "SELL"
    #    profitPrice = entryPrice + config.PROFIT_SPREAD
    #    lossPrice = entryPrice - stop
    #else:
    #    entryPrice = price - config.ENTRY_SPREAD
    #    bracketAction = "BUY"
    #    profitPrice = entryPrice - config.PROFIT_SPREAD
    #    lossPrice = entryPrice + stop

    #Entry Order
    print(tradeContract)
    MktOrder = Order(
        action = action,
        orderType = "MKT",
        faProfile = cciProfile,
        totalQuantity = quantity,
        transmit = True
    )
    #order = ib.MarketOrder(action,quantity)
    #trade = ib.placeOrder(tradeContract,MktOrder)
    print("Order placed  ",action,quantity)
    print("")
    print("trade  ",MktOrder)
    trade = ib.placeOrder(tradeContract, MktOrder)
    print("did place order",trade)
        #ib.sleep(5)
    #print(trade.log)
    #Profit Order
    #profitOrder = Order(
    #    action = bracketAction,
    #    orderType = "LMT",
    #    auxPrice = 0,
    #    lmtPrice = profitPrice,
    #    faProfile = config.ALLOCATION_PROFILE,
    #    totalQuantity = quantity,
    #    orderId = ib.client.getReqId(),
    #    parentId = parentId,
    #    transmit = False
    #)

    #Stop Loss Order
    #lossOrder = Order(
    #    action = bracketAction,
    #    orderType = "STP",
    #    auxPrice = lossPrice,
    #    lmtPrice = 0,
    #    faProfile = config.ALLOCATION_PROFILE,
    #    totalQuantity = quantity,
    #    orderId = ib.client.getReqId(),
    ##    parentId = parentId,
    #    transmit = True
    #)

    return [MktOrder]
