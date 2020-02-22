""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants
import logger
import csv
import os
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
    log.debug("Closed out open orders qty: {qty}".format(qty=qtyCancel))
    closeOutPositions = closeOpenPositions(ib, tradeContract)  # we re going to execute (True)
    return

def createOrdersMain(ib,tradeContract,tradeAction,quantity,cciProfile,buyStopLossPrice,sellStopLossPrice,openOrderType):
    trademkt, tradestp, parentId, MktOrder, stopLossOrder = buildOrders(ib, tradeContract, tradeAction, quantity, cciProfile, buyStopLossPrice, sellStopLossPrice)    # this places the order.  No confirm it was executed
    log.info("createOrdersMain: just created MKT: {l} and STP {s} order.  Order open/close true/false: {oot} ".format(l=trademkt,s=tradestp,oot=openOrderType))
    #symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,trademkt)
    #wroteOrdersToCSV = writeOrdersToCSV(ib, MktOrder, "MktOrder", status, openOrderType)
    #filledTF, fillStatus = checkForOpenOrderStatus(ib, trademkt, "trademkt", trademkt.orderStatus.status)    # moving to event driven trade updates
    #if fillStatus:
    #    updateOrders = writeTradeToCSV(ib, trademkt, "tradeMkt", status, openOrderType = True)
    symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,tradestp)
    wroteOrdersToCSV = writeOrdersToCSV(ib, stopLossOrder, "stopLossOrder", status, openOrderType)
    
    return status

# this is counting for top of the loop for information only
def countOpenOrders(ib):                 # This is to find open STP orders only
    log.info("countOpenOrders ************** in the findOpenOrder function *****************")
    openOrdersList = ib.openTrades()
    x, stpSell, stpBuy = 0, 0, 0
    # if we are to execute, we need to create closing orders for each order we scroll throug
    # not sure we need to differentiate between buy or sell stop orders below
    log.debug("countOpenOrders openOrdersList: {ool}".format(ool=openOrdersList))
    while x < len(openOrdersList):
        symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,openOrdersList[x])
        log.debug("countOpenOrders:: symbol: {s} orderId: {oi} orderType: {ot} action: {a} quantity: {q} status: {status} date_order: {do}".format(s=symbol,oi=orderId,ot=orderType,a=action,q=quantity,status=status,do=date_order))
        validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
        log.info("findOpenOrder: - we have open order records: opendOrderId: {ooi} ".format(ooi=orderId))
        if orderType == "STP" and action == "SELL" and (status == "PendingSubmit" or status == "PreSubmitted"):
            log.info("findOpenOrder - we have open order records: Sell {one}".format(one=orderType))
            stpSell += quantity                       #        we don't care about qty - just cancel order
        elif orderType == "STP" and action == "BUY" and (status == "PendingSubmit" or status == "PreSubmitted"):
            log.info("findOpenOrder: - we have open order records: Buy {one}".format(one=orderType))
            stpBuy += quantity
        x += 1
    log.debug("stpbuy: {sb} stpsell: {ss}".format(sb=stpBuy,ss=stpSell))
    return stpSell, stpBuy

def countOpenPositions(ib,accountName):
    log.info("countOpenPositions: ")
    x = 0
    position_long_tf = False
    position_short_tf = False
    long_position_qty, short_position_qty, account_qty = 0, 0, 0
    positions = ib.positions()
    log.info("countOpenPositions: positions: {p} ".format(p=positions))
    #updatedPositions = updatePositionsCSV(ib,positions)
    while x < len(positions):
        account, symbol, quantity, avgCost = parsePositionString(ib,positions[x])
        log.info("countOpenPositions: positions account should be:{a} ".format(a=account))
        if (symbol) == "ES":
            if account == accountName:
                account_qty = account_qty + quantity
            if quantity > 0:
                long_position_qty += quantity
                position_long_tf = True
            elif positions[x][2] < 0:
                short_position_qty += quantity
                position_short_tf = True
        x += + 1
    log.info("Have a position: long qty: {lqty} and short qty: {sqty} ".format(lqty = long_position_qty,sqty = short_position_qty))    
    return position_long_tf, position_short_tf, long_position_qty, short_position_qty, account_qty

