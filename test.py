import components.payment as payment
import components.DButilC as dbutil


# customer_row = dbutil.get_row(1)
# print(customer_row)
# worker_row = dbutil.get_row(1, table="workers")

# source = payment.create_source(customer_row[5], "4242424242424242", 1, 2023, 314, "usd")
# print(source)

# customer = payment.create_customer(customer_row[1], customer_row[5], "src_1KY0z0HPXOp77GbzvT9W57rG", "usd")
# print(customer)

# charge = payment.create_charge("cus_LETyRtzhL2syUv", 200, "src_1KY0z0HPXOp77GbzvT9W57rG")
# print(charge)

# price = payment.create_worker_price("josias worker", 3000, "USD")
# print(price)

# subs = payment.create_subscription("cus_LETyRtzhL2syUv", "price_1KY1EHHPXOp77Gbz2TuhBA8F", "usd")
# print(subs)

# ret = payment.retrieve_customer("cus_LEgIDhOvkZt0fP")
# print(ret)

# desk = payment.create_desk_price(worker_row[2], worker_row[5], customer_row[10])
# print(desk)



def handle_monetary_data(money):
    money = str(money)

    if len(money) > 2:
        money = money[:-2] + "." + money[-2:]
    return money

x = 299899
y = handle_monetary_data(x)
print(y)
y = float(y) * 2
print(y)