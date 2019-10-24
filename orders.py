""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants
import logger

log = logger.getLogger()

# build orders has to handle outstanding STP orders, open positions and execute new position
def buildOrders(ib, tradeContract, action, quantity, cciProfile,stoplossprice):
    #STP order
    closeOpen.findOpenOrder(self.ib, True)
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
    closeOpen = findOpenOrders(self.ib,True)
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

def findOpenOrders(ib, execute):
        openOrders = ib.reqAllOpenOrders()
        x, stpSell, stpBuy = 0, 0, 0
        log.info("openOrders are ---->  ".format(openOrders))
        # if we are to execute, we need to create closing orders for each order we scroll through
        while x < len(openOrders):
            log.info("order type: {type} with ID: {id}".format(type=openOrders[x].orderType,id=openOrders[x].permId))
            if openOrders[x].orderType == "STP" and openOrders[x].action == "SELL":
                stpSell += openOrders[x].totalQuantity
                if execute:
                    ib.cancelOrder(openOrders[x].permId)
            elif openOrders[x].orderType == "STP" and openOrders[x].action == "BUY":
                stpBuy += openOrders[x].totalQuantity
                if execute:
                    ib.cancelOrder(openOrders[x].permId)
            x += 1
        return stpSell, stpBuy