import asyncio
from cgitb import text
from sys import exit as sys_exit
import sys
from ib_insync import IB, util, objects, Ticker, Watchdog
from datetime import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pytz
from datetime import datetime, timedelta
import categories
import orders
import config
import logger
import logic
import random
from indicator import Indicator
import psycopg2

log = logger.getLogger()

class App:
    def __init__(self, ib: IB):
        self.ib = ib
        self.root = tk.Tk()
        self.style = ttk.Style()
        self.loop = asyncio.get_event_loop()
        self.root.title("ModelTrader Indicators")
        self.root.resizable(True, True)
        self.root.configure(background='#e1d8b9')
        #
        self.frame_app = tk.Frame(self.root)
        self.frame_app.grid(row=0, column=1, padx=5, pady=5, sticky='NW')
        self.appStart = Indicator(self.frame_app, "App Start ","",1)

        self.frame_fifteen = tk.Frame(self.root)
        self.frame_fifteen.grid(row = 0, column=2, padx=5, pady=5, sticky='NW')
        self.label15 = Indicator(self.frame_fifteen, "Fifteen","",1)
        self.cci15 = Indicator(self.frame_fifteen, "CCI      ", "",1)        
        self.cci15_av = Indicator(self.frame_fifteen, "CCI Avg ", "",1)
        self.atr15 = Indicator(self.frame_fifteen, "ATR ", "",1)
        self.cci15p_av = Indicator(self.frame_fifteen, "CCIP Avg", "",1)
        #
        self.frame_hour = tk.Frame(self.root)
        self.frame_hour.grid(row=0, column=3, padx=5, pady=5, sticky='NW')
        self.labelh = Indicator(self.frame_hour, "1 Hour ","",1)
        self.cci1h = Indicator(self.frame_hour, "CCI ", "",2)
        self.cci1h_av = Indicator(self.frame_hour, "CCI Avg ","",2)
        self.atr1h = Indicator(self.frame_hour, "ATR ","",2)
        #
        self.frame_day = tk.Frame(self.root)
        self.frame_day.grid(row=0, column=4, padx=5, pady=5, sticky='NW')
        self.labeld = Indicator(self.frame_day, "1 Day ","",1)
        self.cci1d = Indicator(self.frame_day, "CCI ", "",3)
        self.cci1d_av = Indicator(self.frame_day, "CCI Avg ","",3)
        self.atr1d = Indicator(self.frame_day, "ATR ","",3)

        self.frame_stats = tk.Frame(self.root)
        self.frame_stats.grid(row=0, column=0, padx =5, pady = 5, sticky='nw', rowspan=2)

        self.label4 = Indicator(self.frame_stats, "Positions","",0)
        self.shares = Indicator(self.frame_stats, "Shares", "",1)
        self.qtrhour = Indicator(self.frame_stats, "Time of Check","",1)
        self.connected = Indicator(self.frame_stats, "Connected", "True",1)
        self.contract = Indicator(self.frame_stats, "Contract", "",1)
        #self.label3 = Indicator(self.frame_stats, "15 Minutes ","",1)
        #self.crossover = Indicator(self.frame_stats, "Crossover", "False",1)
        #self.spread = Indicator(self.frame_stats, "CCI/CCIA Spread","",1)

        self.logicCrossed = Indicator(self.frame_stats,"Crossed ",False,3)
        self.logicOpenLong = Indicator(self.frame_stats,"OpenLong ",False,3)
        self.logicOpenShort = Indicator(self.frame_stats,"OpenShort ",False,3)
        self.logicPendingLong = Indicator(self.frame_stats,"Pending Long ",False,3)
        self.logicPendingShort = Indicator(self.frame_stats,"Pending Short ",False,3)
        self.logictradeNow = Indicator(self.frame_stats,"TradeNow? ",False,3)
        self.logicpendingCnt = Indicator(self.frame_stats,"Pending Count:  ",0,3)
        self.logicspread = Indicator(self.frame_stats,"15m Spread:  ",0,3)
        self.logic15over = Indicator(self.frame_stats,"15 cci over ccia ",False,3)
        self.logic1hover = Indicator(self.frame_stats,"1H cci over ccia ",False,3)
        self.logic1dover = Indicator(self.frame_stats,"1D cci over ccia ",False,3)
        self.logicopenOrders = Indicator(self.frame_stats,"Open Orders ",False,3)
        self.logicBarCount = Indicator(self.frame_stats,"Trading Bars ",False,3)

        self.frame_stats2 = tk.Frame(self.root)
        self.frame_stats2.grid(row=2, column=0, padx =5, pady = 5, sticky='nw', rowspan=1)
        self.label5 = Indicator(self.frame_stats2, "Stats 2","",0)
        self.buyStop = Indicator(self.frame_stats2, "Buy Stop", "",1)
        self.sellStop = Indicator(self.frame_stats2, "Sell Stop", "",1)
        self.trailStop = Indicator(self.frame_stats2, "Trail Stop", "",1)
        self.stopMode = Indicator(self.frame_stats2, "Stop Mode", "",1)


        self.frame_other = tk.Frame(self.root)
        self.frame_other.grid(row=1, column=1, padx =5, pady = 5, sticky='nw',columnspan=5)         
        self.status1 = Indicator(self.frame_other, "Status1 ","",0)
        self.text1 = tk.Text(self.frame_other)

