import time

from telebot import types
import telebot
from DB.Connection import DatabaseConnection
from Config.Config import Config
from DB.UserData import UserData
from Bot.HelpServices import HelpServices

from DB.RequestsDatabase.DeleteRequests import DeleteRequests
from DB.RequestsDatabase.InsertRequests import InsertRequests
from DB.RequestsDatabase.GetRequests import GetRequests
from DB.RequestsDatabase.UpdateRequests import UpdateRequests

config = Config()
help_services = HelpServices()

bot = telebot.TeleBot(config.bot_token)

admin_chat_id = config.admin_chat_id

db_connection = DatabaseConnection(config.db_name, config.host, config.user_name, config.password)
db_connection.connect()
user_data = UserData()

insert_requests = InsertRequests(db_connection.connection)
update_requests = UpdateRequests(db_connection.connection)
delete_requests = DeleteRequests(db_connection.connection)
get_requests = GetRequests(db_connection.connection)


# Начало
@bot.message_handler(commands=['start'])
def start(message):
    user = get_requests.get_prop("users", "*", "tg_id", message.chat.id)
    first_message_id = help_services.get_first_message(message.chat.id)
    if first_message_id:
        try:
            bot.delete_message(message.chat.id, first_message_id)
            help_services.delete_first_message_by_tg_id(message.chat.id)
        except Exception as e:
            print(f"Габелла: {e}")
            help_services.delete_first_message_by_tg_id(message.chat.id)
    elif user is None:
        insert_requests.add_user(message.from_user.username, message.chat.id)
    global user_data
    user_data = UserData()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Решите мою задачу', callback_data='solve_problem'))
    sent_message = bot.send_message(message.chat.id,
                     'Мы решим вашу проблему в дороге помоем ваш байк, заправим, а так же перегоним из любой точки в другую.',
                     reply_markup=keyboard)
    help_services.add_first_message(message.chat.id, sent_message.message_id)


# Отмена последнего заказа
@bot.message_handler(commands=['cancel_order'])
def cancel_order(message):
    keyboard = types.InlineKeyboardMarkup()
    order = get_requests.get_last_order(message.chat.id)
    if order is not None and order['state'] != 0:
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='cancel_order'))
        keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='cancel'))
        bot.send_message(message.chat.id, 'Вы уверены, что хотите отменить заказ?', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'У вас нет последних заказов')


# Вызов администратора
@bot.message_handler(commands=['help'])
def call_administrator(message):
    global user_data
    user_data = UserData()
    user = get_requests.get_prop("users", "*", "tg_id", message.chat.id)
    if user is None:
        insert_requests.add_user(message.from_user.username, message.chat.id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='help'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='cancel'))
    bot.send_message(message.chat.id, 'Вы уверены что хотите связаться с администратором?', reply_markup=keyboard)


# Отлавливание callback_data у кнопок, то есть указания что делают кнопки
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'solve_problem':
        help_services.delete_first_message_by_tg_id(callback.message.chat.id)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        update_requests.update_one_prop("users", "step", 0, "tg_id", callback.from_user.id)
        send_geolocation(callback.message)

    elif callback.data == 'cancel':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        start()

    elif callback.data == 'cancel_order':
        canceling_order(callback.message)

    elif callback.data == 'explain_geolocation':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        explain_geolocation(callback.message)

    elif callback.data == 'send_contact':
        send_contact(callback.message)

    elif callback.data in ['refuel', 'wash', 'serve', 'overtake', 'emergency']:
        service = callback.data
        if user_data.editing_services:
            if service in user_data.services:
                user_data.services.remove(service)
            else:
                user_data.services.append(service)
            updated_keyboard = generate_updated_keyboard()
            bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                          message_id=callback.message.message_id,
                                          reply_markup=updated_keyboard)

    elif callback.data == 'to_order':
        to_order(callback.message)

    elif callback.data == 'help':
        connection_with_the_operator(callback.message)

    elif callback.data == 'chat_with_client':
        print()

    elif callback.data in ['1', '2', '3', '4', '5']:
        order_message_id = help_services.getting_json(callback.message.message_id)
        rate = callback.data

        update_requests.update_one_prop("orders", "rate", rate, "message_id", order_message_id)

        user_id = callback.from_user.id
        user = get_requests.get_user_info(user_id)

        order = get_requests.get_prop("orders", "*", "message_id", order_message_id)

        user_data.services = help_services.translate_services(order)
        if 'geolocation' in order and order['geolocation']:
            location_text = f"Местоположение - {order['geolocation']}\n"
        else:
            location_text = ""
        chat_link = f"https://t.me/{callback.from_user.username}"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
        message_text = (
            f"⚡️️Заказ № {order['id']}⚡️ \n"
            f"Никнейм - @{order['username']} \n"
            f"Номер телефона - {order['phone_number']} \n"
            f"Проблема - {order['description']} \n"
            f"{location_text}"  # Включаем местоположение только если оно есть
            f"Уточнения - {order['geolocation_explain']} \n"
            f"Виды работ - {user_data.services} \n"
            f"Оценка работы - {rate}"
        )
        bot.edit_message_text(
            f"⚡️Заказ № {order['id']}⚡️ \nНикнейм - @{order['username']} \nНомер телефона - {order['phone_number']} \nПроблема - {order['description']}\nМестоположение - {order['geolocation']} \nУточнения - {order['geolocation_explain']} \nВиды работ - {user_data.services} \nОценка работы - {rate}",
            admin_chat_id, order_message_id,
            reply_markup=keyboard,
            parse_mode="html")
        bot.edit_message_text("Спасибо за отзыв!", callback.message.chat.id, callback.message.message_id)

    elif callback.data == 'deal':
        order = get_requests.get_prop("orders", "*", "message_id", callback.message.message_id)

        user_data.services = help_services.translate_services(order)
        help_services.state_machine(order, user_data.services, bot, admin_chat_id, callback, update_requests,
                                    insert_requests, get_requests)


