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
def closeOutSTPandPosition(ib, tradeContract):   # this manages the closing of stp orders and open position
    log.info("closeOutSTPandPositions: logic ??????")
    closeSTP = findOpenOrders(ib,True)      # close open STP orders
    closeOutPositions = findOpenPositions(ib,tradeContract, True)  # we are going to execute (True)
    return

def buildOrders(ib, tradeContract, action, quantity, cciProfile,stoplossprice,):
    #STP order
    closeOpen = findOpenOrders(ib, True)
    parentId = ib.client.getReqId()
    stopAction = "BUY"
    if action == "BUY":
        stopAction = "SELL"
    #Entry Order
    print("buildOrders: tradeContract ",tradeContract)
    print("buildOrders: action: ",action)
    print("buildOrders: qty : ",quantity)
    print("buildOrders: cciprofile ",cciProfile)
    print("buildOrders: stoplosspricee ",stoplossprice)
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
        action = stopAction,
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
    print("buildOrders: Order placed  ",action,quantity)
    print("")
    
    print("buildOrders: did place order",trademkt)
    print("")
    print("buildOrders: placed stop order ",tradestp)
    return [MktOrder], [stoplossOrder], parentId

def closeOrders(ib, tradeContract, account, action, quantity):
    #closeOpen = findOpenOrders(ib,True)
    parentId = ib.client.getReqId()
    #Entry Order
    print("closeOrders: tradeContract ",tradeContract)
    print("closeOrders: action: ",action)
    print("closeOrders: qty : ",quantity)
    MktOrder = Order(
        account = account,
        action = action,
        orderType = "MKT",
        orderId = parentId,
        totalQuantity = quantity,
        transmit = True
    )
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    ib.sleep(1)
    trademkt.log
    #Stop Loss Order
    return [MktOrder]

def openOrder(ib):
    openOrders = self.ib.reqAllOpenOrders()
    return

def findOpenOrders(ib,execute):
        #allOpenOrders = ib.reqAllOpenOrders()
        log.info("************** in the findOpenOrder function *****************")
        openOrdersList = ib.openOrders()
        x, stpSell, stpBuy = 0, 0, 0
        # if we are to execute, we need to create closing orders for each order we scroll through
        # not sure we need to differentiate between buy or sell stop orders below
        while x < len(openOrdersList):
            #print("openOrders are ---->  ",openOrdersList[x].conId)
            #log.info("order type: {type} with ID: {id}".format(type=openOrdersList[x].orderType,id=openOrdersList[x].permId))
            openOrderId = openOrdersList[x].permId
            log.info("findOpenOrder: - we have open order records: opendOrderId: {ooi}".format(ooi=openOrderId))
            if openOrdersList[x].orderType == "STP" and openOrdersList[x].action == "SELL":
                log.info("findOpenOrder - we have open order records: SELL {one}".format(one=openOrdersList[x].orderType))
                stpSell += openOrdersList[x].totalQuantity
                if execute:
                    #temp = temphold(orderId=openOrder[x].permId)
                    cv = ib.client.cancelOrder(openOrdersList[x])
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=cv))
            elif openOrdersList[x].orderType == "STP" and openOrdersList[x].action == "BUY":
                log.info("findOpenOrder: - we have open order records: BUY {one}".format(one=openOrdersList[x].orderType))
                stpBuy += openOrdersList[x].totalQuantity
                if execute:
                    print("execute")
                    #temp = temphold(orderId=openOrder[x].permId)
                    cv = ib.client.cancelOrder(openOrdersList[x])
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=cv))
            x += 1
        return stpSell, stpBuy

def findOpenPositions(ib, tradeContract, execute):
        log.info("findOpenPositions: execute: {cv} ".format(cv=execute))
        #position_long_tf = False
        #position_short_tf = False
        x = 0
        #long_position_qty, short_position_qty = 0, 0
        positions = ib.positions()
        while x < len(positions):
            if (positions[x][1].symbol) == "ES":
                if positions[x][2] > 0:
                    log.info("findOpenPositions: Have a position and closing it qty by SELL: {qty} ".format(qty = positions[x][2])) 
                    closeLong = closeOrders(ib, tradeContract, positions[x].account, "SELL", positions[x][2])
                elif positions[x][2] < 0:
                    log.info("findOpenPosition: Have a position and closing it qty by BUY: {qty} ".format(qty = abs(positions[x][2]))) 
                    closeLong = closeOrders(ib, tradeContract, positions[x].account, "BUY", abs(positions[x][2]))
            x += + 1
           
        return 