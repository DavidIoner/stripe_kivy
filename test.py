import components.payment as payment
from datetime import datetime
import components.to_pdf as pdf
import stripe

# get the full path with os
import components.send_pdf as send_pdf

# d = "usd"
# print(d)
# print(d.upper)
c = ["a", "b", "c"]

for i in c:
    
    print(i)

charge = payment.create_charge("cus_LXqVTBt6FGmxTd", 99999, description={"man": "mamia", "mona": "lisa"})