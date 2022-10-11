""" Create and Transmit Orders """
from pickle import FALSE
from types import TracebackType
from ib_insync.order import Order
import config
import constants
from ib_insync.contract import ContFuture, Future
import logger
import csv
import os
import pandas as pd
from datetime import datetime, timedelta
from csv import DictReader
import tkinter as tk
import logic


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

def createOrdersMain(ib, tradeContract, tradeAction, quantity, cciProfile, buyStopLossPrice, sellStopLossPrice, openOrderType, modTrailStopLoss, bars_15mclosePrice,myConnection):
    #trademkt, tradestp, parentId, MktOrder, stopLossOrder = buildOrders(ib, tradeContract, tradeAction, quantity, cciProfile, buyStopLossPrice, sellStopLossPrice, modTrailStopLoss, bars_15mclosePrice, "TRAIL")    # this places the order.  No confirm it was executed
    #buildOrders(ib, tradeContract, tradeAction, quantity, cciProfile, buyStopLossPrice, sellStopLossPrice, modTrailStopLoss, bars_15mclosePrice, "STP")    # this places the order.  No confirm it was executed
    #log.info("createOrdersMain: just created MKT: {l}   Order open/close true/false: {oot} ".format(l=trademkt,oot=openOrderType))
    #log.info("--------------------------------------------------------------------------------------")
    #log.info("createOrdersMain: just created  STP {s} order.  Order open/close true/false: {oot} ".format(s=tradestp,oot=openOrderType))
    # we don't want to enter into the DB rather wait for new order event to trigger.  This gives us confirmation it was received and we get more information.
    # #symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,trademkt)
    #wroteOrdersToCSV = writeOrdersToCSV(ib, MktOrder, "MktOrder", status, openOrderType)
    #filledTF, fillStatus = checkForOpenOrderStatus(ib, trademkt, "trademkt", trademkt.orderStatus.status)    # moving to event driven trade updates
    #if fillStatus:
    #    updateOrders = writeTradeToCSV(ib, trademkt, "tradeMkt", status, openOrderType = True)
    #symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,tradestp)
    #wroteOrdersToCSV = writeOrdersToCSV(ib, stopLossOrder, "stopLossOrder", status, openOrderType)
    #countOpenOrders(ib,myConnection)
    return True

# this is counting for top of the loop for information only
def countOpenOrders(ib,tradeInfo, myConnection):                 # This is to find open STP orders only
#    log.info("countOpenOrders ************** in the countOpenOrders function *****************")
#    openOrdersList = ib.openOrders()
#    log.info("countOpenOrders openOrdersList: {ool}".format(ool=openOrdersList))
#    for orderRow in openOrdersList:
#        orderId, orderType, action, quantity, clientId, permId = parseOrderString(ib,orderRow)
#        cur = myConnection.cursor()
#        # order check
#        cur.execute("select * from orders where permid = '{oi}'".format(oi=permId))
#        orderQueryList = cur.fetchone()
#        if cur.rowcount == 0:    # no entry in orders file need to add
#            cur.execute("insert into orders (order_id,order_type,permid) values ('{oi}','{ot}','{p}')".format(oi=orderRow.orderId,ot=orderRow.orderType,p=orderRow.permId))
#            myConnection.commit()
#        else:
#            log.info("we already have this order in the db")
#    return len(openOrdersList)
    return

def addNewOrders(ib,orderInfo, myConnection,self):                 # This is to find open STP orders only
    log.info("addNewOrders ************** in the addNewOrders function *****************")
    #log.info("addNewOrders::order info coming from main ")
    #log.info(orderInfo)    # we are going to show each row below
    counter = 0
#    cur = myConnection.cursor()
    #log.info("all orders type: {t}: {o}".format(t=type(orderInfo),o=orderInfo)) we get this from mainlocal.py
    for orderRow in orderInfo:
#        log.info("while order in orderInfo (Trade) {w}".format(w=orderRow))
#        cur.execute("select * from orders where permid = '{oi}'".format(oi=orderRow.permId))
#        orderQueryList = cur.fetchone()
        #updateOrderWhenPlaced(myConnection,"",orderRow,"") no contract information
        updateOrderOrder(myConnection,orderRow,"")
        updateTradeMain(myConnection,orderRow,"")
        #updateOrderStatus(myConnection,orderInfo) no order status either
        if orderRow.filledQuantity < 1:
            counter=counter + 1
#        if cur.rowcount == 0:
#            log.info(type(orderRow))
#            if hasattr(orderRow,"filledQuantity"):    #sometimes modified stp order trigger new trade when it isn't  This didn't work because ibysnc returned this huge number
#            if hasattr(orderRow,"filledQuantity") and orderRow.filledQuantity < 10000:    #sometimes modified stp order trigger new trade when it isn't  This didn't work because ibysnc returned this huge number
#                try:    # this would assume a STP order so there is more data
#                    sql = "insert into orders (order_id,order_type,permid,action,filled_qty,lmtprice,auxprice,tif) VALUES \
#                        ('{oi}','{ot}','{id}','{a}',{q},{lp},{ap},'{tif}')". \
#                        format(oi=orderRow.orderId,ot=orderRow.orderType,id=orderRow.permId,a=orderRow.action,q=orderRow.filledQuantity,lp=orderRow.lmtPrice,ap=orderRow.auxPrice,tif=orderRow.tif)

 #                   log.info(sql)
