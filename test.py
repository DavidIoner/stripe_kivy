import components.payment as payment
import components.DButilC as dbutil
# cus = payment.create_customer("jubileu das neves", "juj@gmail.com")

# create a card token for the customer


# cusr = payment.retrieve_customer("cus_LC7hgjJFJKwjMN")

# desk = payment.create_desk_price(cusr.name, 20000, "usd")

# subs = payment.create_subscription(cusr.id, desk.id, "usd")

# print(subs)
customer_row = dbutil.get_row(1)
print(customer_row)


customer = payment.create_customer(customer_row[1], customer_row[5])
src = payment.create_source(customer.id, "4242 4242 4242 4242", "12", "2023", "123")
desk = payment.create_desk_price("josias", 20000)
subs = payment.create_subscription(customer.id, desk.id)
print(customer)
print(subs)