# remember to manually keep this file in sync with the modelbuilder file
import datetime

def categorize_cci_15(cci: int):
    if cci < -100:
        return "CCI15:U"
    if cci > 100:
        return "CCI15:O"
    if cci > 0:
        return "CCI15:IU"
    return "CCI15:IL"

def categorize_cci_15_avg(cci: int):
    if cci < -100:
        return "CCIA15:U"
    if cci > 100:
        return "CCIA15:O"
    if cci > 0:
        return "CCIA15:IU"
    return "CCIA15:IL"	
	
def categorize_cci_1h(cci: int):
    if cci < -100:
        return "CCIA1h:U"
    if cci > 100:
        return "CCIA1h:O"
    if cci > 0:
        return "CCIA1h:IU"
    return "CCIA1h:IL"

def categorize_cci_1d(cci: int):
    if cci < -100:
        return "CCIA1d:U"
    if cci > 100:
        return "CCIA1d:O"
    if cci > 0:
        return "CCIA1d:IU"
    return "CCIA1d:IL"		
	
def categorize_time(time: datetime.datetime):
    if time.hour < 9 or (time.hour == 9 and time.minute < 30):
        return "Night"
    if time.hour < 12:
        return "AM"
    if time.hour < 16:
        return "PM"
    return "Night"
    
def categorize_atr15(atr: float):
    if atr < 1:
        return "ATR15:L"
    if atr > 2.99:
        return "ATR15:H"
    return "ATR15:A"
	
def categorize_atr1h(atr: float):
    if atr < 2:
        return "ATR1:L"
    if atr > 5:
        return "ATR1:H"
    return "ATR1:A"
	
def categorize_atr1d(atr: float):
    if atr < 9:
        return "ATRD:L"
    if atr > 21:
        return "ATRD:H"
    return "ATRD:A"

	
def categorize_BBW15(bbw: float):
    if bbw <= 0.4:
        return "BBW15:L"
    if bbw > 0.54:
        return "BBW15:H"
    return "BBW15:A"
	
def categorize_BBW1h(bbw: float):
    if bbw <= 0.5:
        return "BBW1h:L"
    if bbw > 0.8:
        return "BBW1h:H"
    return "BBW1h:A"
	
def categorize_BBW1d(bbw: float):
    if bbw <= 2.6:
        return "BBW1d:L"
    if bbw > 5:
        return "BBW1d:H"
    return "BBW1d:A"	
	
def categorize_BBb15(bbb: float):
    if bbb < 0:
        return "BBb15:U"
    if bbb > 100:
        return "BBb15:O"
    if bbb < 50:
        return "BBb15:B"
    return "BBb15:T"
	
def categorize_BBb1h(bbb: float):
    if bbb < 0:
        return "BBb1h:U"
    if bbb > 100:
        return "BBb1h:O"
    if bbb < 50:
        return "BBb1h:B"
    return "BBb1h:T"
	
def categorize_BBb1d(bbb: float):
    if bbb < 0:
        return "BBb1d:U"
    if bbb > 100:
        return "BBb1d:O"
    if bbb < 50:
        return "BBb1d:B"
    return "BBb1d:T"	

def categorize_spread(spread: float):
    if abs(spread) > 78:
        return "Spread:O"
    if abs(spread) > 45:
        return "Spread:H"
    if abs(spread) > 26:
        return "Spread:A"
    if abs(spread) > 12:
        return "Spread:M"
    return "Spread:L"