#                    cur.execute("insert into orders (order_id,order_type,permid,action,filled_qty,lmtprice,auxprice,tif) VALUES \
#                        ('{oi}','{ot}','{id}','{a}',{q},{lp},{ap},'{tif}')". \
#                        format(oi=orderRow.orderId,ot=orderRow.orderType,id=orderRow.permId,a=orderRow.action,q=orderRow.filledQuantity,lp=orderRow.lmtPrice,ap=orderRow.auxPrice,tif=orderRow.tif))
#                    myConnection.commit()
#                except: # this would assume a MKT order with much less data
#                    log.info("insert into orders (order_id,order_type,permid,action,quantity) VALUES \
#                        ('{oi}','{ot}','{id}','{a}',{q},'{s})". \
#                        format(oi=orderRow.orderId,ot=orderRow.orderType,id=orderRow.permId,a=orderRow.action,q=orderRow.totalQuantity))
#                    cur.execute("insert into orders (order_id,order_type,permid,action,quantity) VALUES \
#                        ('{oi}','{ot}','{id}','{a}',{q})". \
#                        format(oi=orderRow.orderId,ot=orderRow.orderType,id=orderRow.permId,a=orderRow.action,q=orderRow.totalQuantity))
#                    myConnection.commit()
#            else:
#                log.info("insert into orders (order_id,order_type,permid,action,quantity) VALUES \
#                    ('{oi}','{ot}','{id}','{a}',{q})".\heat seatsta
#                    format(oi=orderRow.orderId,ot=orderRow.orderType,id=orderRow.permId,a=orderRow.action,q=orderRow.totalQuantity))
#                cur.execute("insert into orders (order_id,order_type,permid,action,quantity) VALUES \
#                    ('{oi}','{ot}','{id}','{a}',{q})".\
#                    format(oi=orderRow.orderId,ot=orderRow.orderType,id=orderRow.permId,a=orderRow.action,q=orderRow.totalQuantity))
#                myConnection.commit()
#           open orders should never had filled information and such
#        elif hasattr(orderRow,"filledQuantity") and orderRow.filledQuantity >= 1:       #maybe the order is in the DB but the order previously was not fill
#            cur.execute("select * from orders where permid = '{oi}' and filled_qty = 0".format(oi=orderRow.permId))
#            cur.execute("select * from orders where permid = '{oi}'".format(oi=orderRow.permId))
#            orderQueryListFilled = cur.fetchone()
#            if cur.rowcount > 0:
#                cur.execute("update orders set filled_qty = {q},lmtprice = {lp},auxprice ={ap} where permid = '{p}'".format(q=orderRow.filledQuantity,p=orderRow.permId,lp=orderRow.lmtPrice,ap=orderRow.auxPrice,))
#            log.info("we already have this order in the db but filled was 0 so we updated it")
    self.app.logicopenOrders.update(str(counter))
    return

def addNewTrades(ib,tradeInfo, myConnection,self):                 # This is to find open STP orders only
    # in the trade record we can expect contract, order and orderStatus.  The other tuple headers might not be there
    log.info("addNewTrades ************** in the addNewTrades function *****************")
    #log.info(tradeInfo)
    cur = myConnection.cursor()
    try:
        for tradeRow in tradeInfo:
            log.info("tradeRow")
            log.info(tradeRow)
            if hasattr(tradeRow,"filledQuantity"):    #sometimes modified stp order trigger new trade when it isn't
                log.info("while order {w}".format(w=tradeRow))
                cur.execute("select * from ibtrades where permid = '{oi}'".format(oi=tradeRow.order.permId))
                orderQueryList = cur.fetchone()
                if cur.rowcount == 0:    # no entry in orders file need to add
                    cur.execute("insert into ibtrades (permid,contract_month,symbol,order_type,lmt_price,aux_price,trail_stop_price,account,\
                        filled_qty,parent_permid,status,avg_fill_price,contract_id,source) VALUES \
                        ('{id}','{cm}','{s}','{ot}',{lp},{ap},{ssp},'{act}',{q},'{ppi}','{status}',{afp},'{conid}','{source}')". \
                        format(id=tradeRow.order.permId,cm=tradeRow.contract.lastTradeDateOrContractMonth,s=tradeRow.contract.localSymbol,ot=tradeRow.order.orderType, \
                        lp=tradeRow.order.lmtPrice,ap=tradeRow.order.auxPrice,ssp=tradeRow.order.trailStopPrice,act=tradeRow.order.account,q=tradeRow.order.filledQuantity, \
                        ppi=tradeRow.order.parentPermId,status=tradeRow.orderStatus.status,afp=tradeRow.orderStatus.avgFillPrice,conid=tradeRow.contract.conId,source=tradeRow \
                        ))
                    myConnection.commit()
                    try:
                        cur.execute("update ibtrades set date = '{date}', shares = {shares}, price = {price}, source = '{source}' where permid= '{id}'". \
                            format(id=tradeRow.order.permId,date=tradeRow.fills[0].execution.time,shares=tradeRow.fills[0].execution.shares,price=tradeRow.fills[0].execution.price,source=tradeRow))
                        myConnection.commit()
                    except:
                        log.info("no execution attribute")
                    try:
                        cur.execute("update ibtrades set commission = {comm},realized_pnl = {rpnl}, source = '{source}' where permid= '{id}'". \
                            format(id=tradeRow.order.permId,comm=tradeRow.fills[0].commissionReport.commission,rpnl=tradeRow.fills[0].commissionReport.realizedPNL,source=tradeRow))
                        myConnection.commit()
                    except:
                        log.info("no commission attribute")
            else:   #check if record exists and fills changed.  In the event we have a trade without a fill
                cur.execute("select * from orders where permid = '{oi}' and filled_qty = 0".format(oi=tradeRow.permId))
                orderQueryList = cur.fetchone()
