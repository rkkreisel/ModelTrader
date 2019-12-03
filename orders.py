""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants
import logger
import csv
import pandas as pd
from datetime import datetime, timedelta

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
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    checkOrderStatus = writeOrdersToCSV(ib, trademkt, "trademkt", trademkt.orderStatus.status)
    checkOrderStatus = checkForOpenOrderStatus(ib, trademkt, "trademkt", trademkt.orderStatus.status)
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
    tradestp = ib.placeOrder(tradeContract,stoplossOrder)
    checkOrderStatus = writeOrdersToCSV(ib, trademkt, "trademkt", trademkt.orderStatus.status)   
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
    print("closeOrders: trademkt ",trademkt)
    checkOrderStatus = writeOrdersToCSV(ib, trademkt, "trademkt")
    #ib.sleep(1)
    #trademkt.log
    #Stop Loss Order
    return [MktOrder]

def openOrder(ib):
    openOrders = self.ib.reqAllOpenOrders()

def findOpenOrders(ib,execute):                 # This is to find open STP orders and cancel them when execute is True
        #allOpenOrders = ib.reqAllOpenOrders()
        log.info("************** in the findOpenOrder function *****************")
        openOrdersList = ib.openTrades()
        x, stpSell, stpBuy = 0, 0, 0
        # if we are to execute, we need to create closing orders for each order we scroll throug
        # not sure we need to differentiate between buy or sell stop orders below
        while x < len(openOrdersList):
            #print("openOrders are ---->  ",openOrdersList[x].conId)
            #log.info("order type: {type} with ID: {id}".format(type=openOrdersList[x].orderType,id=openOrdersList[x].permId))
            symbol, orderId, orderType, action, quantity, status, date_order = parseTradeString(openOrdersList[x])
            #openOrderId = openOrdersList[x].orderId
            validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
            log.info("findOpenOrder: - we have open order records: opendOrderId: {ooi} execute: {exe}".format(ooi=orderId, exe=execute))
            if orderType == "STP" and action == "SELL" and status == "PendingSubmit":
                log.info("findOpenOrder - we have open order records: SELL {one}".format(one=orderType))
                stpSell += quantity                       #        we don't care about qty - just cancel order
                if execute:
                    #temp = temphold(orderId=openOrder[x].permId)
                    trademkt= ib.client.cancelOrder(openOrdersList[x].order)
                    print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x].order)
                    print("\n----------------------- TRADEMKT ---------------\n",trademkt)
                    checkOrderStatus = updateCanceledOpenOrders(ib, orderId, trademkt)
                    validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=trademkt))
            elif orderType == "STP" and action == "BUY" and status == "PendingSubmit":
                openOrderFoundTF = True
                log.info("findOpenOrder: - we have open order records: BUY {one}".format(one=orderType))
                stpBuy += quantity
                if execute:
                    print("execute")
                    #temp = temphold(orderId=openOrder[x].permId)
                    trademkt = ib.client.cancelOrder(openOrdersList[x].order)
                    print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x].order)
                    print("\n----------------------- TRADEMKT ---------------\n",trademkt)
                    checkOrderStatus = updateCanceledOpenOrders(ib, orderId, trademkt)
                    validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=trademkt))
            x += 1
        return stpSell, stpBuy

def findOpenPositions(ib, tradeContract, execute):
        log.info("findOpenPositions: execute: {cv} ".format(cv=execute))
        #position_long_tf = False
        #position_short_tf = False
        x = 0
        positionLong, positionShort = 0, 0
        positions = ib.positions()
        print("findOpenPositions: ",positions)
        updatedPositions = updatePositionsCSV(ib,positions)
        while x < len(positions):
            orderFoundTF = False
            #print("openPositions are ---->  ",positions[x])
            #log.info("order type: {type} with ID: {id}".format(type=openOrdersList[x].orderType,id=openOrdersList[x].permId))
            #openOrderId = openOrdersList[x].permId
            log.info("findOpenOrder: - we have open order records: symbol: {s} execute: {exe}".format(s=positions[x].contract.symbol, exe=execute))
            if positions[x].contract.symbol == "ES" and positions[x].position > 0:
                #orderFoundTF = True
                log.info("findOpenPositions - we have open order records: Long {one}".format(one=positions[x].position))
                positionLong += positions[x].position
                if execute:
                    #temp = temphold(orderId=openOrder[x].permId)
                    trademkt= closeOrders(ib,tradeContract, positions[x].account, "SELL", positions[x].position)
                    print("\n----------------------- openOrdersList ---------------\n",position[x])
                    print("\n----------------------- TRADEMKT ---------------\n",trademkt)
                    checkOrderStatus = writeOrdersToCSV(ib, tradeContract, positions[x].account, "SELL", positions[x].position)
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=trademkt))
            elif positions[x].contract.symbol == "ES" and positions[x].position < 0:
                #orderFoundTF = True
                log.info("findOpenPositions - we have open order records: Long {one}".format(one=positions[x].position))
                positionLong += positions[x].position
                if execute:
                    #temp = temphold(orderId=openOrder[x].permId)
                    trademkt= closeOrders(ib,tradeContract, positions[x].account, "BUY", positions[x].position)
                    print("\n----------------------- openOrdersList ---------------\n",position[x])
                    print("\n----------------------- TRADEMKT ---------------\n",trademkt)
                    checkOrderStatus = writeOrdersToCSV(ib, tradeContract, positions[x].account, "BUY", positions[x].position)
                    log.info("findOpenOrder: cancel order sent -> cv: {cv} ".format(cv=trademkt))
            #if not orderFoundTF:      # need to add open order to file. 
            x += 1
        return 

