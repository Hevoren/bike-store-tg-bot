class InsertRequests:
    def __init__(self, connection):
        self.connection = connection

    # Добавление пользователя в бд
    def add_user(self, username, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `users` (`username`, `tg_id`) VALUES ('{username}', '{tg_id}')"
            cursor.execute(sql)
        self.connection.commit()

    def add_user_chating(self, user_id, username_order, order_id, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `user_chating` (`user_id`, `username_order`, `order_id`, `tg_id`) VALUES ('{user_id}', '{username_order}', '{order_id}', '{tg_id}')"
            cursor.execute(sql)
        self.connection.commit()

    # Добавление заказа в бд
    def add_order(self, tmp_services_str, tg_id, user_id, username, phone_number, geolocation, geolocation_coordinates,
                  geolocation_explain,
                  description):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `orders` (`services`, `tg_id`, `user_id`, `username`, `phone_number`, `geolocation`, `geolocation_coordinates`, `geolocation_explain`, `description`) VALUES ('{tmp_services_str}', '{tg_id}', '{user_id}', '{username}', '{phone_number}', '{geolocation}', '{geolocation_coordinates}', '{geolocation_explain}', '{description}')"
            cursor.execute(sql)
        self.connection.commit()

    # Добавление выполяемого заказа в бд
    def add_dealing_order(self, tg_id, order_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `execution_orders` (`tg_id`, `order_id`) VALUES ('{tg_id}', '{order_id}')"
            cursor.execute(sql)
        self.connection.commit()

    def add_one_prop(self, table, column, value):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `{table}` (`{column}`) VALUES ('{value}')"
            cursor.execute(sql)
        self.connection.commit()

    def add_order_begin(self, user_id, tg_id, username):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `orders` (`user_id`, `tg_id`, `username`) VALUES ('{user_id}', '{tg_id}', '{username}')"
            cursor.execute(sql)
        self.connection.commit()