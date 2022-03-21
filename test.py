import components.payment as payment
from datetime import datetime
import components.to_pdf as pdf
import stripe

stripe.api_key = payment.get_api_key()
# customer = payment.create_customer("david", "davidhioner@gmail.com")
# print(customer)
cus = payment.retrieve_customer("cus_LMFhevQAhLshKq")
print(cus.default_source)

if cus.default_source is None:
    # sub = payment.create_subscription(cus.id, "cus_LMFhevQAhLshKq")
    print("no default source")

# charge = payment.create_charge(cus.id, 2000, "usd", "test charge")
# print(charge)


inv = stripe.Invoice.create(
  customer="cus_LKjCT4nT4WWsN5",
  collection_method="send_invoice",
  days_until_due=30,
)

print(inv)