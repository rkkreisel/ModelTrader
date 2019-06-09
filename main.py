import asyncio
from sys import exit as sys_exit
from ib_insync import IB, util, objects, Ticker
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
        self.root = tk.Tk()
        self.loop = asyncio.get_event_loop()

        self.root.title("ModelTrader Indicators")
        self.root.protocol('WM_DELETE_WINDOW', self._onDeleteWindow)
        self.root.minsize(width=250, height=50)

        self.connected = Indicator(self.root, "Connected", "True")
        self.contract = Indicator(self.root, "Contract", "")
        self.cci15 = Indicator(self.root, "CCI (15m)", "")        
        self.cci15_av = Indicator(self.root, "CCI Avg (15m)", "")
        self.atr15 = Indicator(self.root, "ATR (15m)", "")
        self.bband15_width = Indicator(self.root, "BBAND Width (15m)", "")
        self.bband15_b = Indicator(self.root, "BBAND %B (15m)", "")


        self.ib.connectedEvent += self.connectEvent
        self.ib.disconnectedEvent += self.disconnectEvent

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

    def barupdateEvent_15m(self, bars: objects.BarDataList, hasNewBar: bool):
        logger.getLogger().info(f"Got 15m Bars.")
        cci, avg = logic.calculate_cci(bars)
        atr = logic.calculate_atr(bars)
        bband_width, bband_b, = logic.calculate_bbands(bars)
        self.cci15.update(f"{cci:.02f}")
        self.cci15_av.update(f"{avg:.02f}")
        self.atr15.update(f"{atr:.02f}")
        self.bband15_width.update(f"{bband_width:.04f}")
        self.bband15_b.update(f"{bband_b:.04f}")

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
