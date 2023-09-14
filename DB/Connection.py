import pymysql.cursors
from DB.Requests import DatabaseRequests


class DatabaseConnection:
    def __init__(self, db_name, host, user_name, password):
        self.db_name = db_name
        self.host = host
        self.user_name = user_name
        self.password = password
        self.connection = None
        self.requests = None

    def connect(self):
        try:
            self.connection = pymysql.connect(host=self.host,
                                              user=self.user_name,
                                              password=self.password,
                                              cursorclass=pymysql.cursors.DictCursor)
            print(f"Подключено к серверу базы данных")
            self.connection.select_db(self.db_name)
            self.create_database()
            self.create_tables()
            self.requests = DatabaseRequests(self.connection)
        except pymysql.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")

    def create_database(self):
        with self.connection.cursor() as cursor:
            create_db_query = f"CREATE DATABASE IF NOT EXISTS {self.db_name}"
            cursor.execute(create_db_query)
            print(f"Создана база данных: {self.db_name}")

    def create_tables(self):
        with self.connection.cursor() as cursor:
            create_users_table_query = """
            CREATE TABLE IF NOT EXISTS `users` (
                `user_Id` INT AUTO_INCREMENT PRIMARY KEY,
                `username` VARCHAR(255),
                `phone_number` VARCHAR(255),
                `geolocation` VARCHAR(255),
                `tg_id` VARCHAR(255)
            )
            """
            cursor.execute(create_users_table_query)

            create_orders_table_query = """
            CREATE TABLE IF NOT EXISTS `orders` (
                `order_id` INT AUTO_INCREMENT PRIMARY KEY,
                `services` TEXT,
                `tg_id` INT,
                `user_id` INT,
                `geolocation` VARCHAR(255),
                `geolocation_explain` VARCHAR(255),
                `description` TEXT,
                FOREIGN KEY (`user_id`) REFERENCES `users`(`user_Id`)
            )
            """
            cursor.execute(create_orders_table_query)

            print("Созданы таблицы `users` и `orders`")

        self.connection.commit()
