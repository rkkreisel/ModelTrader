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
        self.cci = Indicator(self.root, "CCI", "")
        self.cci_category = Indicator(self.root, "CCI Category", "")
        self.cci_average = Indicator(self.root, "CCI Average", "")
        self.price = Indicator(self.root, "Last Price", "")
        self.time = Indicator(self.root, "Time", "")
        self.time_category = Indicator(self.root, "Time Category", "")

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

    def barUpdateEvent(self, bars: objects.BarDataList, hasNewBar: bool):
        cci, average = logic.calculate_cci(bars)
        self.cci.update(f"{cci:.2f}")
        self.cci_category.update(categories.categorize_cci(int(cci)))
        self.cci_average.update((f"{average:.2f}"))

    def tickUpdateEvent(self, ticker: Ticker):
        price = ticker.tickByTicks[0].price
        utctime = ticker.tickByTicks[0].time
        time = utctime.astimezone(pytz.timezone('US/Eastern'))
        self.price.update(f"${price}")
        self.time.update(time.strftime("%I:%M:%S %p"))
        self.time_category.update(categories.categorize_time(time))



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
