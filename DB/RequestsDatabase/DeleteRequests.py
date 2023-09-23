class DeleteRequests:
    def __init__(self, connection):
        self.connection = connection

    def delete_user_chating(self, tg_id):
        with self.connection.cursor() as cursor:
            sql = f"DELETE FROM user_chating WHERE tg_id = '{tg_id}'"
            cursor.execute(sql)
        self.connection.commit()