# -----------------------------------------------------------------------------------------
def connection_with_the_operator(message):
    bot.edit_message_text(f"Объясните суть проблемы", message.chat.id, message.message_id)
    bot.register_next_step_handler(message, send_to_admin)


# -----------------------------------------------------------------------------------------
def canceling_order(message):
    order = get_requests.get_last_order(message.chat.id)
    if order['state'] in [1, 2, 3]:
        bot.delete_message(message.chat.id, message.message_id)
        update_requests.update_one_prop('orders', 'state', 0, 'id', order['id'])
        bot.send_message(admin_chat_id, f"Заказ №{order['id']} - <b>Отменен</b>", parse_mode="html")
        bot.send_message(message.chat.id, f"Заказ №{order['id']} - <b>Отменен</b>", parse_mode="html")
    elif order['state'] in [0, 4]:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, 'Невозможно отменить завершеный или отмененный заказ')


# -----------------------------------------------------------------------------------------

# Функция для отправки геолокации
def send_geolocation(message):
    user = get_requests.get_user_info(message.chat.id)
    if user['step'] == 0:
        if user['geolocation'] is not None:
            replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
            btn1 = types.KeyboardButton(f"{user['geolocation']}")
            btn2 = types.KeyboardButton('📍Отправить геолокацию', request_location=True)
            replyKeyboard.add(btn1, btn2)
            bot.send_message(message.chat.id,
                             '<b>Шаг 1 из 5.</b>\nПришлите геолокацию, если вы сейчас не в том месте, где ваш байк - тогда вставьте геолокацию в строку и пришлите.',
                             reply_markup=replyKeyboard, parse_mode="html")
            bot.register_next_step_handler(message, send_geolocation_listener)
        else:
            replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            replyKeyboard.add(types.KeyboardButton('📍Отправить геолокацию', request_location=True))
            bot.send_message(message.chat.id,
                             '<b>Шаг 1 из 5.</b>\nПришлите геолокацию, если вы сейчас не в том месте, где ваш байк - тогда вставьте геолокацию в строку и пришлите.',
                             reply_markup=replyKeyboard, parse_mode="html")
            bot.register_next_step_handler(message, send_geolocation_listener)
    else:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        replyKeyboard.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id,
                         'Вы нарушили порядок составления заявки, пожалуйста перезапустите процесс заявки - /start',
                         reply_markup=replyKeyboard)


# Прослушиватель, когда геоданные будет отправлены
@bot.message_handler(content_types=['location'])
def send_geolocation_listener(message):
    if message.location:
        user_data.lon = message.location.longitude
        user_data.lat = message.location.latitude
        update_requests.update_one_prop("users", "geolocation_coordinates", f"{user_data.lon}:{user_data.lat}", "tg_id",
                                        message.chat.id)  # Обновление геолокации пользователя

        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, '<b>Шаг 2 из 5.</b>\nУточните где найти вас и название отеля, этаж, комната.',
                         reply_markup=replyKeyboard, parse_mode="html")
        update_requests.update_one_prop("users", "step", 1, "tg_id", message.chat.id)
        explain_geolocation(message)

    elif message.text and '/' not in message.text:
        user_data.geolocation_text = message.text
        update_requests.update_one_prop("users", "geolocation", message.text, "tg_id",
                                        message.chat.id)  # Обновление геолокации пользователя

        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, '<b>Шаг 2 из 5.</b>\nУточните где найти вас и название отеля, этаж, комната.',
                         reply_markup=replyKeyboard, parse_mode="html")
        update_requests.update_one_prop("users", "step", 1, "tg_id", message.chat.id)
        explain_geolocation(message)

    elif message.text == '/start':
        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
        start(message)

    elif '/' in message.text and '/start' not in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отменить заказ', callback_data='cancel'))
        keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='solve_problem'))
        bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)


