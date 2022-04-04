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

log = logger.getLogger()

class App:
    def __init__(self, ib: IB):
        self.ib = ib
        self.root = tk.Tk()
        #new code
        #ibc = IBC(twsVersion=972, gateway=True, tradingMode='paper')
        #ib.connectedEvent += onConnected
        #watchdog = Watchdog(ibc, ib, port=4002)
        #watchdog.start()
        #end new code
        self.loop = asyncio.get_event_loop()

        self.root.title("ModelTrader Indicators")
        self.root.protocol('WM_DELETE_WINDOW', self._onDeleteWindow)
        self.root.minsize(width=250, height=100)
        self.label4 = Indicator(self.root, "Positions","",1)
        self.shares = Indicator(self.root, "Shares", "",1)
        self.qtrhour = Indicator(self.root, "Time of Check","",1)
        self.connected = Indicator(self.root, "Connected", "True",1)
        self.contract = Indicator(self.root, "Contract", "",1)
        self.label3 = Indicator(self.root, "15 Minutes ","",1)
        self.crossover = Indicator(self.root, "Crossover", "False",1)
        self.spread = Indicator(self.root, "CCI/CCIA Spread","",1)

        self.cci15 = Indicator(self.root, "CCI      ", "",1)        
        self.cci15_av = Indicator(self.root, "CCI Avg ", "",1)
        self.atr15 = Indicator(self.root, "ATR ", "",1)
        self.bband15_width = Indicator(self.root, "BBAND Width", "",1)
        self.bband15_b = Indicator(self.root, "BBAND %B ", "",1)
        self.label1 = Indicator(self.root, " ","",1)
        self.cci15p = Indicator(self.root, "CCI ", "",1)
        self.cci15p_av = Indicator(self.root, "CCIP Avg", "",1)
        
        self.label2 = Indicator(self.root, "1 Hour ","",1)
        self.cci1h = Indicator(self.root, "CCI ", "",2)
        self.cci1h_av = Indicator(self.root, "CCI Avg ","",2)
        self.atr1h = Indicator(self.root, "ATR ","",2)
        self.bband1h_width = Indicator(self.root, "BBand Width ","",2)
        self.bband1h_b = Indicator(self.root, "BBand %p ","",2)

        self.label1 = Indicator(self.root, "1 Day ","",1)
        self.cci1d = Indicator(self.root, "CCI ", "",3)
        self.cci1d_av = Indicator(self.root, "CCI Avg ","",3)
        self.atr1d = Indicator(self.root, "ATR ","",3)
        self.bband1d_width = Indicator(self.root, "BBand Width ","",3)
        self.bband1d_b = Indicator(self.root, "BBand %p ","",3)
        self.status1 = Indicator(self.root, "Status1 ","",0)
        
        self.ib.disconnectedEvent += self.disconnectEvent
        self.ib.connectedEvent += self.connectEvent
        self.ib.orderStatusEvent += self.orderStatusEvent
        self.ib.newOrderEvent += self.newOrderEvent
        self.ib.execDetailsEvent += self.execDetailsEvent
        self.ib.errorEvent += self.onError
        #self.ib.newOrderEvent += self.newOrderEvent
        #test again

    def run(self):
        self._onTimeout()
        # check for command line arguments
        
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
        logic.Algo(self.ib, self,backTest,commandParam).run()
        self.loop.run_forever()

    def _onTimeout(self):
        self.root.update()
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
  
    def orderStatusEvent(self, Trade):
        log.info("main.py:orderStatusEvent: we had with the following trade")
        orders.createTradesCSVFromEvent(self.ib, Trade, eventType = "Update")

    def newOrderEvent(self, Trade):
        log.info("main.py:newOrderEvent: we had with the following trade")
        orders.createTradesCSVFromEvent(self.ib, Trade, eventType = "New")

    def execDetailsEvent(self, Trade, Fill):
        log.info("main.py:execDetailsEvent: we had with the following trade")
        orders.createTradesCSVFromEvent(self.ib, Trade, eventType = "Update")

    def onError(self, reqId, errorCode, errorString, contract):
        #log.info("main.py:onError:: errorcode: {ec} errorstring: {es}".format(ec=errorCode,es=errorString))
        randomClientID = random.randint(1,250)
        log.info("random client ID: {CI}".format(CI=randomClientID))
        if errorCode == 200 or errorCode == 1100 or errorCode == 2100 or errorCode == 162 or errorCode == 2110:# or errorCode == 2107:
            try:
                log.info("main.py:Error 200, 1100, 2100, 162, 2110:onError:: errorcode going to disconnect")
                self.ib.disconnect()
                self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
                self.connected.update("DError 200, 1100, 2100, 162, 2110:isconnected")
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: finished disconnect going into sleep")
                self.ib.sleep(300)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110:: waking up")
                #self.ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID,timeout=0)
                self.ib.connect(config.HOST, config.PORT, clientId=randomClientID,timeout=0)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110:: attempted reconnect")
            except:
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110:: in except - try wasn't successful.  Going to sleep a bit")
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110:: errorcode going to disconnect")
                self.ib.disconnect()
                self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
                self.connected.update("Error 200, 1100, 2100, 162, 2110:Disconnected")
                self.ib.sleep(300)
                log.info("main.py:onError:: waking up")
                self.ib.connect(config.HOST, config.PORT, clientId=randomClientID,timeout=0)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: attempted reconnect")
            finally:
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: Finally exiting - but firs try to reconnect one more time")
                self.ib.disconnect()
                self.ib.waitOnUpdate(timeout=0.5)   #added to handle is client already in use https://github.com/erdewit/ib_insync/issues/76
                self.connected.update("Error 200, 1100, 2100, 162, 2110:Disconnected")
                self.ib.sleep(300)
                log.info("main.py:onError:Error 200, 1100, 2100, 162, 2110: waking up")
                self.ib.connect(config.HOST, config.PORT, clientId=randomClientID,timeout=0)
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
    log.info("random client ID: {CI}".format(CI=randomClientID))
    ib.connect(config.HOST, config.PORT, clientId=randomClientID,timeout=0)
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