""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants

def buildOrders(ib, tradeContract, action, quantity, cciProfile,stoplossprice):

    parentId = ib.client.getReqId()


    #Entry Order
    print("tradeContract ",tradeContract)
    print("action: ",action)
    print("qty : ",quantity)
    print("cciprofile ",cciProfile)
    print("stoplosspricee ",stoplossprice)
    MktOrder = Order(
        action = action,
        orderType = "MKT",
        orderId = parentId,
        faProfile = cciProfile,
        totalQuantity = quantity,
        transmit = False
    )
    #Stop Loss Order
    stoplossOrder = Order(
        action = action,
        orderType = "STP",
        auxPrice = stoplossprice,
        lmtPrice = 0,
        faProfile = cciProfile,
        totalQuantity = quantity,
        orderId = ib.client.getReqId(),
        parentId = parentId,
        transmit = True
    )

    #Stop Loss Order
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
    #order = ib.MarketOrder(action,quantity)
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    tradestp = ib.placeOrder(tradeContract,stoplossOrder)
    print("Order placed  ",action,quantity)
    print("")
    #print("trade  ",MktOrder)
    #trade = ib.placeOrder(tradeContract, MktOrder)
    #for trade in ib.trades():
    #    while not trade.isDone():
    #        ib.waitOnUpdate()
    print("did place order",trademkt)
    print("")
    print("placed stop order ",tradestp)
    
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
    #    parentId = parentId,
    #    transmit = True
    #)

    return [MktOrder]

def coverOrders(ib, tradeContract, action, quantity, cciProfile,stoplossprice):

    parentId = ib.client.getReqId()


    #Entry Order
    print("tradeContract ",tradeContract)
    print("action: ",action)
    print("qty : ",quantity)
    print("cciprofile ",cciProfile)
    MktOrder = Order(
        action = action,
        orderType = "MKT",
        orderId = parentId,
        faProfile = cciProfile,
        totalQuantity = quantity,
        transmit = True
    )
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    #Stop Loss Order
    return [MktOrder]
