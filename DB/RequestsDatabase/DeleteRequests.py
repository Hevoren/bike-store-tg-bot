class DeleteRequests:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, sql, values):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            self.connection.commit()
        finally:
            cursor.close()

    def delete_user_chating(self, tg_id):
        sql = "DELETE FROM user_chating WHERE tg_id = ?"
        values = (tg_id,)
        self.execute_query(sql, values)
