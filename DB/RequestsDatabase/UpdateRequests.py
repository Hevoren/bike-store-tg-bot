class UpdateRequests:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, sql, values):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            self.connection.commit()
        finally:
            cursor.close()

    def update_order_state(self, order_id, state):
        sql = "UPDATE orders SET state = ? WHERE id = ?"
        values = (state, order_id)
        self.execute_query(sql, values)

    def update_one_prop(self, table, column, value, condition_column, value_condition):
        sql = f"UPDATE {table} SET {column} = ? WHERE {condition_column} = ?"
        values = (value, value_condition)
        self.execute_query(sql, values)

    def update_two_prop(self, table, column, value, column2, value2, condition_column, value_condition):
        sql = f"UPDATE {table} SET {column} = ?, {column2} = ? WHERE {condition_column} = ?"
        values = (value, value2, value_condition)
        self.execute_query(sql, values)

    def update_three_prop(self, table, column, value, column2, value2, column3, value3, condition_column, value_condition):
        sql = f"UPDATE {table} SET {column} = ?, {column2} = ?, {column3} = ? WHERE {condition_column} = ?"
        values = (value, value2, value3, value_condition)
        self.execute_query(sql, values)

    def update_order_message_id(self, message_id, order_id):
        sql = "UPDATE orders SET message_id = ? WHERE id = ?"
        values = (message_id, order_id)
        self.execute_query(sql, values)

    def update_dealing_order(self, id, state_id):
        sql = "UPDATE user_order SET state_id = ? WHERE id = ?"
        values = (state_id, id)
        self.execute_query(sql, values)
