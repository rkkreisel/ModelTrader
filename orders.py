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
def closeOutMain(ib, tradeContract, execute):           # this manages the closing of stp orders and open position
    log.info("closeOutMains: logic ")
    qtyCancel = closeOpenOrders(ib)                   # close open STP orders
    log.info("closeOutMain: we just cancelled the following number of orders: {c}".format(c=qtyCancel))
    #log.info("Closed out open orders qty: {qty}".format(qty=qtyCancel))
    closeOutPositions = closeOpenPositions(ib, tradeContract)  # we re going to execute (True)
    return

def createOrdersMain(ib,tradeContract,tradeAction,quantity,cciProfile,stoplossprice):
    trademkt, tradestp, parentId, MktOrder, stopLossOrder = buildOrders(ib, tradeContract, tradeAction, quantity, cciProfile, stoplossprice)    # this places the order.  No confirm it was executed
    log.info("createOrdersMain: just created MKT: {l} and STP {s} order ".format(l=trademkt,s=tradestp))
    symbol, orderId, orderType, action, quantity, status, date_order = parseTradeString(ib,trademkt)
    wroteOrdersToCSV = writeOrdersToCSV(ib, MktOrder, "MktOrder", status)
    filledTF, fillStatus = checkForOpenOrderStatus(ib, trademkt, "trademkt", trademkt.orderStatus.status)
    if fillStatus:
        updateOrders = writeTradeToCSV(ib, trademkt, "tradeMkt", status)
    symbol, orderId, orderType, action, quantity, status, date_order = parseTradeString(ib,tradestp)
    wroteOrdersToCSV = writeOrdersToCSV(ib, stopLossOrder, "stopLossOrder", status)
    
    return fillStatus

# this is counting for top of the loop for information only
def countOpenOrders(ib):                 # This is to find open STP orders only
    log.info("************** in the findOpenOrder function *****************")
    openOrdersList = ib.openTrades()
    x, stpSell, stpBuy = 0, 0, 0
    # if we are to execute, we need to create closing orders for each order we scroll throug
    # not sure we need to differentiate between buy or sell stop orders below
    while x < len(openOrdersList):
        symbol, orderId, orderType, action, quantity, status, date_order = parseTradeString(ib,openOrdersList[x])
        validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
        log.info("findOpenOrder: - we have open order records: opendOrderId: {ooi} ".format(ooi=orderId))
        if orderType == "STP" and action == "Sell" and status == "PendingSubmit":
            log.info("findOpenOrder - we have open order records: Sell {one}".format(one=orderType))
            stpSell += quantity                       #        we don't care about qty - just cancel order
        elif orderType == "STP" and action == "Buy" and status == "PendingSubmit":
            log.info("findOpenOrder: - we have open order records: Buy {one}".format(one=orderType))
            stpBuy += quantity
        x += 1
    return stpSell, stpBuy

def countOpenPositions(ib):
    log.info("countOpenPositions: ")
    x = 0
    position_long_tf = False
    position_short_tf = False
    long_position_qty, short_position_qty = 0, 0
    positions = ib.positions()
    log.info("countOpenPositions: positions: {p} ".format(p=positions))
    #updatedPositions = updatePositionsCSV(ib,positions)
    while x < len(positions):
        account, symbol, quantity, avgCost = parsePositionString(ib,positions[x])
        log.info("countOpenPositions: positions account should be:{a} ".format(a=account))
        if (symbol) == "ES":
            if quantity > 0:
                long_position_qty += quantity
                position_long_tf = True
            elif positions[x][2] < 0:
                short_position_qty += quantity
                position_short_tf = True
        x += + 1
    log.info("Have a position: long qty: {lqty} and short qty: {sqty} ".format(lqty = long_position_qty,sqty = short_position_qty))    
    return position_long_tf, position_short_tf, long_position_qty, short_position_qty 

