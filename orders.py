""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants
import logger

log = logger.getLogger()

# build orders has to handle outstanding STP orders, open positions and execute new position
#there are a few order work flows.
# buy or sell based on trigger with no open stp orders or open position
# buy or sell based on trigger with open stp and open position (every open order should have a stp order)
# no buy or sell but we crossed and need to close stp's and close positions
#
def closeOutSTPandPosition(ib):   # this manages the closing of stp orders and open position
    closeSTP = findOpenOrders(ib.True)      # close open STP orders
    closeOutPositions = findOpenPositions(ib,True)  # we are going to execute (True)
    return

def buildOrders(ib, tradeContract, action, quantity, cciProfile,stoplossprice,):
    #STP order
    closeOpen = findOpenOrders(ib, True)
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
    #closeOpen = findOpenOrders(ib,True)
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
        print("openOrders are ---->  ",openOrders)
        print("execute --------------------------",execute)
        # if we are to execute, we need to create closing orders for each order we scroll through
        # not sure we need to differentiate between buy or sell stop orders below
        while x < len(openOrders):
            log.info("order type: {type} with ID: {id}".format(type=openOrders[x].orderType,id=openOrders[x].permId))
            openOrderId = openOrders[x].permId
            print("order id variable",openOrderId)
            print("order id variable as string", str(openOrderId))
            print("what does permid look like with type ",type(openOrders[x].permId))
            if openOrders[x].orderType == "STP" and openOrders[x].action == "SELL":
                log.info("Cancelling Sell STP order")
                stpSell += openOrders[x].totalQuantity
                if execute:
                    print("execute")
                    ib.cancelOrder(openOrders[x].permId)
            elif openOrders[x].orderType == "STP" and openOrders[x].action == "BUY":
                log.info("Cancelling Buy STP order")
                stpBuy += openOrders[x].totalQuantity
                if execute:
                    print("execute")
                    ib.cancelOrder(openOrders[x].permId)
            x += 1
        return stpSell, stpBuy
def findOpenPositions(self,positions):
        position_long_tf = False
        position_short_tf = False
        x = 0
        long_position_qty, short_position_qty = 0, 0
        while x < len(positions):
            if (positions[x][1].symbol) == "ES":
                if positions[x][2] > 0:
                    long_position_qty += positions[x][2]
                    position_long_tf = True
                elif positions[x][2] < 0:
                    short_position_qty += positions[x][2]
                    position_short_tf = True
            x += + 1
        log.info("Have a position: long qty: {lqty} and short qty: {sqty} ".format(lqty = long_position_qty,sqty = short_position_qty))    
        return position_long_tf, position_short_tf, long_position_qty, short_position_qty 