class GetRequests:
    def __init__(self, connection):
        self.connection = connection

    # Получение выбранного одного значение по выбранному столбцу
    def get_prop(self, table, select_column, condition_column, condition_value):
        with self.connection.cursor() as cursor:
            if select_column == '*':
                sql = f"SELECT * FROM `{table}` WHERE `{condition_column}` = %s LIMIT 1"
            else:
                sql = f"SELECT `{select_column}` FROM `{table}` WHERE `{condition_column}` = %s LIMIT 1"
            cursor.execute(sql, (condition_value,))
            result = cursor.fetchone()

        return result

    # Получение информации о пользователе по tg_id
    def get_user_info(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `users` WHERE `tg_id` = %s LIMIT 1"
            cursor.execute(sql, (tg_id,))
            result = cursor.fetchone()
        return result

    # Получение последнего заказа для дальнейшей отправки в чат
    def get_last_order(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"SELECT * from `orders` WHERE `tg_id` = {tg_id} ORDER BY `id` DESC LIMIT 1"
            cursor.execute(sql)
            last_order = cursor.fetchone()
        self.connection.commit()
        return last_order