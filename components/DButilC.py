import sqlite3
from io import BufferedReader

import pandas as pd

db = sqlite3.connect("components/contract.db")

cursor = db.cursor()
# cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

# cursor.execute("INSERT INTO customers (name) VALUES ('Juan')")
# insert into db where name = 'Juan'
# cursor.execute("UPDATE customers SET name='robertinho' WHERE id=1")
# name = cursor.execute("SELECT name FROM customers WHERE id=1")


def insert_data(item_dict):
    try:
        cursor.execute(
            f"INSERT INTO customers (name, phone, email) VALUES ('{item_dict['name']}', '{item_dict['phone']}', '{item_dict['email']}')"
        )
        db.commit()
        print(f"{item_dict['name']} added to database")
    except sqlite3.OperationalError:
        print("Error: could not insert data")


def get_item(item, where_id, where="name"):
    try:
        cursor.execute(f"SELECT {item} FROM customers WHERE {where}='{where_id}'")
        fetch = cursor.fetchone()
        db.commit()
        return fetch[0]
    except:
        print("Error: could not get item")


# get the full row by name
def get_row(where_id, where="id"):
    try:
        data = cursor.execute(f"SELECT * FROM customers WHERE {where}={where_id}")
        fetch = data.fetchone()
        db.commit()
        return fetch
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


def update_item_dict(item_dict, where_id, where="name"):
    try:
        cursor.execute(
            f"UPDATE customers SET name='{item_dict['name']}', phone='{item_dict['phone']}', email='{item_dict['email']}' WHERE {where}='{where_id}'"
        )
        db.commit()
        print(f"{item_dict['name']} from {where_id} updated to {item_dict['name']}")
    except sqlite3.OperationalError:
        print("Error: could not update item")


def get_qtd():
    qtd = cursor.execute("SELECT COUNT(*) FROM customers")
    db.commit()
    count = list(qtd.fetchone())[0]
    return int(count)


# verify if row exists on database by the "name" column
def verify_row(name):
    try:
        data = cursor.execute(f"SELECT name FROM customers WHERE name='{name}'")
        return True
    except:
        print(f"{name}, creating new one")
        return False


# close database connection
def close_db():
    db.close()


# set all existing ids in order starting from 0
def set_ids():
    cursor.execute("UPDATE customers SET id=rowid-1")
    db.commit()
