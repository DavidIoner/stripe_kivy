from datetime import timedelta
from datetime import time
from datetime import datetime
import components.payment as payment
import components.DButilC as dbutil


dbutil.update_item("customer_id", "01 id loco", 1, where="id", view=True, table="customers")

