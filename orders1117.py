""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants
import logger
import csv

log = logger.getLogger()

# build orders has to handle outstanding STP orders, open positions and execute new position
#there are a few order work flows.
# buy or sell based on trigger with no open stp orders or open position
# buy or sell based on trigger with open stp and open position (every open order should have a stp order)
# no buy or sell but we crossed and need to close stp's and close positions
#
def closeOutSTPandPosition(ib, tradeContract, execute):               # this manages the closing of stp orders and open position
    log.info("closeOutSTPandPositions: logic ??????")
    closeSTP = findOpenOrders(ib,execute)                             # close open STP orders
    closeOutPositions = findOpenPositions(ib,tradeContract, execute)  # we are going to execute (True)
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
    checkOrderStatus = updateOrderandTrades(ib, trademkt, "trademkt")  #wait for status t/f - false since this is 
    tradestp = ib.placeOrder(tradeContract,stoplossOrder)
    checkOrderStatus = updateOrderandTrades(ib, tradestp, "tradestp")   #wait for status t/f
    
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
    log.info("closeOrders: tradeContract: {tc} account: {ac} action: {act} qty: {qty}".format(tc=tradeContract, ac=account, act=action, qty= quantity))
    MktOrder = Order(
        account = account,
        action = action,
        orderType = "MKT",
        orderId = parentId,
        totalQuantity = quantity,
        transmit = True
    )
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    checkOrderStatus = updateOrderandTrades(ib, trademkt, "trademkt")
    #ib.sleep(1)
    #trademkt.log
    #Stop Loss Order
    return [MktOrder]

def openOrder(ib):
    openOrders = self.ib.reqAllOpenOrders()
    return

def findOpenOrders(ib,execute):                 # This is to find open STP orders and cancel them
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
            log.info("findOpenOrder: - we have open order records: opendOrderId: {ooi} execute: {exe}".format(ooi=openOrderId, exe=execute))
            if openOrdersList[x].orderType == "STP" and openOrdersList[x].action == "SELL":
                log.info("findOpenOrder - we have open order records: SELL {one}".format(one=openOrdersList[x].orderType))
                stpSell += openOrdersList[x].totalQuantity
                if execute:
                    #temp = temphold(orderId=openOrder[x].permId)
                    trademkt= ib.client.cancelOrder(openOrdersList[x])
                    print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
                    print("\n----------------------- TRADEMKT ---------------\n",trademkt)
                    checkOrderStatus = updateOrderandTrades(ib, trademkt, "trademkt")
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=trademkt))
            elif openOrdersList[x].orderType == "STP" and openOrdersList[x].action == "BUY":
                log.info("findOpenOrder: - we have open order records: BUY {one}".format(one=openOrdersList[x].orderType))
                stpBuy += openOrdersList[x].totalQuantity
                if execute:
                    print("execute")
                    #temp = temphold(orderId=openOrder[x].permId)
                    trademkt = ib.client.cancelOrder(openOrdersList[x])
                    print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
                    print("\n----------------------- TRADEMKT ---------------\n",trademkt)
                    checkOrderStatus = updateOrderandTrades(ib, trademkt, "trademkt")
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=trademkt))
            x += 1
        return stpSell, stpBuy

