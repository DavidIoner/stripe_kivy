import components.DButilC as dbutil

# tudo = dbutil.get_all()

# for customer, i in tudo:
#     print(customer)
#     print(customer[1])
#     print(i)

# dbutil.update_item("customer_id", "cus_id_0222", 1, "id", table="customers")
import components.to_pdf as pdf

rate = pdf.get_rate('MXN-USD')
amount = 23000 * int(pdf.monetary(rate, dot=False))



print(amount)
