import pymysql.cursors
from DB.RequestsDatabase.DeleteRequests import DeleteRequests
from DB.RequestsDatabase.InsertRequests import InsertRequests
from DB.RequestsDatabase.GetRequests import GetRequests
from DB.RequestsDatabase.UpdateRequests import UpdateRequests


class DatabaseConnection:
    def __init__(self, db_name, host, user_name, password):
        self.db_name = db_name
        self.host = host
        self.user_name = user_name
        self.password = password
        self.connection = None
        self.requests = None
        self.insert_requests = None
        self.update_requests = None
        self.delete_requests = None
        self.get_requests = None

    def connect(self):
        try:
            self.connection = pymysql.connect(host=self.host,
                                              user=self.user_name,
                                              password=self.password,
                                              cursorclass=pymysql.cursors.DictCursor)
            print(f"Подключено к серверу базы данных")
            self.connection.select_db(self.db_name)

            self.delete_requests = DeleteRequests(self.connection)
            self.insert_requests = InsertRequests(self.connection)
            self.update_requests = UpdateRequests(self.connection)
            self.get_requests = GetRequests(self.connection)
        except pymysql.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
