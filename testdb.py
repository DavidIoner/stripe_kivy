import components.DButilC as dbutil

tudo = dbutil.get_all()

for customer in tudo:
    print(customer)
    print(customer[1])