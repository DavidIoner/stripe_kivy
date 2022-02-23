import components.payment as payment
import components.DButilC as dbutil
# cus = payment.create_customer("jubileu das neves", "juj@gmail.com")

# create a card token for the customer


# cusr = payment.retrieve_customer("cus_LC7hgjJFJKwjMN")

# desk = payment.create_desk_price(cusr.name, 20000, "usd")

# subs = payment.create_subscription(cusr.id, desk.id, "usd")

# print(subs)
customer_row = dbutil.get_row(2)
print(customer_row)

company = customer_row[2]
print(company)

ver = dbutil.verify_row(customer_row[1])
print(ver)