# Уточнение информации по поводу местонахождения
def explain_geolocation(message):
    user = get_requests.get_user_info(message.chat.id)
    if user['step'] == 1:
        bot.register_next_step_handler(message, explain_geolocation_listener)
    else:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        replyKeyboard.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id,
                         'Вы нарушили порядок составления заявки, пожалуйста перезапустите процесс заявки - /start',
                         reply_markup=replyKeyboard)


def explain_geolocation_listener(message):
    if message.text and '/' not in message.text:
        user_data.geolocation_explain = message.text
        bot.send_message(message.chat.id,
                         f"Ваше местоположение: {user_data.geolocation_text}, {user_data.geolocation_explain}" if user_data.geolocation_text else f"Ваше местоположение {user_data.lon}:{user_data.lat}, {user_data.geolocation_explain}")
        update_requests.update_one_prop("users", "step", 2, "tg_id", message.chat.id)
        send_contact(message)
    elif message.text == '/start':
        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
        start(message)
    elif '/' in message.text and '/start' not in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отменить заказ', callback_data='cancel'))
        keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='explain_geolocation'))
        bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)


# Отправка контакта
@bot.message_handler(content_types=['contact'])
def send_contact(message):
    user = get_requests.get_user_info(message.chat.id)
    if user['step'] == 2:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        replyKeyboard.add(types.KeyboardButton("Поделиться", request_contact=True))
        bot.send_message(message.chat.id,
                         '<b>Шаг 3 из 5.</b>\nПоделитесь контактом, что бы с вами быстро и легко можно с вами связаться',
                         reply_markup=replyKeyboard, parse_mode="html")
        bot.register_next_step_handler(message, send_contact_listener)
    else:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        replyKeyboard.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id,
                         'Вы нарушили порядок составления заявки, пожалуйста перезапустите процесс заявки - /start',
                         reply_markup=replyKeyboard)


# Прослушиватель отправленного контакта
def send_contact_listener(message):
    if message.contact:
        update_requests.update_one_prop("users", "phone_number", message.contact.phone_number, "tg_id",
                                        message.chat.id)  # Обновление номера

        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Далее...', reply_markup=replyKeyboard)
        bot.delete_message(message.chat.id, message.message_id + 1)
        update_requests.update_one_prop("users", "step", 3, "tg_id", message.chat.id)
        service_choose(message)

    elif message.text == '/start':
        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
        start(message)

    elif '/' in message.text and '/start' not in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отменить заказ', callback_data='cancel'))
        keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='send_contact'))
        bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)

    elif message.text and '/' not in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отменить заказ', callback_data='cancel'))
        keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='send_contact'))
        bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)


# Выбор услуги
def service_choose(message):
    user = get_requests.get_user_info(message.chat.id)
    if user['step'] == 3:
        user_data.editing_services = True
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Заправить', callback_data='refuel'))
        keyboard.add(types.InlineKeyboardButton('Помыть', callback_data='wash'))
        keyboard.add(types.InlineKeyboardButton('Обслужить', callback_data='serve'))
        keyboard.add(types.InlineKeyboardButton('Перегнать', callback_data='overtake'))
        keyboard.add(types.InlineKeyboardButton('Срочная помощь на дороге', callback_data='emergency'))
        keyboard.add(types.InlineKeyboardButton('Заказать ✉️', callback_data='to_order'))
        bot.send_message(message.chat.id, '<b>Шаг 4 из 5.</b>\nОтметьте, чем вам помочь:', reply_markup=keyboard,
                         parse_mode="html")
    else:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        replyKeyboard.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id,
                         'Вы нарушили порядок составления заявки, пожалуйста перезапустите процесс заявки - /start',
                         reply_markup=replyKeyboard)


# Обновление состояния кнопок при нажатии на них
def generate_updated_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f'Заправить{" ✅" if "refuel" in user_data.services else ""}',
                                            callback_data='refuel'))
    keyboard.add(
        types.InlineKeyboardButton(f'Помыть{" ✅" if "wash" in user_data.services else ""}',
                                   callback_data='wash'))
    keyboard.add(
        types.InlineKeyboardButton(f'Обслужить{" ✅" if "serve" in user_data.services else ""}',
                                   callback_data='serve'))
    keyboard.add(types.InlineKeyboardButton(f'Перегнать{" ✅" if "overtake" in user_data.services else ""}',
                                            callback_data='overtake'))
    keyboard.add(
        types.InlineKeyboardButton(
            f'Срочная помощь на дороге{" ✅" if "emergency" in user_data.services else ""}',
            callback_data='emergency'))
    keyboard.add(types.InlineKeyboardButton('Заказать ✉️', callback_data='to_order'))
    return keyboard