def closeOpenOrders(ib):                 # This is to find open STP orders and cancel 
    log.info("************** in the closeOpenOrder function *****************")
    openOrdersList = ib.openOrders()
    x = 0
    # not sure we need to differentiate between buy or sell stop orders below
    while x < len(openOrdersList):
        #symbol, orderId, orderType, action, quantity, status, date_order = parseTradeString(ib,openOrdersList[x])
        #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
        #log.info("closeOpenOrder: - we have open order records: opendOrderId: {ooi} orderType: {ot} ".format(ooi=orderId, ot=orderType))
        log.info("closeOpenOrder: closing all open orders - currently working on: {oo}".format(oo=openOrdersList[x]))
        trademkt = ib.cancelOrder(openOrdersList[x])            # don't need to place order when cancelling
        #print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
        log.info("----------------------- TRADEMKT ---------------: {t}".format(t=trademkt))
        #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
        symbol, orderId, orderType, action, quantity, status, date_order = parseTradeString(ib,trademkt)      
        checkOrderStatus = updateCanceledOpenOrders(ib, orderId, trademkt)   # update each order that we cancelled
        log.info("closeOpenOrder: cancel order sent -> cv: {cv} and order status completed?:{os} ".format(cv=trademkt,os=checkOrderStatus))
        x += 1
    return x

def closeOpenPositions(ib, tradeContract):             #we want to close open positions as known in IB as well as keep our CSV files up to date.
    # we need to manage the following here
    # get open positions from IB
    # close the positions order
    # create order entry in csv
    # track status and update orders and trade csv and positions.
    log.info("closeOpenPositions: ")
    x = 0
    positionLong, positionShort = 0, 0
    positions = ib.positions()
    log.info("closeOpenPositions: number of positions (not quantity): {op}".format(op=len(positions)))
    #updatedPositions = updatePositionsCSV(ib,positions)
    while x < len(positions):
        orderFoundTF = False
        account, symbol, quantity, avgCost = parsePositionString(ib,positions[x])   # need abs quty since buy/sell abs and position are plus and minus
        log.info("closeOpenPositions: - we have open Position records: symbol: {s} and len of positions: {lp}".format(s=symbol,lp=len(positions)))
        action = "Buy"
        if symbol == "ES" and abs(quantity) > 0:
            action = "Sell"
        #orderFoundTF = True
        log.info("closeOpenPositions - we have open order records: Long {one} with the action: {act}".format(one=abs(quantity),act=action))
        positionLong += quantity
        #temp = temphold(orderId=openOrder[x].permId)
        trademkt, MktOrder = closePositionsOrders(ib,tradeContract, account, action, abs(quantity))
        symbol, orderId, orderType, action, quantity, status, date_order = parseTradeString(ib,trademkt)
        print("\n----------------------- openOrdersList ---------------\n",positions[x])
        print("\n----------------------- TRADEMKT ---------------\n",trademkt)
        writeToCsv = writeOrdersToCSV(ib, MktOrder, "MktOrder",status)               # writing to orders csv
        log.info("closeOpenPositions: cancel order sent -> cv: {cv} and status: {s} ".format(cv=trademkt, s=status))
        # checking status of the order
        filledTF, openOrderStatus = checkForOpenOrderStatus(ib, trademkt, "trademkt", status)
        if filledTF:
            writeToCsv = writeTradeToCSV(ib,trademkt,"trademkt",status)
        x += 1
    return 

def writeOrdersToCSV(ib, orderInfo, orderName, status):
    # tradestp, "tradestp", tradestp.orderStatus.status
    # Go through open order
    #log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: ".format(oi=orderInfo))
    #log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: {os}".format(oi=orderInfo, os=orderInfo.order.orderId))
    orderId, orderType, action, quantity = parseOrderString(ib,orderInfo)
    time = datetime.now()
    log.info("\nwriteOrdersToCSV: orderId: {oi} and qty: {q} ".format(oi=orderId, q=quantity))
    #csv_row = str(orderInfo) 
    with open('data/orders.csv', mode='a', newline = '') as ordersCSV:
        fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        histwriter.writeheader()
        histwriter.writerow({'Order_Id': orderId, 'Order': orderInfo, 'Status': 'Cancel Submitted', 'Date_Pending': time, 'Date_Cancelled': '1/1/20', 'Date_Filled': '1/1/20'})
    return