#                if cur.rowcount == 0:
#                    cur.execute("insert into ibtrades (permid,contract_month,symbol,order_type,lmt_price,aux_price,trail_stop_price,account,\
#                        filled_qty,parent_permid,status,avg_fill_price,contract_id,source) VALUES \
#                        ('{id}','{cm}','{s}','{ot}',{lp},{ap},{ssp},'{act}',{q},'{ppi}','{status}',{afp},'{conid}','{source}')". \
#                        format(id=tradeRow.order.permId,cm=tradeRow.contract.lastTradeDateOrContractMonth,s=tradeRow.contract.localSymbol,ot=tradeRow.order.orderType, \
#                        lp=tradeRow.order.lmtPrice,ap=tradeRow.order.auxPrice,ssp=tradeRow.order.trailStopPrice,act=tradeRow.order.account,q=tradeRow.order.filledQuantity, \
#                        ppi=tradeRow.order.parentPermId,status=tradeRow.orderStatus.status,afp=tradeRow.orderStatus.avgFillPrice,conid=tradeRow.contract.conId,source=tradeRow \
#                        ))
 #                   myConnection.commit()
                log.info("we already have this order in the db")
    except:
        log.info("we were not able to iterate throught the trade record")
    return

def updateFills(ib,fillInfo, myConnection,self):                 # This is to find open STP orders only
    # in the trade record we can expect contract, order and orderStatus.  The other tuple headers might not be there
    log.info("updateFills ************** in the updateFills function *****************")
    #log.info(tradeInfo)
    cur = myConnection.cursor()
    for fillRow in fillInfo:
        log.info("while order {w}".format(w=fillRow))
        if hasattr(fillRow,"execution"):    #sometimes modified stp order trigger new trade when it isn't
            log.info("while order {w}".format(w=fillRow))
            # we have to assume their is an ibtrades entry correlated to this fill
            cur.execute("update ibtrades set date = '{date}', shares = {shares}, price = {price}, source = '{source}', account = '{acct}' where permid= '{id}'". \
                format(id=fillRow.execution.permId,date=fillRow.execution.time,shares=fillRow.execution.shares,price=fillRow.execution.avgPrice,acct=fillRow.execution.acctNumber))
            myConnection.commit()
        if hasattr(fillRow,"commissionReport"):
            cur.execute("update ibtrades set commission = {comm}, realizedPNL = {pnl} where permid= '{id}'". \
                format(id=fillRow.execution.permId,comm=fillRow.commissionReport.commission,pnl=fillRow.execution.realizedPNL))
            myConnection.commit()
    return

def checkForFilledOrders(ib,myConnection,self):
    #download order from IB and then step through the filled and make sure there is a record in the orders_status table.  We can't get orders after a restart - i don't th9ink need to confirm
    openOrders = ib.orders()
    log.info("openOrders pull {o}".format(o=openOrders))
    addNewOrders(ib,openOrders,myConnection,self)
    openTrades = ib.trades()
    addNewTrades(ib,openTrades,myConnection,self)
    return

def countOpenPositions(ib,accountName):
    log.info("countOpenPositions: ")
    position_long_tf = False
    position_short_tf = False
    long_position_qty, short_position_qty, account_qty = 0, 0, 0
    positions = ib.positions()
    log.info("countOpenPositions: positions: {p} count: {c} ".format(p=positions,c=len(positions)))
    #x = 0
    for position in positions:
        account, symbol, quantity, avgCost = parsePositionString(ib,position)
        log.info("countOpenPositions: positions account should be:{a} ".format(a=account))
        if (symbol) == "ES":
            if account == accountName:
                account_qty = account_qty + quantity
            if quantity > 0:
                long_position_qty += quantity
                position_long_tf = True
            elif position[2] < 0:
                short_position_qty += quantity
                position_short_tf = True
            log.info("Have a position in : {a}".format(a=account))
            log.info ("long qty:           {lqty}".format(lqty = long_position_qty))
            log.info("short qty:           {sqty} ".format(sqty = short_position_qty))  
            log.info("account qty:           {sqty} ".format(sqty = account_qty))
    return position_long_tf, position_short_tf, long_position_qty, short_position_qty, account_qty

