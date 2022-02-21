from operator import itemgetter
from tkinter import Y

import components.DButilC as dbutil

item_dict = {
    "name": "joja",
    "phone": "55555555",
    "email": "mail@mail",
    "company": "",
}

# insert item dict into database
# dbutil.insert_data(item_dict)

# dbutil.update_item()
menu = [
    {
        "name": dbutil.get_item("name", i, "id"),
    }
    for i in range(0, dbutil.get_qtd())
]
# sorted_list = sorted(menu, key=itemgetter("name"))
# print(menu)
# print(sorted_list)
n = dbutil.get_item("name", 1, "id")

print(n)

# dbutil.set_ids()
# x = dbutil.get_row(0)
# print(x)

customer_row = dbutil.get_row(1, "id")
print(customer_row)
try:
    print(customer_row[1])
except:
    print("error")
