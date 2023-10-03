import time
from telebot import types
import telebot

from DB.Connection import DatabaseConnection
from DB.UserData import UserData
from DB.RequestsDatabase.DeleteRequests import DeleteRequests
from DB.RequestsDatabase.InsertRequests import InsertRequests
from DB.RequestsDatabase.GetRequests import GetRequests
from DB.RequestsDatabase.UpdateRequests import UpdateRequests

from Config.Config import Config

config = Config()

bot = telebot.TeleBot(config.bot_token)

admin_chat_id = config.admin_chat_id

db_connection = DatabaseConnection()
db_connection.connect("DB/bike_service.sqlite")
user_data = UserData()

insert_requests = InsertRequests(db_connection.connection)
update_requests = UpdateRequests(db_connection.connection)
delete_requests = DeleteRequests(db_connection.connection)
get_requests = GetRequests(db_connection.connection)
