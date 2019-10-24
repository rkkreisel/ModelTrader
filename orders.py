""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants
# build orders has to handle outstanding STP orders, open positions and execute new position
def buildOrders(ib, tradeContract, action, quantity, cciProfile,stoplossprice):
    #STP order
    #orders.findOpenOrder(True)
    # parentId = ib.client.getReqId()
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
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    tradestp = ib.placeOrder(tradeContract,stoplossOrder)
    print("Order placed  ",action,quantity)
    print("")
    
    print("did place order",trademkt)
    print("")
    print("placed stop order ",tradestp)
    return [MktOrder], [stoplossOrder], parentId

def coverOrders(ib, tradeContract, action, quantity, cciProfile):
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

def openOrder(ib):
    openOrders = self.ib.reqAllOpenOrders()
    return

def findOpenOrders(self, execute):
        openOrders = self.ib.reqAllOpenOrders()
        x, stpSell, stpBuy = 0, 0, 0
        print("openOrders are ----> ",openOrders)
        while x < len(openOrders):
            if openOrders[x].orderType == "STP" and openOrders[x].action == "SELL":
                stpSell += openOrders[x].totalQuantity
            elif openOrders[x].orderType == "STP" and openOrders[x].action == "BUY":
                stpBuy += openOrders[x].totalQuantity
            x += 1
        return stpSell, stpBuy