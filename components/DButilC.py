import sqlite3

import pandas as pd

db = sqlite3.connect("components/contract.db")

cursor = db.cursor()
# cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

# cursor.execute("INSERT INTO customers (name) VALUES ('Juan')")
# insert into db where name = 'Juan'
# cursor.execute("UPDATE customers SET name='robertinho' WHERE id=1")
# name = cursor.execute("SELECT name FROM customers WHERE id=1")


def insert_data(item_dict, table="customers"):
    try:
        cursor.execute(
            f"INSERT INTO {table} (name, phone, email) VALUES ('{item_dict['name']}', '{item_dict['phone']}', '{item_dict['email']}')"
        )
        db.commit()
        print(f"{item_dict['name']} added to database")
    except sqlite3.OperationalError:
        print("Error: could not insert data")

def insert_data_customer(item_dict):
    try:
        cursor.execute(
            f"INSERT INTO customers (name, company, located_at, phone, email, local, onboard, security, apartment, currency) VALUES ('{item_dict['name']}','{item_dict['company']}','{item_dict['located_at']}', '{item_dict['phone']}', '{item_dict['email']}', '{item_dict['local']}', '{item_dict['onboard']}', '{item_dict['security']}', '{item_dict['apartment']}', '{item_dict['currency']}')"
        )
        db.commit()
        print(f"{item_dict['name']} added to database")
    except sqlite3.OperationalError:
        print("Error: could not insert data")


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


# verify if row exists on database by the "name" column
def verify_row(name, table="customers"):
    try:
        data = cursor.execute(f"SELECT name FROM {table} WHERE name='{name}'")
        return True
    except:
        print(f"{name}, creating new one")
        return False


# close database connection
def close_db():
    db.close()


# set all existing ids in order starting from 0
def set_ids(table="customers"):
    cursor.execute(f"UPDATE {table} SET id=rowid-1")
    db.commit()