def closeOpenOrders(ib):                 # This is to find open STP orders and cancel 
    log.info("************** in the closeOpenOrder function *****************")
    openOrdersList = ib.openOrders()
    x = 0
    # not sure we need to differentiate between buy or sell stop orders below
    for openOrder  in openOrdersList:
        #symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,openOrdersList[x])
        #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
        #log.info("closeOpenOrder: - we have open order records: opendOrderId: {ooi} orderType: {ot} ".format(ooi=orderId, ot=orderType))
        log.info("closeOpenOrder: closing all open orders - currently working on: {oo}".format(oo=openOrder))
        trademkt = ib.cancelOrder(openOrder)            # don't need to place order when cancelling
        #log.info("\n----------------------- openOrdersList ---------------\n",openOrdersList[x])
        #log.info("----------------------- TRADEMKT ---------------: {t}".format(t=trademkt))
        log.info("----------------------- TRADEMKT ---------------: ")
        #validatedOpenOrders = validateOpenOrdersCSV(ib, orderId, status)
        symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,trademkt)      
        #checkOrderStatus = updateCanceledOpenOrders(ib, orderId, trademkt)   # update each order that we cancelled
        log.info("lets see what event is trigger on the cancelled order ")
        x += 1
    return len(openOrdersList)

def closeOpenPositions(ib, tradeContract):             #we want to close open positions as known in IB as well as keep our CSV files up to date.
    # we need to manage the following here
    # get open positions from IB
    # close the positions order
    # create order entry in csv
    # track status and update orders and trade csv and positions.
    log.info("closeOpenPositions: ")
    positionLong, positionShort = 0, 0
    positions = ib.positions()
    log.info("closeOpenPositions: number of positions (not quantity): {op}".format(op=len(positions)))
    #updatedPositions = updatePositionsCSV(ib,positions)
    x = 0
    while x < len(positions):
        orderFoundTF = False
        account, symbol, quantity, avgCost = parsePositionString(ib,positions[x])   # need abs quty since buy/sell abs and position are plus and minus
        log.info("closeOpenPositions: - we have open Position records: symbol: {s} and len of positions: {lp}".format(s=symbol,lp=len(positions)))
        action = "Buy"
        orderQty = abs(quantity)
        openClose = "C"
        if symbol == "ES" and quantity > 0:
            action = "Sell"
            orderQty = -quantity
        #orderFoundTF = True
        log.info("closeOpenPositions - we have open order records: Long {one} with the action: {act}".format(one=abs(quantity),act=action))
        positionLong += quantity
        #temp = temphold(orderId=openOrder[x].permId)
        trademkt, MktOrder = closePositionsOrders(ib,tradeContract, account, action, abs(quantity))
        symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,trademkt)
        #log.info("\n----------------------- openOrdersList ---------------\n",positions[x])
        #log.info("\n----------------------- TRADEMKT ---------------\n",trademkt)
        writeToCsv = writeOrdersToCSV(ib, MktOrder, "MktOrder",status, openOrderType = False)               # writing to orders csv
        log.info("closeOpenPositions: cancel order sent -> cv: {cv} and status: {s} ".format(cv=trademkt, s=status))
        # checking status of the order
        #filledTF, openOrderStatus = checkForOpenOrderStatus(ib, trademkt, "trademkt", status)  # doing with event driven trade info
        #if filledTF:
        #    writeToCsv = writeTradeToCSV(ib,trademkt,"trademkt",status, openOrderType = False)
        x += 1
    return 

def writeOrdersToCSV(ib, orderInfo, orderName, status, openOrderType):
    orderId, orderType, action, quantity, permId = parseOrderString(ib,orderInfo)
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
        histwriter.writerow({'Order_Id': orderId, 'permID': permId, 'Order': orderInfo, 'Status': status, 'Date_Pending': time, 'Date_Cancelled': '1/1/20', 'Date_Filled': datetime.now(),'To_Open':openOrderType})
    return

def checkForOpenOrderStatus(ib, orderInfo, orderName, status):
    # going through orders looking for filled and updating trades   
    startTime = datetime.now()
    while True:
        symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,orderInfo)
        log.info("Checking for status change.  status:{s})".format(s=status))
        if status not in ['PendingSubmit','PreSubmitted']:
            log.info("checkForOpenOrderStatus: Open Executed worked.  Fill Status is:{fs}".format(fs=status))
            filledTF = True
            break
        elif (datetime.now() - startTime).total_seconds() > 100:
            log.debug("order failed for: {0} ".format(orderInfo.order.orderId))
            filledTF = False
            break
        log.info("\ncheckForOpenOrderStatus: going to sleep {s}\n".format(s=(datetime.now() - startTime).total_seconds()))
        ib.sleep(1.0)
    return filledTF, status

def createTradesCSVFromEvent(ib, Trade, eventType):    # called from main.py as events come in RE trades
    log.info("updateTradesCSVFromEvent: updating CSV file with event type {et} expecting only one record ".format(et=eventType))
    symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,Trade)
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
        fieldnames = ['Order_Id','Perm ID','Account','Type', 'Action','Status','EndingQty','PendingSubmit','PreSubmitted','Submitted','PendingCancel','Cancelled','Filled','ToOpen','ParentId','FAProfile','AvgFillPrice','TotalQty','Trade']
        histwriter = csv.DictWriter(ordersCSV, fieldnames = fieldnames)
        if os.stat("data/trades.csv").st_size < 50: #don't want to keep repeating the header
            histwriter.writeheader()
        histwriter.writerow({'Order_Id':orderId,'Perm ID':permID,'Account':account,'Type':orderType, 'Action':action,'Status':status,'EndingQty':account_qty,'PendingSubmit':tmpPendingSubmit, 'PreSubmitted':tmpPreSubmitted, 'Submitted':tmpSubmitted,'PendingCancel':tmpPendingCancel,'Cancelled':tmpCancelled, 'Filled':tmpFilled,'ToOpen':'True', 'ParentId': tmpParentId, 'FAProfile': faProfile,'AvgFillPrice': tmpAvgFillPrice, 'TotalQty':quantity, 'Trade': Trade})
    #logic.update_tk_text("update tk from orders.py.  Just finished updating CSV after a stop order")
    return 