#        self.text1.pack()
#        self.OrdersTradesText = tk.Text(self.frame_other, height=10, width=200)
        self.OrdersTradesText = tk.Text(self.root)
        self.OrdersTradesText.grid(row=2, column=1, padx =5, pady = 5, sticky='nw',columnspan=5)         
        self.OrdersTradesText.insert(tk.INSERT,"Orders/Trades")
        #
        self.ib.disconnectedEvent += self.disconnectedEvent
        self.ib.connectedEvent += self.connectEvent
        self.ib.updateEvent += self.updateEvent
        self.ib.orderStatusEvent += self.orderStatusEvent
        self.ib.newOrderEvent += self.newOrderEvent
        self.ib.orderModifyEvent += self.orderModifyEvent
        self.ib.openOrderEvent += self.openOrderEvent
        self.ib.positionEvent += self.positionEvent
        self.ib.accountValueEvent += self.accountValueEvent
        self.ib.accountSummaryEvent += self.accountSummaryEvent
        self.ib.pnlEvent += self.pnlEvent
        self.ib.pnlSingleEvent += self.pnlSingleEvent
        self.ib.execDetailsEvent += self.execDetailsEvent
        self.ib.cancelOrderEvent += self.cancelOrderEvent
        self.ib.updatePortfolioEvent += self.updatePortfolioEvent
        self.ib.commissionReportEvent += self.commissionReportEvent
        self.ib.errorEvent += self.onError
        self.myConnection = psycopg2.connect(host=config.hostname, user=config.username, password=config.password, dbname=config.database)
        #self.ib.newOrderEvent += self.newOrderEvent
        #test again and again again
        
    def run(self):
        self._onTimeout()
        # check for command line arguments
        # db connection
        #try:
        #    myConnection = psycopg2.connect(host=config.hostname, user=config.username, password=config.password, dbname=config.database)
            #doQuery( myConnection )
        #    cur = myConnection.cursor()
        #    print("connected to the DB")
        #    log.info("Successfully connected to the database")
        #except:
        #    print("Unable to connect to the database")

        #
        if len(sys.argv) > 1:
            dt = datetime(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),0,0) 
            if isinstance(dt,datetime):
                log.info("VALID number of arguments {i}".format(i=len(sys.argv)))
                log.info("argument list {l}".format(l=str(sys.argv)))
                log.info("datetime {d}".format(d=datetime.now()))
                backTest = True
                commandParam = dt
                log.info(commandParam)
            else:
                backTest = False
        else:
            commandParam = ""
            backTest = False
        logic.Algo(self.ib, self,backTest,commandParam,self.myConnection).run()
        self.loop.run_forever()
    # detail on events - https://ib-insync.readthedocs.io/api.html#module-ib_insync.ib  https://ib-insync.readthedocs.io/_modules/ib_insync/ib.html?highlight=execDetailsEvent#

    def _onTimeout(self):
        self.frame_other.update()
        self.loop.call_later(0.03, self._onTimeout)

    def _onDeleteWindow(self):
        self.loop.stop()

    def connectEvent(self): # Is emitted after connecting and synchronzing with TWS/gateway.
        self.connected.update("Connected")
        logger.getLogger().info("Connected.")

#    def disconnectEvent(self): # Is emitted after disconnecting from TWS/gateway.
#        self.connected.update("Disconnected")
#        logger.getLogger().info("Disconnected.")

    def disconnectedEvent(self): # Is emitted after disconnecting from TWS/gateway.
        self.connected.update("disconnectedEvent")
        logger.getLogger().info("disconnectedEvent")
        try:
            log.info("try on disconnectEvent")
            self.ib.disconnect()
            self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
            self.connected.update("DError 200, 1100, 2100, 162, 2110:isconnected")
            log.info("main.py:disconnectedEvent finished disconnect going into sleep")
            self.ib.sleep(50)
            log.info("main.py:disconnectedEvent:: waking up")
            #self.ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
            self.ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
            log.info("main.py:disconnectedEvent:: attempted reconnect")
        except:
            log.info("main.py:disconnectedEvent - try wasn't successful.  Going to sleep a bit")
            log.info("main.py:disconnectedEvent:: errorcode going to disconnect")
            self.ib.disconnect()
            self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
            self.connected.update("main.py:disconnectedEvent")
            self.ib.sleep(50)
            log.info("main.py:disconnectedEvent:: waking up")
            self.ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
            log.info("main.py:disconnectedEvent: attempted reconnect")
        finally:
            log.info("main.py:disconnectedEvent - but first try to reconnect one more time")
            self.ib.disconnect()
            self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
            self.connected.update("main.py:disconnectedEvent")
            self.ib.sleep(50)
            log.info("main.py:disconnectedEvent: waking up")
            self.ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
            log.info("main.py:disconnectedEvent: attempted reconnect")

