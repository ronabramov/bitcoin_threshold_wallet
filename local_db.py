import os
import sqlite3
import common_utils

DB_FILE = "local_db.sqlite"
if not os.path.exists(DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY,hashed_password TEXT,homeserver_url TEXT,homeserver_login TEXT,homeserver_password TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS wallets (wallet_id TEXT PRIMARY KEY,threshold INTEGER,users TEXT,metadata TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (transaction_id TEXT PRIMARY KEY,wallet_id TEXT,details TEXT,approvers TEXT)""")
        conn.commit()

        

def save_user_data(email: str, password: str, homeserver):
    hashed_password = common_utils.hash_password(password)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users (email, hashed_password, homeserver_url, homeserver_login, homeserver_password)
                VALUES (?, ?, ?, ?, ?)
                """,
                (email, hashed_password, homeserver['url'], homeserver['login'], homeserver['password'])
            )
            conn.commit()
            print("User details locally saved successfully.")
        except sqlite3.IntegrityError:
            print("Error: User with this email already exists.")

def retrieve_users(): #Testing users retival.
    """Retrieve and display all users from the local database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user in users:
            print("Email:", user[0])
            print("Hashed Password:", user[1])
            print("Homeserver URL:", user[2])
            print("Homeserver Login:", user[3])
            print("Homeserver Password:", user[4])
            print("---------------------")