def closeOpenOrders(ib):                 # This is to find open STP orders and cancel 
    log.info("************** in the closeOpenOrder function *****************")
    openOrdersList = ib.openOrders()
    x = 0
    # not sure we need to differentiate between buy or sell stop orders below
    while x < len(openOrdersList):
        #symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,openOrdersList[x])
        #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
        #log.info("closeOpenOrder: - we have open order records: opendOrderId: {ooi} orderType: {ot} ".format(ooi=orderId, ot=orderType))
        log.info("closeOpenOrder: closing all open orders - currently working on: {oo}".format(oo=openOrdersList[x]))
        trademkt = ib.cancelOrder(openOrdersList[x])            # don't need to place order when cancelling
        #print("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
        log.info("----------------------- TRADEMKT ---------------: {t}".format(t=trademkt))
        #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
        symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,trademkt)      
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
        orderQty = abs(quantity)
        if symbol == "ES" and quantity > 0:
            action = "Sell"
            orderQty = -quantity
        #orderFoundTF = True
        log.info("closeOpenPositions - we have open order records: Long {one} with the action: {act}".format(one=abs(quantity),act=action))
        positionLong += quantity
        #temp = temphold(orderId=openOrder[x].permId)
        trademkt, MktOrder = closePositionsOrders(ib,tradeContract, account, action, abs(quantity))
        symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,trademkt)
        #print("\n----------------------- openOrdersList ---------------\n",positions[x])
        #print("\n----------------------- TRADEMKT ---------------\n",trademkt)
        writeToCsv = writeOrdersToCSV(ib, MktOrder, "MktOrder",status, openOrderType = False)               # writing to orders csv
        log.info("closeOpenPositions: cancel order sent -> cv: {cv} and status: {s} ".format(cv=trademkt, s=status))
        # checking status of the order
        #filledTF, openOrderStatus = checkForOpenOrderStatus(ib, trademkt, "trademkt", status)  # doing with event driven trade info
        #if filledTF:
        #    writeToCsv = writeTradeToCSV(ib,trademkt,"trademkt",status, openOrderType = False)
        x += 1
    return 

def writeOrdersToCSV(ib, orderInfo, orderName, status, openOrderType):
    orderId, orderType, action, quantity = parseOrderString(ib,orderInfo)
    time = datetime.now()
    log.info("\nwriteOrdersToCSV: orderId: {oi} and qty: {q} ".format(oi=orderId, q=quantity))
    #csv_row = str(orderInfo) 
    with open('data/orders.csv', mode='a', newline = '') as ordersCSV:
        fieldnames = ['Order_Id','Status','To_Open','Date_Pending','Date_Cancelled','Date_Filled','Order']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        if os.stat("data/orders.csv").st_size < 50: #don't want to keep repeating the header
            histwriter.writeheader()
        histwriter.writerow({'Order_Id': orderId, 'Status': 'Cancel Submitted', 'To_Open': openOrderType, 'Date_Pending': time, 'Date_Cancelled': '1/1/20', 'Date_Filled': '1/1/20', 'Order': orderInfo})
    return

def writeTradeToCSV(ib, orderInfo, orderName, status, openOrderType):
    orderId = orderInfo.order.orderId
    status = orderInfo.orderStatus.status
    time = datetime.now()
    log.info("writeTradesToCSV: orderInfo: and orderId: {os} and status: oos: {oos}".format(os=orderId,oos=status))
    csv_row = str(orderInfo) 
    with open('data/trades.csv', mode='a', newline = '') as ordersCSV:
        fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled','To_Open']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        if os.stat("data/trades.csv").st_size < 50: #don't want to keep repeating the header
            histwriter.writeheader()
        histwriter.writerow({'Order_Id': orderId, 'Order': orderInfo, 'Status': status, 'Date_Pending': time, 'Date_Cancelled': '1/1/20', 'Date_Filled': datetime.now(),'To_Open':openOrderType})
    return

