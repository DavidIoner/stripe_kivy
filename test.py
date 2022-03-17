import components.payment as payment
from datetime import datetime

# sub = payment.create_christmas_price("cus_LIxj9R9mYLHLDm", "worker natalino", 30000, "usd")
# print(sub)

# src = payment.create_source("mail@mail.com", "4242424242424242", 12, 2025, "123", "usd")
# print(src.id)

# print(att)

# sub = payment.create_subscription("cus_LKisxqo9gj5z2Y", "price_1Ke4B6HPXOp77GbzVvp5IPCX", cancel=3)

payment.delete_subscription("sub_1Ke4B6HPXOp77GbzUluPyGa1")