#    def profitandloss(self):
#        pandl = self.objects.PnL()
#        log.info("main.py:PNL {p}".format(p=pandl))

    def updateEvent(self): # Is emitted after a network packet has been handeled.
        log.info("main.py:update Event occurred - network packet has been handeled")

    def orderModifyEvent(sel,Trade):
        #log.info("main.py:an order has been modified class: {c} trade:{t}".format(c=type(Trade),t=Trade))
        log.info("main.py:orderModifyEvent")

    def openOrderEvent(self,Trade):
        #log.info("main.py:openOrderEvent - was this the type {c} stp {t}".format(c=type(Trade),t=Trade))
        log.info("main.py:openOrderEvent")

    def orderStatusEvent(self, Trade): #Emits the changed order status of the ongoing trade.
        #log.info("main.py:orderStatusEvent: we had with the following trade type:{c} Trade: {t}".format(c=type(Trade),t=Trade))
        log.info("main.py:orderStatusEvent:")
#        orders.addNewOrders(self.ib, Trade, self.myConnection, self)
        orders.updateOrderWhenPlaced(self.ib, self.myConnection, "", Trade)
        log.info("back in main.py after orderStatusEvent")

    def newOrderEvent(self, Trade): # Emits a newly placed trade.
        log.info("main.py::newOrderEvent")
        # log.info("main.py:newOrderEvent: we had with the following trade type: {c} Trade: {t}".format(c=type(Trade),t=Trade))
#        orders.addNewOrders(self.ib, Trade, self.myConnection, self)
        orders.updateOrderWhenPlaced(self.ib, self.myConnection, "", Trade)
        log.info("back in main.py after newOrderEvent")

    def positionEvent(self, Position):
        log.info("main.py:positionEvent {p}".format(p=Position))

    def execDetailsEvent(self, Trade, Fill):    # emits the fill together with the ongoing trade it belongs to.
        #log.info("main.py:execDetailsEvent: we had with the following trade type trade: {c} type Fill: {f} fill: {fill} trade: {t}".format(c=type(Trade),f=type(Fill),fill=Fill,t=Trade))
        log.info("main.py:execDetailsEvent:")
        log.info("log.infoing the info from execDetailesEvent")
        log.info(Trade)
        log.info("Fill info")
        log.info(Fill)
 