def updateTradesCSVFromEvent(ib, Trade, eventType):    # called from main.py as events come in RE trades
    # we have an open order from IB.  Going to run through our CSV file and make sure it exists.
    # if it doesn't exist, we will add it
    #log.info("we are looking for openOrderId")
    # REFERENCE fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled','Date_Updated]
    
#    symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,Trade)
#    foundOrderInCSV = False
#    with open('data/trades.csv', newline ='') as csvfile:
#        reader = csv.DictReader(csvfile)
#        for row in reader:
#            if row['Order_Id'] == orderId:
#                csvfile.close()
#                df = pd.read_csv("data/trades.csv")   # https://stackoverflow.com/questions/11033590/change-specific-value-in-csv-file-via-python
#                #df.head(5)   #log.infos first 5 rows
#                if status == "Filled": df.loc[df['Order_Id'] == orderId, 'AvgFillPrice'] = avgFillPrice
#                if status == 'PreSubmitted': df.loc[df['Order_Id'] == orderId, 'Presubmitted'] = datetime.now()
#                if status == 'PendingSubmit': df.loc[df['Order_Id'] == orderId, 'PendingSubmit'] = datetime.now()        
#                if status == 'Cancelled': df.loc[df['Order_Id'] == orderId, 'Cancelled'] = datetime.now()        
#                if status == 'Submitted': df.loc[df['Order_Id'] == orderId, 'Submitted'] = datetime.now()        
#                if status == 'Filled': df.loc[df['Order_Id'] == orderId, 'Filled'] = datetime.now()        
#                df.loc[df['Order_Id'] == orderId, 'Trade'] = Trade
#                df.loc[df['Order_Id'] == orderId, 'Status'] = status
#                df.to_csv("data/trades.csv", index=False)
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
    log.info("we are looking for openOrderId from IB open orders in our CSV file openOrderId: {id}".format(id=openOrderId))
    # REFERENCE fieldnames = ['Order_Id','Order','Status','Date_Pending','Date_Cancelled','Date_Filled','Date_Updated]
    foundOrderInCSV = False
    with open('data/orders.csv', newline ='') as csvfile:
        reader = csv.DictReader(csvfile)
        log.info("dictionary of orders.csv: ".format(reader))
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
    clientId = tradeInfo.clientId
    permId = tradeInfo.permId
    return orderId, orderType, action, quantity, clientId, permId
    
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
    permID = Trade.order.permId
    parentId, avgFillPrice = "", 0
    if orderType == "STP": parentId = Trade.order.parentId
    if status == "Filled": avgFillPrice = Trade.orderStatus.avgFillPrice
    date_order = Trade.log[0].time      # there are nested logs
    log.info("parseTradeString:: symbol: {s} orderId: {oi} orderType: {ot} action: {a} quantity: {q} status: {status} date_order: {do} permID: {pi} ".format(s=symbol,oi=orderId,ot=orderType,a=action,q=quantity,status=status,do=date_order,pi=permID))
    return symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID
    
def parsePositionString(ib, positionInfo):
    #log.info("parsePositionString.  Here are the positions {p}".format(p=positionInfo))
    account = positionInfo.account
    symbol = positionInfo.contract.symbol
    quantity = positionInfo.position
    avgCost = positionInfo.avgCost
    return account, symbol, quantity, avgCost

def buildOrders(ib, myConnection, tradeContract, action, quantity, cciProfile, buyStopLossPrice, sellStopLossPrice, modTrailStopLoss, bars_15mclosePrice,STPorTRAIL):
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
    log.info("buildOrders: bars_15mclosePrice: {cp}".format(cp=bars_15mclosePrice))
    
    if action == "Sell":
        stopAction = "Buy"
        stoplossprice = sellStopLossPrice
        stoplimitprice = bars_15mclosePrice - 20
        limitPrice = bars_15mclosePrice - 15
        trailLimitPrice = bars_15mclosePrice + config.trailStopOffset
    elif action == "Buy":
        limitPrice = bars_15mclosePrice + 20
        stopAction = "Sell"
        stoplossprice = buyStopLossPrice
        stoplimitprice = bars_15mclosePrice + 15
        trailLimitPrice = bars_15mclosePrice - config.trailStopOffset

    log.info("close price: {c} stoplimitprice: {slp} limitprice {lp} trailLimitPrice {tlp}".format(c=bars_15mclosePrice,slp=stoplimitprice,lp=limitPrice,tlp=trailLimitPrice))
    if STPorTRAIL == "STP":
        MktOrder = Order(
            action = action,
            orderType = "MKT",
            #lmtPrice = limitPrice,
            orderId = parentId,
            faProfile = cciProfile,
            totalQuantity = quantity,
            openClose = "O",
            transmit = False
            
        )
        trademkt = ib.placeOrder(tradeContract,MktOrder)
        log.info("market order {l}".format(l=trademkt))
        updateOrderWhenPlaced(myConnection,"O",trademkt.order,trademkt.contract,trademkt.orderStatus)
    #
        #Stop Loss Order
        
        stopLossOrder = Order(
            action = stopAction,
            orderType = "STP",
            auxPrice = stoplossprice,
            lmtPrice = stoplimitprice,
            #trailStopPrice = modTrailStopLoss,
            faProfile = cciProfile,
            totalQuantity = quantity,
            orderId = ib.client.getReqId(),
            parentId = parentId,
            outsideRth = True,
            tif = "GTC",
            openClose = "C"
        )
        tradestp = ib.placeOrder(tradeContract,stopLossOrder)
        log.info("stop order {l}".format(l=tradestp))
        updateOrderWhenPlaced(myConnection,"C",tradestp.order,tradestp.contract,tradestp.orderStatus)
