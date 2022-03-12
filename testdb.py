from datetime import timedelta
from datetime import time
from datetime import datetime
import components.payment as payment



# epoch 2 weeks ago
end_date = datetime.now() + timedelta(weeks=50)
end_date = str(end_date)[:10]
epoch = datetime(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:10]), 0, 0).timestamp()
epoch = int(epoch)
print(epoch)


# price = payment.create_desk_price("test", 100, "usd")
# print(price)
# print(price.id)



sub = payment.create_subscription("cus_LIqUYxo9YcPjAU", "price_1KcIXBHPXOp77GbzcFpVHwmN", 2)
print(sub)


