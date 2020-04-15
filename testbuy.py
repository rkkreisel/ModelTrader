
from ib_insync.order import Order
import config
import constants
import logger
import csv
import os
import pandas as pd
from datetime import datetime, timedelta
from ib_insync import *
#util.startLoop()

ib = IB()
ib.connect('127.0.0.1',55555,clientId=6)
contContract = ib.reqContractDetails(
        ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE))
print("contContract ",contContract)
print("")
tradeContract = Contract(exchange=config.EXCHANGE, secType="FUT", localSymbol="ESM0")
#tradeContract = ib.qualifyContracts(contContract)[0]   # gives all the details of a contract so we can trade it
#contract = ib.reqContractDetails(ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE))
#order = LimitOrder('SELL',2,2800)

limitOrder = Order(
        action = "SELL",
        orderType = "LMT",
        auxPrice = 0,
        lmtPrice = 2800,
        faProfile = "cci_day",
        totalQuantity = 1,
        tif = "GTC",
        transmit = True
    )

print("tradeContract ",tradeContract)
print("")
print("order ",limitOrder)
print("")
trade = ib.placeOrder(tradeContract,limitOrder)
ib.sleep(1)
print("trade log ",trade.log)