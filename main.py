import asyncio
from sys import exit as sys_exit
from ib_insync import IB, util, objects, Ticker
from datetime import *
import tkinter as tk
import pytz

import categories
import config
import logger
import logic
from indicator import Indicator


class App:
    def __init__(self, ib: IB):
        self.ib = ib
        #self.root = tk.Tk()
        self.loop = asyncio.get_event_loop()

        #self.root.title("ModelTrader Indicators")
        #self.root.protocol('WM_DELETE_WINDOW', self._onDeleteWindow)
        #self.root.minsize(width=250, height=50)

        #self.qtrhour = Indicator(self.root, "Time of Check","",1)
        #self.connected = Indicator(self.root, "Connected", "True",1)
        #self.contract = Indicator(self.root, "Contract", "",1)
        #self.label3 = Indicator(self.root, "15 Minutes ","",1)
        #self.crossover = Indicator(self.root, "Crossover", "False",1)

        #self.cci15 = Indicator(self.root, "CCI      ", "",1)        
        #self.cci15_av = Indicator(self.root, "CCI Avg ", "",1)
        #self.atr15 = Indicator(self.root, "ATR ", "",1)
        #self.bband15_width = Indicator(self.root, "BBAND Width", "",1)
        #self.bband15_b = Indicator(self.root, "BBAND %B ", "",1)
        #self.label1 = Indicator(self.root, " ","",1)
        #self.cci15p = Indicator(self.root, "CCI ", "",1)
        #self.cci15p_av = Indicator(self.root, "CCIP Avg", "",1)
        
        #self.label2 = Indicator(self.root, "1 Hour ","",1)
        #self.cci1h = Indicator(self.root, "CCI ", "",2)
        #self.cci1h_av = Indicator(self.root, "CCI Avg ","",2)
        #self.atr1h = Indicator(self.root, "ATR ","",2)
        #self.bband1h_width = Indicator(self.root, "BBand Width ","",2)
        #self.bband1h_b = Indicator(self.root, "BBand %p ","",2)

        #self.label1 = Indicator(self.root, "1 Day ","",1)
        #self.cci1d = Indicator(self.root, "CCI ", "",3)
        #self.cci1d_av = Indicator(self.root, "CCI Avg ","",3)
        #self.atr1d = Indicator(self.root, "ATR ","",3)
        #self.bband1d_width = Indicator(self.root, "BBand Width ","",3)
        #self.bband1d_b = Indicator(self.root, "BBand %p ","",3)
        #self.status1 = Indicator(self.root, "Status1 ","",0)
        
        self.ib.disconnectedEvent += self.disconnectEvent
        self.ib.connectedEvent += self.connectEvent

    def run(self):
        self._onTimeout()
        logic.Algo(self.ib, self).run()
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
        pandl = elf.objects.PnL()
        logger.getLogger().info("PNL",pandl)

    
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
    try:
        logger.getLogger().info("Connecting...")
        ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID)
        ib.reqMarketDataType(config.DATATYPE.value)
    except OSError:
        logger.getLogger().error("Connection Failed.")
        sys_exit()

    app = App(ib)
    app.run()


if __name__ == '__main__':
    logger.setup()
    util.patchAsyncio()
    main(IB())
