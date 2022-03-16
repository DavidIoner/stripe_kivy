import components.payment as payment
from datetime import datetime

# sub = payment.create_christmas_price("cus_LIxj9R9mYLHLDm", "worker natalino", 30000, "usd")
# print(sub)

src = payment.create_source("mail@mail.com", "4242424242424242", 12, 2025, "123", "usd")
print(src.id)

att = payment.attach_source("cus_LKjCT4nT4WWsN5", src.id, "usd")
print(att)