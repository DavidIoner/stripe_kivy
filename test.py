import components.payment as payment
from datetime import datetime
import components.to_pdf as pdf
import stripe

stripe.api_key = payment.get_api_key()
cus = payment.retrieve_customer("cus_LMFhevQAhLshKq")
print(cus)

source = payment.create_source(cus.email, "4242424242424242", "12", "2025", "123")
print(source)
print(source.id)
payment.attach_source("cus_LMFhevQAhLshKq", source.id)
print(cus.default_source)


if cus.default_source is not None:
  src = stripe.Source.retrieve(cus.default_source)
  print(src)
else:
  print("no default source")