# Trail Order *************************************************
    elif STPorTRAIL == "TRAIL":
        limitOrder = Order(
        orderId = parentId,
        action = action,
        orderType = "LMT",
        lmtPrice = limitPrice,
        faProfile = cciProfile,
        totalQuantity = quantity,
        transmit = False,
        tif = "IOC",
        openClose = "O"
        )
        trademkt = ib.placeOrder(tradeContract,limitOrder)
        log.info("limit order {l}\n".format(l=trademkt))
    
        trailStopLossOrder = Order(
            action = stopAction,
            orderType = "TRAIL",
            auxPrice = 7,
            trailStopPrice = trailLimitPrice,
            faProfile = cciProfile,
            totalQuantity = quantity,
            orderId = ib.client.getReqId(),
            parentId = parentId,
            outsideRth = True,
            tif = "GTC",
            transmit = True,
            openClose = "C"
        )
        tradestp = ib.placeOrder(tradeContract,trailStopLossOrder)
        log.info("trail order {l}\n".format(l=tradestp))
    return

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
        transmit = True,
        openClose = "C"
    ) 
    trademkt = ib.placeOrder(tradeContract,MktOrder)
    symbol, orderId, orderType, action, quantity, status, date_order, faProfile, parentId, avgFillPrice, account, permID = parseTradeString(ib,trademkt)
    log.info("closePositionsOrders: trademkt ",trademkt)
    writeToCsv = writeOrdersToCSV(ib, MktOrder, "MktOrder",status, openOrderType = False)
    return trademkt, MktOrder

def modifySTPOrder(ib, modBuyStopLossPrice,modSellStopLossPrice, closePrice,myConnection):
    contContract = ib.reqContractDetails(ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE))
    tradeContract = contContract[0].contract
    openOrdersList = ib.openOrders()
    #x = 0
    #cnt = 0
    if len(openOrdersList) > 0:
        for openOrder in openOrdersList:
            log.info("----------------------- modify stop orders ---------------: ")
            log.info("Action: {a} orderType: {ot} auxPrice: {ap} modBuyStopLossPrice: {mbslp} modSellStopLossPrice: {msslp} # of orders: {no} close: {c}" \
                .format(a=openOrder.action,ot=openOrder.orderType,ap=openOrder.auxPrice,mbslp=modBuyStopLossPrice,msslp=modSellStopLossPrice,no=len(openOrdersList),c=closePrice))
            # for debugging
            log.info("openOrdersList: {ool}".format(ool=openOrdersList))
            if openOrder.action.upper() == "BUY" and openOrder.orderType == "STP" and openOrder.auxPrice > modSellStopLossPrice:
                #cnt = cnt +1
                log.info("new auxPrice buy: {ap}  new lmtprice {lt}".format(ap=modBuyStopLossPrice,lt=modSellStopLossPrice - 1))
                openOrder.auxPrice = modSellStopLossPrice
                #openOrdersList[x].lmtPrice = modSellStopLossPrice - 10
                #openOrder = openOrdersList[x]
                log.info("openOrdersList: {oo}".format(oo=openOrder))
                ib.placeOrder(tradeContract,openOrder)
            elif openOrder.action.upper() == "SELL" and openOrder.orderType == "STP" and openOrder.auxPrice < modBuyStopLossPrice:
                #cnt = cnt +1
                log.info("new auxPrice buy: {ap} from: {pp} new lmtprice {lt}".format(ap=modSellStopLossPrice,pp=openOrder.auxPrice,lt=modBuyStopLossPrice +1))
                openOrder.auxPrice = modBuyStopLossPrice
                #openOrdersList[x].lmtPrice = modBuyStopLossPrice + 10
                #openOrder = openOrdersList[x]
                log.info("openOrdersList: {oo}".format(oo=openOrder))
                ib.placeOrder(tradeContract,openOrder)
            else:
                log.info("modifySTPOrder:: we have open orders but either they were not better stops or not STP orders.  order action: \
                    {oa} type: {t} aux price: {ap} mod pricebuy: {mpb} mod price sell: {mps}".format(oa = openOrder.action, t = openOrder.orderType, ap = openOrder.auxPrice, mpb = modBuyStopLossPrice, mps = modSellStopLossPrice))
            #x += 1
            #log.info("\nnumber of open order is:{o}".format(o=x))
    else:
        log.info("no open stop orders to modify")
    return len(openOrdersList)

