import time
from datetime import datetime, timedelta
startTime = datetime.now()
print("datetime.now and startTime",datetime.now(),"/n",startTime)
print("starttime ",startTime)
print("starttime total second",(datetime.now()-startTime).total_seconds())
while True:
    if (datetime.now()-startTime).total_seconds() > 100:
        print("Cancelling order failed for:  ")
        break
    else:
        print("sleeping",(datetime.now()-startTime).total_seconds())
        time.sleep(1)