def writeTradeToCSV(ib, orderInfo, orderName, status):
    # Go through open order  trademkt, "tradeMkt", status
    #log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: ".format(oi=orderInfo))
    #log.info("\nwriteOrdersToCSV: orderInfo: {oi} and orderId: {os}".format(oi=orderInfo, os=orderInfo.order.orderId))
    orderId = orderInfo.order.orderId
    status = orderInfo.orderStatus.status
    time = datetime.now()
    log.info("\nwriteTradesToCSV: orderInfo: {oi} and orderId: {os} and status: oos: {oos}".format(oi=orderInfo, os=orderId,oos=status))
    csv_row = str(orderInfo) 
    with open('data/trades.csv', mode='a', newline = '') as ordersCSV:
        fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        histwriter.writeheader()
        histwriter.writerow({'Order_Id': orderId, 'Order': orderInfo, 'Status': status, 'Date_Pending': time, 'Date_Cancelled': '1/1/20', 'Date_Filled': datetime.now()})
    return

def checkForOpenOrderStatus(ib, orderInfo, orderName, status):
    # going through orders looking for filled and updating trades   
    startTime = datetime.now()
    while True:
        symbol, orderId, orderType, action, quantity, fillStatus, date_order = parseTradeString(ib,orderInfo)
        log.info("Checking for status change.  status:{s})".format(s=fillStatus))
        if fillStatus not in ['PendingSubmit','PreSubmitted']:
            log.info("checkForOpenOrderStatus: Open Executed worked.  Fill Status is:{fs}".format(fs=fillStatus))
            filledTF = True
            break
        elif (datetime.now() - startTime).total_seconds() > 100:
            log.debug("order failed for: {0} ".format(orderInfo.order.orderId))
            filledTF = False
            break
        log.info("\ncheckForOpenOrderStatus: going to sleep {s}\n".format(s=(datetime.now() - startTime).total_seconds()))
        ib.sleep(1.0)
    return filledTF, fillStatus

def updateCanceledOpenOrders(ib, orderId, trademkt):     # I don't think this creates a new order but just cancels and existing order.  No new csv records created but updated.
    startTime = datetime.now()
    cancelledTF = False
    log.info("updateCanceledOpenOrders: trademkt: {tm}".format(tm=trademkt))
    while True:
        log.info("updateCanceledOpenOrders: in loop trademkt: {tm} seconds start {sd} end {ed}".format(tm=trademkt.orderStatus.status,sd=datetime.now(),ed=startTime))
        status = trademkt.orderStatus.status
        if status not in ['PendingSubmit','PreSubmitted','PendingCancel']:
            log.info("Cancelling Open Orders worked")
            updateOrders = updateOrderWithCancelledSTP(ib, orderId, "tradeMkt", status)
            cancelledTF = True
            break
        if (datetime.now() - startTime).total_seconds() > 100:
            log.debug("Cancelling order failed for: {0} ".format(trademkt.order.orderId))
        ib.sleep(1.0)
    return cancelledTF

#def updatePositionsCSV(ib,positionsInfo):
#    csv_row = positionsInfo
#    with open('data/positions.csv', mode='a', newline = '') as positionsCSV:
#        fieldnames = ['Trade']
#        histwriter = csv.DictWriter(positionsCSV, fieldnames = fieldnames)
#        histwriter.writeheader()
#        histwriter.writerow({'Trade': positionsInfo})
#    return