#        orders.addNewOrders(self.ib, Trade, self.myConnection, self)
        orders.updateOrderWhenPlaced(self.ib, self.myConnection, "", Trade)
        orders.updateFills(self.ib, Fill, self.myConnection, self)

    def cancelOrderEvent(self, Trade): # Emits a trade directly after requesting for it to be cancelled.
        #log.info("main.py:cancelOrderEvent type Trade: {c} trade: {t}".format(c=type(Trade),t=Trade))
        log.info("main.py:cancelOrderEvent")

    def updatePortfolioEvent(self, PortfolioItem): #A portfolio item has changed.
        log.info("main.py:updatePortfolioEvent: {i}".format(i=PortfolioItem))

    def commissionReportEvent(self,Trade,Fill,CommissionReport): #The commission report is emitted after the fill that it belongs to
        log.info("main.py:commissionReportEvent: Commission Report: {cr}".format(cr=CommissionReport))
        log.info("main.py:commissionReportEvent Trade: {t}".format(t=Trade))
        log.info("main.py:commissionReportEvent Fill: {f}".format(f=Fill))

    def accountValueEvent(self,AccountValue): #An account value has changed.
        #log.info("main.py:accountValueEvent: {a}".format(a=AccountValue))
        log.info("main.py:accountValueEvent")

    def accountSummaryEvent(self,AccountValue):
        log.info("main.py:accountSummaryEvent: {a}".format(a=AccountValue))

    def pnlEvent(self,PnL): # A profit- and loss entry is updated.
        log.info("main.py:pnlEvent: {a}".format(a=PnL))

    def pnlSingleEvent(self,PnLSingle): #A profit- and loss entry for a single position is updated
        log.info("main.py:pnlSingleEvent: {a}".format(a=PnLSingle))

    def onError(self, reqId, errorCode, errorString, contract):
        log.info("main.py:onError:: reqId: {r} errorcode: {ec} errorstring: {es}".format(r=reqId,ec=errorCode,es=errorString))
        #randomClientID = random.randint(1,250)
        #log.info("random client ID: {CI}".format(CI=0))
        if errorCode == 200 or errorCode == 1100 or errorCode == 2100 or errorCode == 162 or errorCode == 2110:# or errorCode == 2107:
            try:
                log.info("main.py:Error 200, 1100, 2100, 162, 2110:onError:: errorcode going to disconnect")
                self.ib.disconnect()
                self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
                self.connected.update("DError 200, 1100, 2100, 162, 2110:isconnected")
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: finished disconnect going into sleep")
                self.ib.sleep(50)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110:: waking up")
                #self.ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
                self.ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110:: attempted reconnect")
            except:
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110:: in except - try wasn't successful.  Going to sleep a bit")
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110:: errorcode going to disconnect")
                self.ib.disconnect()
                self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
                self.connected.update("Error 200, 1100, 2100, 162, 2110:Disconnected")
                self.ib.sleep(50)
                log.info("main.py:onError:: waking up")
                self.ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: attempted reconnect")
            finally:
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: Finally exiting - but firs try to reconnect one more time")
                self.ib.disconnect()
                self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
                self.connected.update("Error 200, 1100, 2100, 162, 2110:Disconnected")
                self.ib.sleep(50)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: waking up")
                self.ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: attempted reconnect")
            #global timeout_retry_flag
            #if timeout_retry_flag >= 5:
            #    log.info("onerror: Request timed out. Setting flag.")
            #    log.info("onerror: Request timed out. Setting flag.")
            #    set_timeout_flag(True, contract.conId)
            #    timeout_retry_flag = 0
            #else:
            #    timeout_retry_flag += 1
            #    print(f"onerror: Timeout try {timeout_retry_flag}")
            #    raise TimeoutError
        
        #    self.ib.disconnect()
        #    self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
        #    self.connected.update("Error 200, 1100, 2100, 162, 2110:Disconnected")
        #    self.ib.sleep(300)
        #    log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: waking up")
        #    self.ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
        #    log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: attempted reconnect")
#       elif errorCode == 2105:
#            log.info("main.py:onError: 2105 not an error we want to restart - doing a quick sleep")
#            self.ib.disconnect()
#            self.connected.update("Error Code 2105:Disconnected")
#            log.info("main.py:onError:Error Code 2105: finished disconnect going into sleep")
#            self.ib.sleep(100)
#            log.info("main.py:onError:2105: waking up")
#            self.ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID)
#            log.info("main.py:onError:Error Code 2105: attempted reconnect")
#        elif errorCode == 2107:
#            print("main.py:Error Code 2105:on Error: not a bad error")

    #def barupdateEvent_15m(self, bars: objects.BarDataList, hasNewBar: bool):
        #logger.getLogger().info(f"Got 15m Bars.")
        #cci, avg = logic.calculate_cci(bars)
        #atr = logic.calculate_atr(bars)
        #bband_width, bband_b, = logic.calculate_bbands(bars)
        #qtrtime = datetime.now()
        #self.cci15.update(f"{cci:.02f}")
        #self.cci15_av.update(f"{avg:.02f}")
        #self.atr15.update(f"{atr:.02f}")
        #self.bband15_width.update(f"{bband_width:.04f}")
        #self.bband15_b.update(f"{bband_b:.04f}")
        #self.qtrhour.update(qtrtime)

def main(ib: IB):
    logger.getLogger().info("Connecting...")
    ib.disconnect()
    ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
    randomClientID = random.randint(1,250)
    log.info("random client ID: {CI}".format(CI=0))
    ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
    #ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
    ib.reqMarketDataType(config.DATATYPE.value)
#    try:
#        logger.getLogger().info("Connecting...")
#        ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
#        #ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
#        ib.reqMarketDataType(config.DATATYPE.value)
#    except NameError:    # got this block from https://groups.io/g/insync/message/4045
#            #self.num_disconnects += 1
#            print(datetime.datetime.now(), 'Connection error exception', self.num_disconnects)
#            #self.ib.cancelHistoricalData(bars)
#            log.info('Sleeping for 10sec...')
#            ib.disconnect
#            self.ib.sleep(10)
#            ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
#    except OSError:
#        log.info("main try except OS errror > Connection Failed.")
#        sys_exit()

    app = App(ib)
    app.run()
timeout_retry_flag = 0

            
if __name__ == '__main__':
    logger.setup()
    util.patchAsyncio()
    main(IB())