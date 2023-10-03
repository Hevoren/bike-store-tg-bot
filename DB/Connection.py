import pymysql.cursors
import sqlite3
from DB.RequestsDatabase.DeleteRequests import DeleteRequests
from DB.RequestsDatabase.InsertRequests import InsertRequests
from DB.RequestsDatabase.GetRequests import GetRequests
from DB.RequestsDatabase.UpdateRequests import UpdateRequests


class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.insert_requests = None
        self.update_requests = None
        self.delete_requests = None
        self.get_requests = None

    def connect(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file, check_same_thread=False)
            print("Connected to the SQLite database")
            self.init_requests()
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def init_requests(self):
        self.insert_requests = InsertRequests(self.connection)
        self.update_requests = UpdateRequests(self.connection)
        self.delete_requests = DeleteRequests(self.connection)
        self.get_requests = GetRequests(self.connection)

    def create_tables(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER NOT NULL,
                    username TEXT DEFAULT NULL,
                    phone_number TEXT DEFAULT NULL,
                    geolocation TEXT DEFAULT NULL,
                    geolocation_coordinates TEXT DEFAULT NULL,
                    is_asking INTEGER NOT NULL DEFAULT 0,
                    step INTEGER DEFAULT 0,
                    editing_services INTEGER DEFAULT 0
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tg_id INTEGER NOT NULL,
                    services TEXT DEFAULT NULL,
                    username TEXT DEFAULT NULL,
                    phone_number TEXT DEFAULT NULL,
                    geolocation TEXT DEFAULT NULL,
                    geolocation_coordinates TEXT DEFAULT NULL,
                    geolocation_explain TEXT DEFAULT NULL,
                    description TEXT DEFAULT NULL,
                    state INTEGER NOT NULL DEFAULT 1,
                    rate INTEGER DEFAULT NULL,
                    message_id INTEGER DEFAULT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS execution_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER NOT NULL,
                    order_id INTEGER NOT NULL
                )
            ''')

            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
