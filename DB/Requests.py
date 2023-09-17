class DatabaseRequests:
    def __init__(self, connection):
        self.connection = connection

    def add_user_begin(self, username, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `users` (`username`, `tg_id`) VALUES ('{username}', '{tg_id}')"
            cursor.execute(sql)
        self.connection.commit()

    def add_user(self, username, phone_number, geolocation, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `users` (`username`, `phone_number`, `geolocation`, `tg_id`) VALUES ('{username}', '{phone_number}', '{geolocation}', {tg_id})"
            cursor.execute(sql)
        self.connection.commit()

        # Добавление заказа в бд

    def add_order(self, tmp_services_str, tg_id, user_id, username, phone_number, geolocation, geolocation_coordinates, geolocation_explain,
                  description):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `orders` (`services`, `tg_id`, `user_id`, `username`, `phone_number`, `geolocation`, `geolocation_coordinates`, `geolocation_explain`, `description`) VALUES ('{tmp_services_str}', '{tg_id}', '{user_id}', '{username}', '{phone_number}', '{geolocation}', '{geolocation_coordinates}', '{geolocation_explain}', '{description}')"
            cursor.execute(sql)
        self.connection.commit()

    def add_dealing_order(self, tg_id, order_id, state_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `user_order` (`tg_id`, `order_id`, `state_id`) VALUES ('{tg_id}', '{order_id}', '{state_id}')"
            cursor.execute(sql)
        self.connection.commit()

    # ---------------------------------------------------------------------------
    # Получение tg_id для проверки пользовался ли пользователь ботом или нет
    def get_prop(self, table, select_column, condition_column, condition_value):
        with self.connection.cursor() as cursor:
            if select_column == '*':
                sql = f"SELECT * FROM `{table}` WHERE `{condition_column}` = %s LIMIT 1"
            else:
                sql = f"SELECT `{select_column}` FROM `{table}` WHERE `{condition_column}` = %s LIMIT 1"
            cursor.execute(sql, (condition_value,))
            result = cursor.fetchone()

        return result

    def get_user_info(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `users` WHERE `tg_id` = %s LIMIT 1"
            cursor.execute(sql, (tg_id,))
            result = cursor.fetchone()
        return result

    # Получение последнего заказа для дальнейшей отправки в чат
    def get_last_order(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"SELECT * from `orders` WHERE `tg_id` = {tg_id} ORDER BY `order_id` DESC LIMIT 1"
            cursor.execute(sql)
            last_order = cursor.fetchone()
        self.connection.commit()
        return last_order

    # def get_dealing(self, ):

    # ---------------------------------------------------------------------------

    def update_order_state(self, order_id, state_id):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE orders set state = '{state_id}' WHERE `order_id` = {order_id}"
            cursor.execute(sql)
        self.connection.commit()

    def update_one_prop(self, table, column, value, condition_column, value_condition):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE {table} SET {column} = %s WHERE {condition_column} = %s"
            cursor.execute(sql, (value, value_condition))
        self.connection.commit()

    def update_two_prop(self, table, column, value, column2, value2, condition_column, value_condition):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE {table} SET {column} = %s, {column2} = %s WHERE {condition_column} = %s"
            cursor.execute(sql, {value, value2, value_condition})
        self.connection.commit()

    # ---------------------------------------------------------------------------

    def update_order_message_id(self, message_id, order_id):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE orders set message_id = '{message_id}' WHERE order_id = '{order_id}'"
            cursor.execute(sql)
        self.connection.commit()

    # ---------------------------------------------------------------------------

    def update_dealing_order(self, user_order_id, state_id):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE user_order set state_id = '{state_id}' WHERE user_order_id = '{user_order_id}'"
            cursor.execute(sql)
        self.connection.commit()
