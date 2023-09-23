class UpdateRequests:
    def __init__(self, connection):
        self.connection = connection

    # Обновелние статуса заказа в orders
    def update_order_state(self, order_id, state):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE orders set state = '{state}' WHERE `id` = {order_id}"
            cursor.execute(sql)
        self.connection.commit()

    # Обновление одного выбранного значения таблицы
    def update_one_prop(self, table, column, value, condition_column, value_condition):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE {table} SET {column} = %s WHERE {condition_column} = %s"
            cursor.execute(sql, (value, value_condition))
        self.connection.commit()

    # Обновление двух выбранных значений таблицы
    def update_two_prop(self, table, column, value, column2, value2, condition_column, value_condition):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE {table} SET {column} = %s, {column2} = %s WHERE {condition_column} = %s"
            cursor.execute(sql, {value, value2, value_condition})
        self.connection.commit()

    # Обновление трех выбранных занчений таблицы
    def update_three_prop(self, table, column, value, column2, value2, column3, value3, condition_column,
                          value_condition):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE {table} SET {column} = %s, {column2} = %s, {column3} = %s WHERE {condition_column} = %s"
            cursor.execute(sql, {value, value2, value3, value_condition})
        self.connection.commit()

    # Обновление id сообщения заказа
    def update_order_message_id(self, message_id, order_id):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE orders set message_id = '{message_id}' WHERE id = '{order_id}'"
            cursor.execute(sql)
        self.connection.commit()

    # Обновление статуса заказа в user_order
    def update_dealing_order(self, id, state_id):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE user_order set state_id = '{state_id}' WHERE id = '{id}'"
            cursor.execute(sql)
        self.connection.commit()