def checkForOpenOrderStatus(ib, orderInfo, orderName, status):
    # going through orders looking for filled and updating trades   
    startTime = datetime.now()
    while True:
        symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,orderInfo)
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

def createTradesCSVFromEvent(ib, Trade, eventType):    # called from main.py as events come in RE trades
    log.info("updateTradesCSVFromEvent: updating CSV file with event type {et} expecting only one record ".format(et=eventType))
    symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,Trade)
    position_long_tf, position_short_tf, long_position_qty, short_position_qty, account_qty = countOpenPositions(ib,account)
    csv_row = str(Trade) 
    tmpPreSubmitted, tmpPendingSubmit, tmpFilled, tmpCancelled, tmpParentId, tmpPendingCancel, tmpSubmitted, tmpAvgFillPrice = "","", "", "", "", "", "", 0
    if status == "PreSubmitted": tmpPreSubmitted = datetime.now()
    if status == "PendingSubmit": tmpPendingSubmit = datetime.now()
    if status == "Submitted": tmpSubmitted = datetime.now()
    if status == "Filled": tmpFilled = datetime.now()
    if status == "PendingCancel": tmpPendingCancel = datetime.now()
    if status == "Cancelled": tmpCancelled = datetime.now()
    if status == "Filled": tmpAvgFillPrice = avgFillPrice
    if orderType == "STP": tmpParentId = parentId
    with open('data/trades.csv', mode='a', newline = '') as ordersCSV:
        fieldnames = ['Order_Id','Account','Type', 'Action','Status','EndingQty','PendingSubmit','PreSubmitted','Submitted','PendingCancel','Cancelled','Filled','ToOpen','ParentId','FAProfile','AvgFillPrice','TotalQty','Trade']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        if os.stat("data/trades.csv").st_size < 50: #don't want to keep repeating the header
            histwriter.writeheader()
        histwriter.writerow({'Order_Id':orderId,'Account':account,'Type':orderType, 'Action':action,'Status':status,'EndingQty':account_qty,'PendingSubmit':tmpPendingSubmit, 'PreSubmitted':tmpPreSubmitted, 'Submitted':tmpSubmitted,'PendingCancel':tmpPendingCancel,'Cancelled':tmpCancelled, 'Filled':tmpFilled,'ToOpen':'True', 'ParentId': tmpParentId, 'FAProfile': faProfile,'AvgFillPrice': tmpAvgFillPrice, 'TotalQty':quantity, 'Trade': Trade})
    return 

def updateTradesCSVFromEvent(ib, Trade, eventType):    # called from main.py as events come in RE trades
    # we have an open order from IB.  Going to run through our CSV file and make sure it exists.
    # if it doesn't exist, we will add it
    #log.info("we are looking for openOrderId")
    # REFERENCE fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled','Date_Updated]
    symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,Trade)
    foundOrderInCSV = False
    with open('data/trades.csv', newline ='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Order_Id'] == orderId:
                csvfile.close()
                df = pd.read_csv("data/trades.csv")   # https://stackoverflow.com/questions/11033590/change-specific-value-in-csv-file-via-python
                #df.head(5)   #prints first 5 rows
                if status == "Filled": df.loc[df['Order_Id'] == orderId, 'AvgFillPrice'] = avgFillPrice
                if status == 'PreSubmitted': df.loc[df['Order_Id'] == orderId, 'Presubmitted'] = datetime.now()
                if status == 'PendingSubmit': df.loc[df['Order_Id'] == orderId, 'PendingSubmit'] = datetime.now()        
                if status == 'Cancelled': df.loc[df['Order_Id'] == orderId, 'Cancelled'] = datetime.now()        
                if status == 'Submitted': df.loc[df['Order_Id'] == orderId, 'Submitted'] = datetime.now()        
                if status == 'Filled': df.loc[df['Order_Id'] == orderId, 'Filled'] = datetime.now()        
                df.loc[df['Order_Id'] == orderId, 'Trade'] = Trade
                df.loc[df['Order_Id'] == orderId, 'Status'] = status
                df.to_csv("data/trades.csv", index=False)
    return

