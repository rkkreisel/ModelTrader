from enum import Enum


class MarketDataTypes(Enum):
    LIVE = 1
    FROZEN = 2
    DELAYED = 3
    FROZEN_DELAYED = 4
