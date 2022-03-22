from datetime import timedelta
from datetime import time
from datetime import datetime
from locale import currency
from resource import prlimit
import components.payment as payment
import components.DButilC as dbutil

# dbutil.delete_all("all")
dbutil.reset_sequence("customers")

