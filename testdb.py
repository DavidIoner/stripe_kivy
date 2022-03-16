from datetime import timedelta
from datetime import time
from datetime import datetime
from locale import currency
import components.payment as payment
import components.DButilC as dbutil

# end_date = datetime.now() + timedelta(days=1)
# end_date = str(end_date)[:10]
# epoch = datetime(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:10]), 0, 0).timestamp()
# epoch = int(epoch)
# print(end_date)
# print(epoch)

# calculate how many months until christmas
today = datetime.now()
christmas = datetime(today.year, 12, 3, 0, 0)
if today.month > 12:
    christmas = datetime(today.year + 1, 12, 3, 0, 0)
now = datetime.now()
months_until_christmas = (christmas - now).days / 30
months_until_christmas = int(months_until_christmas)
print(months_until_christmas)