def updateOrderWithCancelledSTP(ib, openOrderId, orderName, newstatus):
    # we have an open order from IB.  Going to run through our CSV file and make sure it exists.
    # if it doesn't exist, we will add it
    # this is for a single order
    # log.info("updateOrderWithCancelledSTP: we are looking for openOrderId")
    # REFERENCE fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled','Date_Updated]
    foundOrderInCSV = False
    x3 = 0
    df = pd.read_csv("data/orders.csv")   # https://stackoverflow.com/questions/11033590/change-specific-value-in-csv-file-via-python
    with open('data/orders.csv', newline ='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Order_Id'] == openOrderId:
                foundOrderInCSV = True
                log.info("updateOrderWithCancelledSTP: we found the order we are cancelling in the CSV file")
                df.set_value(x3,"status",newstatus)                
        x3 += 1
    csvfile.close()
    df.to_csv("data/orders.csv", index=False)
    if not foundOrderInCSV:
        log.info("updateOrderWithCancelledSTP: we DID NOT FIND the order we are cancelling in the CSV file")
    return foundOrderInCSV

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
                    df = pd.read_csv("data/orders.csv")   # https://stackoverflow.com/questions/11033590/change-specific-value-in-csv-file-via-python
                    df.head(5)
                    df.loc[df['Order_Id']==openOrderId, 'Status'] = status
                    df.loc[df['Order_Id']==openOrderId, 'Date_Updated'] = datetime.now()
                    df.to_csv("data/orders.csv", index=False)
    return

def parseOrderString(ib,tradeInfo):
    log.debug("parseOrderString: tradeInfo: {to} ".format(to=tradeInfo))
    orderId = tradeInfo.orderId
    orderType = tradeInfo.orderType
    action = tradeInfo.action
    quantity = tradeInfo.totalQuantity
    return orderId, orderType, action, quantity
    
def parseTradeString(ib,tradeInfo):
    log.debug("parseTradeString: tradeInfo: {to} ".format(to=tradeInfo))
    symbol = tradeInfo.contract.symbol
    orderId = tradeInfo.order.orderId
    orderType = tradeInfo.order.orderType
    action = tradeInfo.order.action
    quantity = tradeInfo.order.totalQuantity
    status = tradeInfo.orderStatus.status
    date_order = tradeInfo.log[0].time      # there are nested logs
    return symbol, orderId, orderType, action, quantity, status, date_order
    
def parsePositionString(ib, positionInfo):
    #print("parsePositionString.  Here are the positions {p}".format(p=positionInfo))
    account = positionInfo.account
    symbol = positionInfo.contract.symbol
    quantity = positionInfo.position
    avgCost = positionInfo.avgCost
    return account, symbol, quantity, avgCost

def buildOrders(ib, tradeContract, action, quantity, cciProfile,stoplossprice,):
    #STP order
    #closeOpen = findOpenOrders(ib, True)
    parentId = ib.client.getReqId()
    stopAction = "Buy" 
    if action == "Buy":
        stopAction = "Sell"
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
    #Stop Loss Order
    stopLossOrder = Order(
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
    tradestp = ib.placeOrder(tradeContract,stopLossOrder)
    #print("buildOrders: Order placed  ",action,quantity)
    #print("")
    
    #print("buildOrders: did place order",trademkt)
    #print("")
    #print("buildOrders: placed stop order ",tradestp)

    return trademkt, tradestp, parentId, MktOrder, stopLossOrder

def closePositionsOrders(ib, tradeContract, account, action, quantity):
    #closeOpen = findOpenOrders(ib,True)
    parentId = ib.client.getReqId()
    #Entry Order
    log.info("closePositionsOrders: tradeContract: {tc} account: {ac} action: {act} qty: {qty}".format(tc=tradeContract, ac=account, act=action, qty= quantity))
    MktOrder = Order(
        account = account,
        action = action,
        orderType = "MKT",
        orderId = parentId,
        totalQuantity = quantity,
        transmit = True
    ) 
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    symbol, orderId, orderType, action, quantity, status, date_order = parseTradeString(ib,trademkt)
    print("closePositionsOrders: trademkt ",trademkt)
    writeToCsv = writeOrdersToCSV(ib, MktOrder, "MktOrder",status)
    return trademkt, MktOrder