def updateCanceledOpenOrders(ib, orderId, trademkt):     # I don't think this creates a new order but just cancels and existing order.  No new csv records created but updated.
    startTime = datetime.now()
    cancelledTF = False
    log.debug("updateCanceledOpenOrders: trademkt: {tm}".format(tm=trademkt))
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

def updateOrderWithCancelledSTP(ib, openOrderId, orderName, newstatus):
    # we have an open order from IB.  Going to run through our CSV file and make sure it exists.
    # if it doesn't exist, we will add it
    # this is for a single order
    # log.info("updateOrderWithCancelledSTP: we are looking for openOrderId")
    # REFERENCE fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled','Date_Updated]
    foundOrderInCSV = False
    x3 = 0
    if os.stat("data/orders.csv").st_size > 50:
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
    
def parseTradeString(ib,Trade):
    log.debug("parseTradeString: tradeInfo ")
    symbol = Trade.contract.symbol
    orderId = Trade.order.orderId
    orderType = Trade.order.orderType
    action = Trade.order.action
    quantity = Trade.order.totalQuantity
    status = Trade.orderStatus.status
    faProfile = Trade.order.faProfile
    account = Trade.order.account
    parentId, avgFillPrice = "", 0
    if orderType == "STP": parentId = Trade.order.parentId
    if status == "Filled": avgFillPrice = Trade.orderStatus.avgFillPrice
    date_order = Trade.log[0].time      # there are nested logs
    log.info("parseTradeString:: symbol: {s} orderId: {oi} orderType: {ot} action: {a} quantity: {q} status: {status} date_order: {do} ".format(s=symbol,oi=orderId,ot=orderType,a=action,q=quantity,status=status,do=date_order))
    return symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account
    
def parsePositionString(ib, positionInfo):
    #print("parsePositionString.  Here are the positions {p}".format(p=positionInfo))
    account = positionInfo.account
    symbol = positionInfo.contract.symbol
    quantity = positionInfo.position
    avgCost = positionInfo.avgCost
    return account, symbol, quantity, avgCost

def buildOrders(ib, tradeContract, action, quantity, cciProfile, buyStopLossPrice, sellStopLossPrice):
    #STP order
    #closeOpen = findOpenOrders(ib, True)
    parentId = ib.client.getReqId()
    #Entry Order
    log.info("buildOrders: tradeContract: {tc} ".format(tc=tradeContract))
    log.info("buildOrders: action: {a} ".format(a=action))
    log.info("buildOrders: qty : {q}".format(q=quantity))
    log.info("buildOrders: cciprofile: {p} ".format(p=cciProfile))
    log.info("buildOrders: buystoplossprice: {sl} ".format(sl=buyStopLossPrice))
    log.info("buildOrders: sellstoplossprice: {stl} ".format(stl=sellStopLossPrice))
    MktOrder = Order(
        action = action,
        orderType = "MKT",
        orderId = parentId,
        faProfile = cciProfile,
        totalQuantity = quantity,
        transmit = False
    )
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    stopAction = "Buy"
    stoplossprice = sellStopLossPrice
    if action == "Buy":
        stopAction = "Sell"
        stoplossprice = buyStopLossPrice

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
        tif = "GTC",
        transmit = True
    )
    tradestp = ib.placeOrder(tradeContract,stopLossOrder)
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
    symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account = parseTradeString(ib,trademkt)
    print("closePositionsOrders: trademkt ",trademkt)
    writeToCsv = writeOrdersToCSV(ib, MktOrder, "MktOrder",status, openOrderType = False)
    return trademkt, MktOrder