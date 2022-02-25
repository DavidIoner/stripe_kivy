import components.DButilC as dbutil

# items = dbutil.get_row("caca", "customer")
# print(items)
# row = dbutil.get_row(1, table="workers")
# print(row)
for i in range(1, dbutil.get_qtd(table="workers")+1):
    row = dbutil.get_row(i, table="workers")
    # print(row)
    if row[1] == "caca":
        print(row)
        print(i)