import datetime

def categorize_cci(cci: int):
    if cci < -200:
        return "Oversold Extended"
    if cci < -100:
        return "Oversold"
    if cci < 0:
        return "Lower"
    if cci < 100:
        return "Upper"
    if cci < 200:
        return "Overbought"
    return "Overbought Extended"


def categorize_time(time: datetime.datetime):
    if time.hour < 9 or (time.hour == 9 and time.minute < 30):
        return "Night"
    if time.hour < 12:
        return "AM"
    if time.hour < 16:
        return "PM"
    return "Night"
 