def writeOrdersToCSV(ib, orderInfo, orderName):
    # Go through open order
    #log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: ".format(oi=orderInfo))
    #log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: {os}".format(oi=orderInfo, os=orderInfo.order.orderId))
    orderId = orderInfo.order.orderId
    status = orderInfo.orderStatus.status
    log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: {os} and status: oos: {oos}".format(oi=orderInfo, os=orderId,oos=status))
    csv_row = str(orderInfo) 
    with open('data/orders.csv', mode='a', newline = '') as ordersCSV:
        fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        histwriter.writeheader()
        histwriter.writerow({'Order_Id': orderId, 'Order': orderInfo, 'Status': status, 'Date_Pending': datetime.datetimenow(), 'Date_Cancelled': '1/1/20', 'Date_Filled': '1/1/20'})

    #while not (orderName + ".isDone()"):
    #    log.info("waiting for the order status to change, orderName: ".format(orderName))
        #ib.waitOnUpdate()
    return
def writeTradeToCSV(ib, orderInfo, orderName, status):
    # Go through open order
    #log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: ".format(oi=orderInfo))
    #log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: {os}".format(oi=orderInfo, os=orderInfo.order.orderId))
    orderId = orderInfo.order.orderId
    status = orderInfo.orderStatus.status
    log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: {os} and status: oos: {oos}".format(oi=orderInfo, os=orderId,oos=status))
    csv_row = str(orderInfo) 
    with open('data/trades.csv', mode='a', newline = '') as ordersCSV:
        fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        histwriter.writeheader()
        histwriter.writerow({'Order_Id': orderId, 'Order': orderInfo, 'Status': status, 'Date_Pending': datetime.datetimenow(), 'Date_Cancelled': '1/1/20', 'Date_Filled': '1/1/20'})

    #while not (orderName + ".isDone()"):
    #    log.info("waiting for the order status to change, orderName: ".format(orderName))
        #ib.waitOnUpdate()
    return

def checkForOpenOrderStatus(ib, orderInfo, orderName, status):
    # going through orders looking for filled and updating trades
    startTime = datetime.datetime.now()
    while True:
        status = orderInfo.orderStatus.status
        if status not in ['PendingSubmit','PreSubmitted']:
            log.info("Open Executed worked")
            updateOrders = writeTradeToCSV(ib, orderId, "tradeMkt", status)
            break
        if (datetime.datetimenow() - startTime).total_seconds() > 100:
            log.debug("order failed for: {0} ".format(orderInfo.order.orderId))
        self.ib.sleep(0.2)
        
    x1 = 0
    updatedOrders = ib.trades()
    print("\n---------------------------------updated Orders now Trades ----------------------------------",updatedOrders)
    csv_file_x1 = csv.reader(open('data/orders.csv', "rt"), delimiter = ",")
    while x1 < len(updatedOrders):
        log.debug("x1 {xs} and len(updatedorders): {l}".format(xs = x1, l=len(updatedOrders)))
        for rowx1 in csv_file_x1:
            log.info("writeOrdersToCSV: going through order changes and csv, rowx1[0]: {rx} updatedOrders[x1]: {uo}".format(rx=rowx1[0],uo=updatedOrders[x1]))
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

def updateCanceledOpenOrders(ib, orderId, trademkt):
    startTime = datetime.datetime.now()
    while True:
        status = trademkt.orderStatus.status
        if status not in ['PendingSubmit','PreSubmitted']:
            log.info("Cancelling Open Orders worked")
            updateOrders = writeOrdersToCSV(ib, orderId, "tradeMkt", status)
            break
        if (datetime.datetimenow() - startTime).total_seconds() > 100:
            log.debug("Cancelling order failed for: {0} ".format(trademkt.order.orderId))
        self.ib.sleep(0.2)
    return

def updatePositionsCSV(ib,positionsInfo):
    csv_row = positionsInfo
    with open('data/positions.csv', mode='a', newline = '') as positionsCSV:
        fieldnames = ['Trade']
        histwriter = csv.DictWriter(positionsCSV, fieldnames = fieldnames)
        histwriter.writeheader()
        histwriter.writerow({'Trade': positionsInfo})
    return

def validateOpenOrdersCSV(ib, openOrderId, status):
    # we have an open order from IB.  Going to run through our CSV file and make sure it exists.
    # if it doesn't exist, we will add it
    log.info("we are looking for openOrderId")
    # REFERENCE fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled','Date_Updated]
    foundOrderInCSV = False
    with open('data/orders.csv', newline ='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Order_Id'] == openOrderId:
                if row['Status'] == status:           # means we have it in the CSV and status matches.  Nothing to do
                    log.info("validateOpenOrdersCSV:found in CSV and status matches")
                    break
                else:                                 # order is in CSV but the status does not match.  Need to update CSV
                    csvfile.close()
                    df = pd.read_csv("data\orders.csv")   # https://stackoverflow.com/questions/11033590/change-specific-value-in-csv-file-via-python
                    df.head(5)
                    df.loc[df['Order_Id']==openOrderId, 'Status'] = status
                    df.loc[df['Order_Id']==openOrderId, 'Date_Updated'] = datetime.datetime.now()
                    df.to_csv("data\orders.csv", index=False)
    return
    
def parseTradeString(tradeInfo):
    print(tradeInfo)
    symbol = tradeInfo.contract.symbol
    orderId = tradeInfo.order.orderId
    orderType = tradeInfo.order.orderType
    action = tradeInfo.order.action
    quantity = tradeInfo.order.totalQuantity
    status = tradeInfo.orderStatus.status
    date_order = tradeInfo.log[0].time      # there are nested logs
    return symbol, orderId, orderType, action, quantity, status, date_order