import components.DButilC as dbutil

# tudo = dbutil.get_all()

# for customer, i in tudo:
#     print(customer)
#     print(customer[1])
#     print(i)

dbutil.update_item("customer_id", "cus_id_0222", 1, "id", table="customers")