def getListOfTrades(ib):
    recentTradesList = ib.trades()
    #log.info("getListofTrades: recent trades -> {rt}".format(rt=recentTradesList))
    # fills is in both trades and fills.  fills has what we need but Trades also has the trade detail that we want so we have to use trades
    if len(recentTradesList) < 0: 
        log.info("getListOfTrades:: no trades in the current session")
    else:
        for i in range(len(recentTradesList)):
            #get info from entry
            ListOfTradesReadCsv(recentTradesList[i])
    return

def ListOfTradesReadCsv(recentTradesListItem):
    log.info("New permId {p}".format(p=recentTradesListItem.order.permId))
    return

def ListOfTradesWriteCsv(recentTradesListItem):
    with open('data/trades.csv', mode='a', newline = '') as writeTrades:
        fieldnames = ['Order_Id','PermID','Account','Type','Action','Status','EndingQty','PendingSubmit','PreSubmitted','Submitted','PendingCancel','Cancelled','Filled','ToOpen','ParentId','FAProfile','AvgFillPrice','TotalQty','Trade']
        histwriter = csv.DictWriter(writeTrades, fieldnames = fieldnames)
        histwriter.writerow({'Order_Id':recentTradesListItem.order.orderId,'PermID':recentTradesListItem.order.permId,'Account':recentTradesListItem.order.account,'Type':recentTradesListItem.order.orderType,\
            'Action':recentTradesListItem.order.action,'Status':recentTradesListItem.orderStatus.status, 'ParentId': recentTradesListItem.orderStatus.parentId, 'Trade': recentTradesListItem})
    return

def updateOrderWhenPlaced(myConnection,oClose,orderInfo,contractInfo,orderStatusInfo):
    log.info(orderInfo)
    log.info(orderStatusInfo)
    log.info(contractInfo)
    #we know the order when placed has the following components: contract, order, orderstatus, fills and log
    updateOrderContract(myConnection,contractInfo)
    updateOrderOrder(myConnection,orderInfo,oClose)
    updateOrderStatus(myConnection,orderStatusInfo)
    #cur = myConnection.cursor()
    #cur.execute("insert into orders ({c},open_close) VALUES ('{id}','{oc}')".format(c=col,id=coldata,oc=oClose))
    #myConnection.commit()
    return

def updateOrderContract(myConnection,orderInfo):
    log.info("updateOrderContract")
    cur = myConnection.cursor()
    cur.execute("select from contract where con_id = '{c}'".format(c=orderInfo.conId))
    cur.fetchone()
    if cur.rowcount == 0: 
        cur.execute("insert into contract (con_id) VALUES ('{c}')".format(c=orderInfo.conId))
    else:
        if hasattr(orderInfo,"secType"):
            cur.execute("update contract set sec_type = '{a}' where con_id='{c}'".format(a=orderInfo.secType,c=orderInfo.conId))
        if hasattr(orderInfo,"symbol"):
            cur.execute("update contract set symbol = '{a}' where con_id='{c}'".format(a=orderInfo.symbol,c=orderInfo.conId))
        if hasattr(orderInfo,"lastTradeDateOrContractMonth"):
            cur.execute("update contract set contract_month = '{a}' where con_id='{c}'".format(a=orderInfo.lastTradeDateOrContractMonth,c=orderInfo.conId))
        if hasattr(orderInfo,"multiplier"):
            cur.execute("update contract set multiplier = {a} where con_id='{c}'".format(a=orderInfo.multiplier,c=orderInfo.conId))
        if hasattr(orderInfo,"exchange"):
            cur.execute("update contract set exchange = '{a}' where con_id='{c}'".format(a=orderInfo.exchange,c=orderInfo.conId))
        if hasattr(orderInfo,"currency"):
            cur.execute("update contract set currency = '{a}' where con_id='{c}'".format(a=orderInfo.currency,c=orderInfo.conId))
        if hasattr(orderInfo,"localSymbol"):
            cur.execute("update contract set local_symbol = '{a}' where con_id='{c}'".format(a=orderInfo.localSymbol,c=orderInfo.conId))
        if hasattr(orderInfo,"tradingClass"):
            cur.execute("update contract set trading_class = '{a}' where con_id='{c}'".format(a=orderInfo.tradingClass,c=orderInfo.conId))
        myConnection.commit()
    return

def updateOrderOrder(myConnection,orderInfo,oClose):
    log.info("updateOrderOrder")
    cur = myConnection.cursor()
    cur.execute("select from orders where order_id = '{c}'".format(c=orderInfo.orderId))
    cur.fetchone()
    if cur.rowcount == 0:
        cur.execute("insert into orders (order_id) VALUES ('{c}')".format(c=orderInfo.orderId))
        myConnection.commit()
    else:
        log.info("order already in DB going to update columns")
        if oClose == "O" or oClose == "C":
            cur.execute("update orders set open_close = '{a}' where order_id='{c}'".format(a=oClose,c=orderInfo.orderId))
        if hasattr(orderInfo,"action"):
            cur.execute("update orders set action = '{a}' where order_id='{c}'".format(a=orderInfo.action,c=orderInfo.orderId))
        if hasattr(orderInfo,"totalQuantity"):
            cur.execute("update orders set quantity = {a} where order_id='{c}'".format(a=orderInfo.totalQuantity,c=orderInfo.orderId))
        if hasattr(orderInfo,"orderType"):
            cur.execute("update orders set order_type = '{a}' where order_id='{c}'".format(a=orderInfo.orderType,c=orderInfo.orderId))
        if hasattr(orderInfo,"faProfile"):
            cur.execute("update orders set fa_profile = '{a}' where order_id='{c}'".format(a=orderInfo.faProfile,c=orderInfo.orderId))
        myConnection.commit()
    return

