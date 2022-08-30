import asyncio
from sys import exit as sys_exit
import sys
from ib_insync import IB, util, objects, Ticker, Watchdog
from datetime import *
import tkinter as tk
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
        self.loop = asyncio.get_event_loop()
        self.root.title("ModelTrader Indicators")
        self.root.protocol('WM_DELETE_WINDOW', self._onDeleteWindow)
        #self.root.minsize(width=250, height=600)
        self.root.geometry("300x400")

        #self.frameMain = tk.LabelFrame(self.root, text="This is my FrameMain", width=950, height=550, padx=5, pady=5, bg='blue')
        #self.frameMain.grid_columnconfigure(0, weight=1)
        #self.frameMain.grid_columnconfigure(1, weight=1)
        #self.nameLabel = tk.Label(master=self.frameMain, text='hello hello hello hello hello hello hello ' + ":", anchor="w", padx=5)
        #self.frameMain.pack()
  
        #self.frameLeft = tk.LabelFrame(self.root, text="This is my FrameLeft", width=100, height=100, padx=5, pady=5, bg='blue')
        #self.frameLeft.grid(row=0, column=0)
        self.frame1 = tk.LabelFrame(self.root, text="This is my Frame1", padx=5, pady=5, bg='green')
        self.frame1.grid(row=0, column=0,sticky='nw')
        #self.frameLeft.pack()
        #self.frame1 = tk.LabelFrame(self.root, text="This is my Frame1", width=300, height=300, padx=5, pady=5, bg='blue')
        #self.frame1.grid(row=0, column=1)
        #self.frame1.pack(padx=10, pady=10)
        self.frame2 = tk.LabelFrame(self.root, text="This is my Frame2", padx=5, pady=5)
        self.frame2.grid(row=0, column=2,sticky='nw')
        self.frame3 = tk.LabelFrame(self.root, text="This is my Frame3", padx=5, pady=5)
        self.frame3.grid(row=0, column=1,sticky='nw')
        self.frameOrders = tk.LabelFrame(self.root, text="This is my FrameOrder", padx=5, pady=5)
        self.frameOrders.grid(row=1, column=2,sticky='nw')
        #self.frame2.pack(padx=10, pady=10, anchor="w")
        self.label4 = Indicator(self.frame1, "Positions","",0)
        self.shares = Indicator(self.frame1, "Shares", "",1)
        self.qtrhour = Indicator(self.frame1, "Time of Check","",1)
        self.connected = Indicator(self.frame1, "Connected", "True",1)
        self.contract = Indicator(self.frame1, "Contract", "",1)
        self.label3 = Indicator(self.frame1, "15 Minutes ","",1)
        self.crossover = Indicator(self.frame1, "Crossover", "False",1)
        self.spread = Indicator(self.frame1, "CCI/CCIA Spread","",1)

        self.cci15 = Indicator(self.frame1, "CCI      ", "",1)        
        self.cci15_av = Indicator(self.frame1, "CCI Avg ", "",1)
        self.atr15 = Indicator(self.frame1, "ATR ", "",1)
        #self.bband15_width = Indicator(self.frame1, "BBAND Width", "",1)
        #self.bband15_b = Indicator(self.frame1, "BBAND %B ", "",1)
        self.label1 = Indicator(self.frame1, " ","",1)
        self.cci15p = Indicator(self.frame1, "CCI ", "",1)
        self.cci15p_av = Indicator(self.frame1, "CCIP Avg", "",1)
        
        self.label2 = Indicator(self.frame1, "1 Hour ","",1)
        self.cci1h = Indicator(self.frame1, "CCI ", "",2)
        self.cci1h_av = Indicator(self.frame1, "CCI Avg ","",2)
        self.atr1h = Indicator(self.frame1, "ATR ","",2)
        #self.bband1h_width = Indicator(self.frame1, "BBand Width ","",2)
        #self.bband1h_b = Indicator(self.frame1, "BBand %p ","",2)

        self.label1 = Indicator(self.frame1, "1 Day ","",1)
        self.cci1d = Indicator(self.frame1, "CCI ", "",3)
        self.cci1d_av = Indicator(self.frame1, "CCI Avg ","",3)
        self.atr1d = Indicator(self.frame1, "ATR ","",3)
        #self.bband1d_width = Indicator(self.frame1, "BBand Width ","",3)
        #self.bband1d_b = Indicator(self.frame1, "BBand %p ","",3)
        self.status1 = Indicator(self.frame1, "Status1 ","",0)

        #self.profit = Indicator(self.frame1,"Profit ","",3)
        #self.orders = Indicator(self.frame1,"Orders ","",3)
        #self.windollars = Indicator(self.frame1,"Win $ ","",3)
        #self.lossdollars = Indicator(self.frame1,"Loss $ ","",3)
        #self.wincount = Indicator(self.frame1,"Win # ","",3)
        #self.losscount = Indicator(self.frame1,"Loss # ","",3)
        #self.ratio = Indicator(self.frame1,"Ratio ","",3)

        #logic conditions
        self.logicCrossed = Indicator(self.frame3,"Crossed ",False,3)
        self.logicOpenLong = Indicator(self.frame3,"OpenLong ",False,3)
        self.logicOpenShort = Indicator(self.frame3,"OpenShort ",False,3)
        self.logicPendingLong = Indicator(self.frame3,"Pending Long ",False,3)
        self.logicPendingShort = Indicator(self.frame3,"Pending Short ",False,3)
        self.logictradeNow = Indicator(self.frame3,"TradeNow? ",False,3)
        self.logicpendingCnt = Indicator(self.frame3,"Pending Count:  ",0,3)
        self.logicspread = Indicator(self.frame3,"15m Spread:  ",0,3)
        self.logic15over = Indicator(self.frame3,"15 cci over ccia ",False,3)
        self.logic1hover = Indicator(self.frame3,"1H cci over ccia ",False,3)
        self.logic1dover = Indicator(self.frame3,"1D cci over ccia ",False,3)
        self.logicopenOrders = Indicator(self.frame3,"Open Orders ",False,3)

        self.text1 = tk.Text(self.frame2, height=10, width=200)
        self.text1.pack()
        self.OrdersTradesText = tk.Text(self.frameOrders, height=10, width=200)
        self.OrdersTradesText.insert(tk.INSERT,"Orders/Trades")
        self.OrdersTradesText.pack()
        self.ib.disconnectedEvent += self.disconnectEvent
        self.ib.connectedEvent += self.connectEvent
        self.ib.orderStatusEvent += self.orderStatusEvent
        self.ib.newOrderEvent += self.newOrderEvent
        self.ib.execDetailsEvent += self.execDetailsEvent
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
                print("VALID number of arguments ",len(sys.argv))
                print("argument list",str(sys.argv))
                print("datetime", datetime.now())
                backTest = True
                commandParam = dt
                print(commandParam)
            else:
                backTest = False
        else:
            commandParam = ""
            backTest = False
        logic.Algo(self.ib, self,backTest,commandParam,self.myConnection).run()
        self.loop.run_forever()
    # detail on events - https://ib-insync.readthedocs.io/api.html#module-ib_insync.ib
    def _onTimeout(self):
        self.frame1.update()
        self.loop.call_later(0.03, self._onTimeout)

    def _onDeleteWindow(self):
        self.loop.stop()

    def connectEvent(self):
        self.connected.update("Connected")
        logger.getLogger().info("Connected.")

    def disconnectEvent(self):
        self.connected.update("Disconnected")
        logger.getLogger().info("Disconnected.")

    def profitandloss(self):
        pandl = self.objects.PnL()
        log.info("main.py:PNL {p}".format(p=pandl))

    def updateEvent(self):
        log.info("main.py:update Event occurred")

    def orderModifyEvent(self):
        log.info("main.py:an order has been modified")

    def orderOrderEvent(self):
        log.info("main.py:open order event - was this the stp")

    def orderOrderModifyEvent(self):
        log.info("\nmain.py:openOrderModifyEvent - was this the stp\n")

    def orderStatusEvent(self, Trade):
        log.info("main.py:orderStatusEvent: we had with the following trade")
        orders.createTradesCSVFromEvent(self.ib, Trade, "Update")
        log.info("back in main.py after orderStatusEvent")

    def newOrderEvent(self, Trade):
        log.info("\nmain.py:newOrderEvent: we had with the following trade\n")
        orders.addNewTrades(self.ib, Trade, self.myConnection)
        log.info("back in main.py after orderStatusEvent")

    def positionEvent(self):
        log.info("main.py:open order event - was this the stp")

    def accountValueEvent(self):
        log.info("main.py:account value event - was this the stp")

    def execDetailsEvent(self, Trade, Fill):
        log.info("main.py:execDetailsEvent: we had with the following trade")
        orders.createTradesCSVFromEvent(self.ib, Trade, "Update")

    def onError(self, reqId, errorCode, errorString, contract):
        #log.info("main.py:onError:: errorcode: {ec} errorstring: {es}".format(ec=errorCode,es=errorString))
        randomClientID = random.randint(1,250)
        log.info("random client ID: {CI}".format(CI=0))
        if errorCode == 200 or errorCode == 1100 or errorCode == 2100 or errorCode == 162 or errorCode == 2110:# or errorCode == 2107:
            try:
                log.info("main.py:Error 200, 1100, 2100, 162, 2110:onError:: errorcode going to disconnect")
                self.ib.disconnect()
                self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
                self.connected.update("DError 200, 1100, 2100, 162, 2110:isconnected")
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: finished disconnect going into sleep")
                self.ib.sleep(500)
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
                self.ib.sleep(500)
                log.info("main.py:onError:: waking up")
                self.ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: attempted reconnect")
            finally:
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: Finally exiting - but firs try to reconnect one more time")
                self.ib.disconnect()
                self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
                self.connected.update("Error 200, 1100, 2100, 162, 2110:Disconnected")
                self.ib.sleep(500)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: waking up")
                self.ib.connect(config.HOST, config.PORT, clientId=0,timeout=0)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: attempted reconnect")
            #global timeout_retry_flag
            #if timeout_retry_flag >= 5:
            #    log.info("onerror: Request timed out. Setting flag.")
            #    print("onerror: Request timed out. Setting flag.")
            #    set_timeout_flag(True, contract.conId)
            #    timeout_retry_flag = 0
            #else:
            #    timeout_retry_flag += 1
            #    print(f"onerror: Timeout try {timeout_retry_flag}")
            #    raise TimeoutError
        #else:
        #    log.info("main.py:onError:NOT > Error 200, 1100, 2100, 162, 2110: Finally exiting - but firs try to reconnect one more time")
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