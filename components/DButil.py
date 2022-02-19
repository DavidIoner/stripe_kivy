import sqlite3

db = sqlite3.connect("customer.db")

cursor = db.cursor()

# cursor.execute("INSERT INTO customers (name) VALUES ('Juan')")
# insert into db where name = 'Juan'
# cursor.execute("UPDATE customers SET name='robertinho' WHERE id=1")
# name = cursor.execute("SELECT name FROM customers WHERE id=1")

def insert_data(item_dict):
    try:
        cursor.execute(
            f"INSERT INTO customers (name, address, city, state, zipcode, phone, email, web) VALUES ('{item_dict['name']}', '{item_dict['address']}', '{item_dict['city']}', '{item_dict['state']}', '{item_dict['zipcode']}', '{item_dict['phone']}', '{item_dict['email']}', '{item_dict['web']}')"
        )
        db.commit()
        print(f"{item_dict['name']} added to database")
    except sqlite3.OperationalError:
        print("Error: could not insert data")


def get_item(item, where_id, where="name"):
    try:
        data = cursor.execute(
            f"SELECT {item} FROM customers WHERE {where}='{where_id}'"
        )
        fetch = data.fetchone()
        return fetch[0]
    except:
        print("Error: could not get item")


def update_item(item, item_value, where_id, where="name", view=True):
    try:
        cursor.execute(
            f"UPDATE customers SET {item}='{item_value}' WHERE {where}='{where_id}'"
        )
        db.commit()
        if view:
            print(f"{item} from {where_id} updated to {item_value}")
    except sqlite3.OperationalError:
        print("Error: could not update item")


def get_qtd():
    qtd = cursor.execute("SELECT COUNT(*) FROM customers")
    count = list(qtd.fetchone())[0]
    return count