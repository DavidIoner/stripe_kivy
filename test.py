import components.payment as payment

# cus = payment.create_customer("jubileu das neves", "juj@gmail.com")

# create a card token for the customer


cusr = payment.retrieve_customer("cus_LC7hgjJFJKwjMN")

desk = payment.create_desk_price(cusr.name, 20000, "usd")

subs = payment.create_subscription(cusr.id, desk.id, "usd")

print(subs)