def updateOrderStatus(myConnection,orderInfo):
    log.info("updateOrderStatus")
    cur = myConnection.cursor()
    cur.execute("select from orders_status where order_id = '{c}'".format(c=orderInfo.orderId))
    cur.fetchone()
    if cur.rowcount == 0:
        cur.execute("insert into orders_status (order_id) VALUES ('{c}')".format(c=orderInfo.orderId))
        myConnection.commit()
    else:
        log.info("order already in DB going to update columns")
        if hasattr(orderInfo,"status"):
            cur.execute("update orders_status set status = '{a}' where order_id='{c}'".format(a=orderInfo.status,c=orderInfo.orderId))
        if hasattr(orderInfo,"filled"):
            cur.execute("update orders_status set filled = {a} where order_id='{c}'".format(a=orderInfo.filled,c=orderInfo.orderId))
        if hasattr(orderInfo,"remaining"):
            cur.execute("update orders_status set remaining = {a} where order_id='{c}'".format(a=orderInfo.remaining,c=orderInfo.orderId))
        if hasattr(orderInfo,"avgFillPrice"):
            cur.execute("update orders_status set avg_fill_price = {a} where order_id='{c}'".format(a=orderInfo.avgFillPrice,c=orderInfo.orderId))
        cur.execute("update orders_status set datetime = '{a}' where order_id='{c}'".format(a=datetime.now(),c=orderInfo.orderId))        
        myConnection.commit()
    return

def updateTradeMain(myConnection,tradeInfo,oClose):
    log.info("updateTradeMain")
    if hasattr(tradeInfo,"order"):
        updateTradeOrder(myConnection,tradeInfo.order)
    if hasattr(tradeInfo,"trade"):
        updateTradeContract(myConnection,tradeInfo.contract,tradeInfo.order.orderId)
    if hasattr(tradeInfo,"orderStatus"):
        updateTradeStatus(myConnection,tradeInfo.orderStatus,tradeInfo.order.orderId)

    return
    
def updateTradeOrder(myConnection,orderInfo):    
    log.info("updateTradeOrder")
    cur = myConnection.cursor()
    cur.execute("select from ibtrades where order_id = '{c}'".format(c=orderInfo.orderId))
    cur.fetchone()
    if cur.rowcount == 0:
        cur.execute("insert into ibtrades (order_id, order_type, action, fa_profile) VALUES ('{c}','{t}','{a}','{p}')".format(c=orderInfo.orderId,t=orderInfo.orderType,a=orderInfo.action,p=orderInfo.faProfile))
        myConnection.commit()
    else:
        log.info("updateTradeOrder: order already in DB going to update columns")
        if hasattr(orderInfo,"action"):
            cur.execute("update ibtrades set action = '{a}' where order_id='{c}'".format(a=orderInfo.action,c=orderInfo.orderId))
        if hasattr(orderInfo,"orderType"):
            cur.execute("update ibtrades set order_type = '{a}' where order_id='{c}'".format(a=orderInfo.orderType,c=orderInfo.orderId))
        if hasattr(orderInfo,"faProfile"):
            cur.execute("update ibtrades set fa_profile = '{a}' where order_id='{c}'".format(a=orderInfo.faProfile,c=orderInfo.orderId))
        myConnection.commit()
    return

def updateTradeContract(myConnection,contractInfo,orderId):    
    log.info("updateTradeOrder")
    cur = myConnection.cursor()
    # we have to assume there is already a ibtrade record from the previous step
    if hasattr(contractInfo,"symbol"):
        cur.execute("update ibtrades set symbol = '{a}' where order_id='{c}'".format(a=contractInfo.symbol,c=orderId))
    if hasattr(contractInfo,"lastTradeDateOrContractMonth"):
        cur.execute("update ibtrades set contract_month = '{a}' where order_id='{c}'".format(a=contractInfo.lastTradeDateOrContractMonth,c=orderId))
    if hasattr(contractInfo,"localSymbol"):
        cur.execute("update ibtrades set local_symbol = '{a}' where order_id='{c}'".format(a=contractInfo.localSymbol,c=orderId))
    myConnection.commit()
    return

def updateTradeStatus(myConnection,statusInfo,orderId):    
    log.info("updateTradeStatus")
    cur = myConnection.cursor()
    # we have to assume there is already a ibtrade record from the previous step
    if hasattr(statusInfo,"status"):
        cur.execute("update ibtrades set status = '{a}' where order_id='{c}'".format(a=statusInfo.status,c=orderId))
    if hasattr(statusInfo,"filled"):
        cur.execute("update ibtrades set filled_qty = '{a}' where order_id='{c}'".format(a=statusInfo.filled,c=orderId))
    if hasattr(statusInfo,"avgFillPrice"):
        cur.execute("update ibtrades set avg_fill_price = '{a}' where order_id='{c}'".format(a=statusInfo.avgFillPrice,c=orderId))
    myConnection.commit()
    return
