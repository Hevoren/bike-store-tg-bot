class InsertRequests:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, sql, values):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            self.connection.commit()
        finally:
            cursor.close()

    def add_user(self, username, tg_id):
        sql = "INSERT INTO `users` (`username`, `tg_id`) VALUES (?, ?)"
        values = (username, tg_id)
        self.execute_query(sql, values)

    def add_user_chating(self, user_id, username_order, order_id, tg_id):
        sql = "INSERT INTO `user_chating` (`user_id`, `username_order`, `order_id`, `tg_id`) VALUES (?, ?, ?, ?)"
        values = (user_id, username_order, order_id, tg_id)
        self.execute_query(sql, values)

    def add_order(self, tmp_services_str, tg_id, user_id, username, phone_number, geolocation, geolocation_coordinates,
                  geolocation_explain, description):
        sql = "INSERT INTO `orders` (`services`, `tg_id`, `user_id`, `username`, `phone_number`, `geolocation`, `geolocation_coordinates`, `geolocation_explain`, `description`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (tmp_services_str, tg_id, user_id, username, phone_number, geolocation, geolocation_coordinates, geolocation_explain, description)
        self.execute_query(sql, values)

    def add_dealing_order(self, tg_id, order_id):
        sql = "INSERT INTO `execution_orders` (`tg_id`, `order_id`) VALUES (?, ?)"
        values = (tg_id, order_id)
        self.execute_query(sql, values)

    def add_one_prop(self, table, column, value):
        sql = f"INSERT INTO `{table}` (`{column}`) VALUES (?)"
        values = (value,)
        self.execute_query(sql, values)

    def add_order_begin(self, user_id, tg_id, username):
        sql = "INSERT INTO `orders` (`user_id`, `tg_id`, `username`) VALUES (?, ?, ?)"
        values = (user_id, tg_id, username)
        self.execute_query(sql, values)
