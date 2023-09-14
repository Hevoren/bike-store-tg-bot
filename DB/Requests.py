class DatabaseRequests:
    def __init__(self, connection):
        self.connection = connection

    def add_user(self, username, phone_number, geolocation, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `users` (`username`, `phone_number`, `geolocation`, `tg_id`) VALUES ('{username}', '{phone_number}', '{geolocation}', {tg_id})"
            cursor.execute(sql)
        self.connection.commit()

    def get_user_geolocation(self, tg_id):
        with self.connection.cursor() as cursor:
            # Используйте параметризованный SQL запрос с LIMIT 1
            sql = "SELECT `geolocation` FROM `users` WHERE `tg_id` = %s LIMIT 1"
            cursor.execute(sql, (tg_id,))
            result = cursor.fetchone()  # Используйте fetchone(), чтобы получить одну строку
            if result != None:
                geolocation = result['geolocation']
                return geolocation

    # Получение tg_id для проверки пользовался ли пользователь ботом или нет
    def get_user_tg(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT `tg_id` FROM `users` WHERE `tg_id` = %s LIMIT 1"
            cursor.execute(sql, (tg_id,))
            result = cursor.fetchone()
        return result

    # Получение user_id для добавления заказа на пользователя
    def get_user_id(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT `user_id` FROM `users` WHERE `tg_id` = %s LIMIT 1"
            cursor.execute(sql, (tg_id,))
            result = cursor.fetchone()

        return result['user_id']

    def get_user_info(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `users` WHERE `tg_id` = %s LIMIT 1"
            cursor.execute(sql, (tg_id,))
            result = cursor.fetchone()
        return result

    # Добавление заказа в бд
    def add_order(self, tmp_services_str, tg_id, user_id, geolocation, geolocation_explain, description):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `orders` (`services`, `tg_id`, `user_id`, `geolocation`, `geolocation_explain`, `description`) VALUES ('{tmp_services_str}', '{tg_id}', '{user_id}', '{geolocation}', '{geolocation_explain}', '{description}')"
            cursor.execute(sql)
        self.connection.commit()

    # Получение последнего заказа для дальнейшей отправки в чат
    def get_last_order(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"SELECT * from `orders` WHERE `tg_id` = {tg_id} ORDER BY `order_id` DESC LIMIT 1"
            cursor.execute(sql)
            last_order = cursor.fetchone()
        self.connection.commit()
        return last_order

    # Обновление геолокации для облегчения следующей отрпавки геолокации
    def update_geolocation(self, tg_id, geolocation):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE users set geolocation = '{geolocation}' WHERE tg_id = '{tg_id}'"
            cursor.execute(sql)
        self.connection.commit()

    def update_order_state(self, order_id, order_state):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE orders set state = '{order_state}' WHERE `order_id` = {order_id}"
            cursor.execute(sql)
        self.connection.commit()

    def add_order_message_id(self, message_id, order_id):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE orders set message_id = '{message_id}' WHERE order_id = '{order_id}'"
            cursor.execute(sql)
        self.connection.commit()