# Заказ
def to_order(message):
    user_data.editing_services = False
    bot.send_message(message.chat.id, '<b>Шаг 5 из 5.</b>\nОпишите проблему и ситуацию', parse_mode="html")
    update_requests.update_one_prop("users", "step", 4, "tg_id", message.chat.id)
    bot.register_next_step_handler(message, to_order_listener)


# Прослушиватель отправленной проблемы
def to_order_listener(message):
    user = get_requests.get_user_info(message.chat.id)
    if user['step'] == 4:
        if message.text and '/' not in message.text:
            tmp_services = ', '.join(map(str, user_data.services))
            user = get_requests.get_user_info(message.chat.id)
            insert_requests.add_order(tmp_services, message.chat.id, user['id'], user['username'],
                                      user['phone_number'], user_data.geolocation_text,
                                      f"{user_data.lon}:{user_data.lat}", user_data.geolocation_explain,
                                      message.text)
            bot.send_message(message.chat.id, "С вами свяжутся в течении 15 минут")
            send_to_chat(message)
        elif message.text == '/start':
            replyKeyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
            start(message)
        elif '/' in message.text and '/start' not in message.text:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Отменить заказ', callback_data='cancel'))
            keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='to_order'))
            bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)
    else:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        replyKeyboard.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id,
                         'Вы нарушили порядок составления заявки, пожалуйста перезапустите процесс заявки - /start',
                         reply_markup=replyKeyboard)


# -----------------------------------------------------------------------------------------


# Отправка заявки в чат Админов
def send_to_chat(message):
    user = get_requests.get_user_info(message.from_user.id)
    order = get_requests.get_last_order(user['tg_id'])
    if len(order['geolocation_coordinates']) == 19 and ':' in order['geolocation_coordinates']:
        parts = order['geolocation_coordinates'].split(':')
        if len(parts) == 2:
            user_data.lon = parts[0]
            user_data.lat = parts[1]
    else:
        user_data.geolocation_text = order['geolocation']

    user_data.geolocation_explain = order['geolocation_explain']

    user_data.services = help_services.translate_services(order)
    chat_link = f"https://t.me/{user['username']}"
    if user_data.lat and user_data.lon:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
        keyboard.add(types.InlineKeyboardButton(text="Договорился", callback_data='deal'))
        sent_message = bot.send_message(admin_chat_id,
                                        f"⚡️️Заказ № {order['id']}⚡️ \nНикнейм - @{order['username']} \nНомер телефона - {order['phone_number']} \nПроблема - {order['description']}\nУточнения - {order['geolocation_explain']} \nВиды работ - {user_data.services} \n",
                                        reply_markup=keyboard)
        bot.send_location(admin_chat_id, user_data.lat, user_data.lon)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
        keyboard.add(types.InlineKeyboardButton(text="Договорился", callback_data='deal'))
        sent_message = bot.send_message(admin_chat_id,
                                        f"⚡️️Заказ № {order['id']}⚡️ \nНикнейм - @{order['username']} \nНомер телефона - {order['phone_number']} \nПроблема - {order['description']}\nМестоположение - {order['geolocation']} \nУточнения - {order['geolocation_explain']} \nВиды работ - {user_data.services} \n",
                                        reply_markup=keyboard)

    update_requests.update_order_message_id(sent_message.message_id,
                                            get_requests.get_last_order(message.chat.id)['id'])


# -----------------------------------------------------------------------------------------

def send_to_admin(message):
    chat_link = f"https://t.me/{message.from_user.username}"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Написать", url=chat_link))
    bot.send_message(admin_chat_id, f"Поступила проблема от @{message.from_user.username}: {message.text}", reply_markup=keyboard)
    bot.send_message(message.chat.id, f"Ваше сообщение успешно отправлено, через некоторое вермя вам ответят")


# -----------------------------------------------------------------------------------------

def rate_work(tg_id, order_message_id):
    user = get_requests.get_user_info(tg_id)
    keyboard = types.InlineKeyboardMarkup(row_width=6)
    keyboard.add(types.InlineKeyboardButton(text="1", callback_data="1"),
                 types.InlineKeyboardButton(text="2", callback_data="2"),
                 types.InlineKeyboardButton(text="3", callback_data="3"))
    keyboard.add(types.InlineKeyboardButton(text="4", callback_data="4"),
                 types.InlineKeyboardButton(text="5", callback_data="5"))
    sent_rate_message = bot.send_message(tg_id, "Ваш заказ выполнен!\nОцените качество обслуживания",
                                         reply_markup=keyboard)
    rate_message_id = sent_rate_message.message_id
    help_services.adding_json(user['id'], tg_id, order_message_id, rate_message_id)


# -----------------------------------------------------------------------------------------

if __name__ == '__main__':
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
