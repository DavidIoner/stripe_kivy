import sqlite3


db = sqlite3.connect("components/contract.db")
cursor = db.cursor()


def insert_data_customer(item_dict):
    print(item_dict)
    try:
        cursor.execute(
            f"INSERT INTO customers (name, company, located_at, phone, email, licensor, local, christmas, currency) VALUES ('{item_dict['name']}','{item_dict['company']}','{item_dict['located_at']}', '{item_dict['phone']}', '{item_dict['email']}', '{item_dict['licensor']}', '{item_dict['local']}', '{item_dict['christmas']}', '{item_dict['currency']}')"
        )
        db.commit()
        print(f"{item_dict['name']} added to database")
    except sqlite3.OperationalError:
        print("Error: could not insert data")

def insert_data_worker(item_dict):
    try:
        cursor.execute(
            f"INSERT INTO workers (name, customer, wage, desk, onboard, apartment, holiday, currency_wage) VALUES ('{item_dict['name']}','{item_dict['customer']}','{item_dict['wage']}', '{item_dict['desk']}', '{item_dict['onboard']}', '{item_dict['apartment']}', '{item_dict['holiday']}', '{item_dict['currency_wage']}')"
        )
        db.commit()
        print(f"{item_dict['name']} added to database")
    except sqlite3.OperationalError:
        print("Error: could not insert data")

def get_all(table="customers"):
    cursor.execute(f"SELECT * FROM {table}")
    fetch = cursor.fetchall()
    db.commit()
    return fetch

def get_item(item, where_id, where="name", table="customers"):
    try:
        cursor.execute(f"SELECT {item} FROM {table} WHERE {where}='{where_id}'")
        fetch = cursor.fetchone()
        db.commit()
        return fetch[0]
    except:
        print("Error: could not get item")


# get the full row by name
def get_row(where_id, where="id", table="customers"):
    try:
        data = cursor.execute(f"SELECT * FROM {table} WHERE {where}={where_id}")
        fetch = data.fetchone()
        db.commit()
        return fetch
    except:
        print("Error: could not get item")


def update_item(item, item_value, where_id, where="id", view=True, table="customers"):
    try:
        cursor.execute(
            f"UPDATE {table} SET {item}='{item_value}' WHERE {where}='{where_id}'"
        )
        db.commit()
        if view:
            print(f"{item} from {where_id} updated to {item_value}")
    except sqlite3.OperationalError:
        print("Error: could not update item")


def update_item_dict(item_dict, where_id, where="name", table="customers"):
    try:
        cursor.execute(
            f"UPDATE {table} SET name='{item_dict['name']}', phone='{item_dict['phone']}', email='{item_dict['email']}' WHERE {where}='{where_id}'"
        )
        db.commit()
        print(f"{item_dict['name']} from {where_id} updated to {item_dict['name']}")
    except sqlite3.OperationalError:
        print("Error: could not update item")


def get_qtd(table="customers"):
    qtd = cursor.execute(f"SELECT COUNT(*) FROM {table}")
    db.commit()
    count = list(qtd.fetchone())[0]
    return int(count)


def get_last_id(table="customers"):
    cursor.execute(f"SELECT MAX(id) FROM {table}")
    fetch = cursor.fetchone()
    db.commit()
    return fetch[0]


# verify if row exists on database by the "name" column
def verify_row(name, customer=None, table="customers"):
    if customer == None:
        try:
            cursor.execute(f"SELECT name FROM {table} WHERE name='{name}'")
            return True
        except:
            print(f"{name}, creating new one")
            return False
    else:
        try:
            cursor.execute(f"SELECT name, customer FROM {table} WHERE name='{name}'")
            return True
        except:
            return False




def delete_row(id, table="customers"):
    cursor.execute(f"DELETE FROM {table} WHERE id={id}")
    db.commit()

def delete_all(table="customers"):
    if table == "all":
        cursor.execute("DELETE FROM customers")
        cursor.execute("DELETE FROM workers")
    else:
        cursor.execute(f"DELETE FROM {table}")
    db.commit()



# close database connection
def close_db():
    db.close()