def findOpenPositions(ib, tradeContract, execute):
        log.info("findOpenPositions: execute: {cv} ".format(cv=execute))
        #position_long_tf = False
        #position_short_tf = False
        x = 0
        #long_position_qty, short_position_qty = 0, 0
        positions = ib.positions()
        updatedPositions = updatePositionsCSV(ib,positions)
        while x < len(positions):
            #print("openOrders are ---->  ",openOrdersList[x].conId)
            #log.info("order type: {type} with ID: {id}".format(type=openOrdersList[x].orderType,id=openOrdersList[x].permId))
            opxsenOrderId = openOrdersList[x].permId
            log.info("findOpenOrder: - we have open order records: opendOrderId: {ooi} execute: {exe}".format(ooi=openOrderId, exe=execute))
            if openOrdersList[x].orderType == "STP" and openOrdersList[x].action == "SELL":
                log.info("findOpenOrder - we have open order records: SELL {one}".format(one=openOrdersList[x].orderType))
                stpSell += openOrdersList[x].totalQuantity
                if execute:
                    #temp = temphold(orderId=openOrder[x].permId)
                    trademkt= ib.client.cancelOrder(openOrdersList[x])
                    print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
                    print("\n----------------------- TRADEMKT ---------------\n",trademkt)
                    checkOrderStatus = updateOrderandTrades(ib, trademkt, "trademkt")
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=trademkt))
            elif openOrdersList[x].orderType == "STP" and openOrdersList[x].action == "BUY":
                log.info("findOpenOrder: - we have open order records: BUY {one}".format(one=openOrdersList[x].orderType))
                stpBuy += openOrdersList[x].totalQuantity
                if execute:
                    print("execute")
                    #temp = temphold(orderId=openOrder[x].permId)
                    trademkt = ib.client.cancelOrder(openOrdersList[x])
                    print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
                    print("\n----------------------- TRADEMKT ---------------\n",trademkt)
                    checkOrderStatus = updateOrderandTrades(ib, trademkt, "trademkt")
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=trademkt))
            x += 1
        
        
        
        
        
        
        
        while x < len(positions):
            if (positions[x][1].symbol) == "ES":
                if positions[x][2] > 0:
                    log.info("findOpenPositions: Have a position and closing it qty by SELL: {qty} ".format(qty = positions[x][2])) 
                    closeLong = closeOrders(ib, tradeContract, positions[x].account, "SELL", positions[x][2])
                    checkOrderStatus = updateOrderandTrades(ib, closeLong,"closeLong")
                elif positions[x][2] < 0:
                    log.info("findOpenPosition: Have a position and closing it qty by BUY: {qty} ".format(qty = abs(positions[x][2]))) 
                    closeLong = closeOrders(ib, tradeContract, positions[x].account, "BUY", abs(positions[x][2]))
                    checkOrderStatus = updateOrderandTrades(ib, closeLong, "closeLong")
            x += + 1
           
        return 
def updateOrderandTrades(ib,orderInfo,orderName):
    #log.info("\nupdateOrderandTrades: orderInfo: {oi} and orderId: ".format(oi=orderInfo))
    #log.info("\nupdateOrderandTrades: orderInfo: {oi} and orderId: {os}".format(oi=orderInfo, os=orderInfo.order.orderId))
    log.info("\nupdateOrderandTrades: orderInfo: {oi} and orderId: {os} and status: oos: {oos}".format(oi=orderInfo, os=orderInfo.order.orderId,oos=orderInfo.orderStatus.status))
    csv_row = str(orderInfo) 
    with open('data/orders.csv', mode='a') as ordersCSV:
            histwriter = csv.writer(ordersCSV, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            histwriter.writerow([csv_row])

    while not (orderName + ".isDone()"):
        log.info("waiting for the order status to change, orderName: ".format(orderName))
        #ib.waitOnUpdate()

    x1 = 0
    updatedOrders = ib.trades()
    print("\n---------------------------------updated Orders now Trades ----------------------------------",updatedOrders)
    csv_file_x1 = csv.reader(open('data/orders.csv', "rt"), delimiter = ",")
    while x1 < len(updatedOrders):
        log.debug("x1 {xs} and len(uupdatedorders): {l}".format(xs = x1, l=len(updatedOrders)))
        for rowx1 in csv_file_x1:
            log.info("updateOrderandTrades: going through order changes and csv, rowx1[0]: {rx} updatedOrders[x1]: {uo}".format(rx=rowx1[0],uo=updatedOrders[x1]))
            if rowx1[0] == updatedOrders[x1]:                             #13 is winrisk - whether we trade or not
                log.info("we have a match in between orders and csv file")
                #rowx1[0] = ""   #updatedOrders.orderStatus.status
                log.info("we have a match but what is the order status oooooooooooooo",format(updatedOrders.orderStatus.status))
                if updatedOrders.orderStatus.status == "Submitted":
                    with open('data/trades.csv', mode='a') as tradesCSV:
                        csv_row = orderInfo.order.orderId + ',' + orderInfo.orderStatus.status + ',' + rowx1[0] 
                        histwriter = csv.writer(tradesCSV, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        histwriter.writerow([csv_row])
        x1 += 1
        log.info("updateOrdersandTrades: x1 before +:{x}".format(x=x1))
    
    return

def updatePositionsCSV(ib,positionsInfo):
    csv_row = positionsInfo
    with open('data/positions.csv', mode='a') as positionsCSV:
        histwriter = csv.writer(positionsCSV, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        histwriter.writerow([csv_row])
    
    return