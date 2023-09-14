# state == 1 активен
# state == 2 отменен
# state == 3 выполняется
# state == 4 выполнен
from datetime import datetime, timedelta

import telebot
from telebot import types

from DB.Connection import DatabaseConnection
from Config.Config import Config
from DB.UserData import UserData
from DB.Requests import DatabaseRequests

config = Config()

bot = telebot.TeleBot(config.bot_token)
admin_chat_id = config.admin_chat_id

db_connection = DatabaseConnection(config.db_name, config.host, config.user_name, config.password)
db_connection.connect()

db_requests = DatabaseRequests(db_connection.connection)


# Начало
@bot.message_handler(commands=['start'])
def main(message):
    print(datetime.now())
    global user_data
    user_data = UserData()
    user_data.state = 0
    user_data.tg_id = message.from_user.id
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Решите мою задачу', callback_data='solve_problem'))
    bot.send_message(message.chat.id,
                     'Мы решим вашу проблему в дороге помоем ваш байк, заправим, а так же перегоним из любой точки в другую.',
                     reply_markup=keyboard)


@bot.message_handler(commands=['cancel_order'])
def cancel_order(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='cancel_order'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='cancel_canceling_order'))
    bot.send_message(message.chat.id, 'Вы уверены, что хотите отменить заказ?', reply_markup=keyboard)


# Отлавливание callback_data у кнопок, то есть указания что делают кнопки
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'solve_problem':
        send_geolocation(callback.message)

    elif callback.data == 'cancel':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        main(callback.message)

    elif callback.data == 'explain_geolocation':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        explain_geolocation(callback.message)

    elif callback.data == 'send_contact':
        send_contact(callback.message)

    elif callback.data in ['refuel', 'wash', 'serve', 'overtake', 'emergency']:
        service = callback.data
        if user_data.editing_services == True:
            if service in user_data.services:
                user_data.services.remove(service)
            else:
                user_data.services.append(service)
            updated_keyboard = generate_updated_keyboard()
            bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                          reply_markup=updated_keyboard)
    elif callback.data == 'to_order':
        to_order(callback.message)
    elif callback.data == 'cancel_order':
        canceling_order(callback.message)
    elif callback.data == 'cancel_canceling_order':
        canceling_canceling_order(callback.message)


def canceling_order(message):
    order = db_requests.get_last_order(user_data.tg_id)
    if order['state'] != 4 or 2:
        time_order = db_requests.get_last_order(user_data.tg_id)['created_at']
        time_order = datetime.strptime(time_order, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        time_difference = current_time - time_order
        if time_difference <= timedelta(minutes=15):
            db_requests.update_order_state(order['order_id'], 2)
            db_requests.get_last_order(user_data.tg_id)
            bot.send_message(admin_chat_id, f"Заказ №{order['order_id']} - *Отменен*")
        else:
            bot.send_message(admin_chat_id, f"Заказ №{order['order_id']} - *Отменен*")
    else:
        bot.send_message(admin_chat_id, 'Невозможно отменить завершеный или отмененный заказ')
        bot.send_message(message.chat.id, 'Невозможно отменить завершеный или отмененный заказ')



def canceling_canceling_order(message):
    bot.delete_message(message.chat.id, message.message_id)


# ----
# Функция для отправки геолокации
@bot.message_handler(content_types=['location'])
def send_geolocation(message):
    if user_data.state == 0:
        geolocation = db_requests.get_user_geolocation(user_data.tg_id)
        if geolocation is not None:
            replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(f"{geolocation}")
            btn2 = types.KeyboardButton('Поделиться геоданными', request_location=True)
            replyKeyboard.add(btn1, btn2)
            bot.send_message(message.chat.id,
                             'Пришлите геолокацию, если вы сейчас не в том месте, где ваш байк - тогда вставьте геолокацию в строку и пришлите.',
                             reply_markup=replyKeyboard)
            bot.register_next_step_handler(message, send_geolocation_listener)
        else:
            replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            replyKeyboard.add(types.KeyboardButton('Поделиться геоданными', request_location=True))
            bot.send_message(message.chat.id,
                             'Пришлите геолокацию, если вы сейчас не в том месте, где ваш байк - тогда вставьте геолокацию в строку и пришлите.',
                             reply_markup=replyKeyboard)
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
        replyKeyboard = types.ReplyKeyboardRemove()
        user_data.lon = message.location.longitude
        user_data.lat = message.location.latitude
        geolocation = f"{user_data.lon}:{user_data.lat}"
        db_requests.update_geolocation(user_data.tg_id, geolocation)
        bot.send_message(message.chat.id, 'Уточните где найти вас и название отеля, этаж, комната.',
                         reply_markup=replyKeyboard)
        user_data.state = 1
        explain_geolocation(message)
    elif message.text and '/' not in message.text:
        user_data.geolocation_text = message.text
        db_requests.update_geolocation(user_data.tg_id, user_data.geolocation_text)
        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Уточните где найти вас и название отеля, этаж, комната.',
                         reply_markup=replyKeyboard)
        user_data.state = 1
        explain_geolocation(message)
    elif message.text == '/start':
        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
        main(message)
    elif '/' in message.text and '/start' not in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
        keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='solve_problem'))
        bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)


# Уточнение информации по поводу местонахождения
def explain_geolocation(message):
    if user_data.state == 1:
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
        user_data.state = 2
        send_contact(message)
    elif message.text == '/start':
        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
        main(message)
    elif '/' in message.text and '/start' not in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
        keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='explain_geolocation'))
        bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)


# ----


# Отправка контакта
@bot.message_handler(content_types=['contact'])
def send_contact(message):
    if user_data.state == 2:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        replyKeyboard.add(types.KeyboardButton("Поделиться", request_contact=True))
        bot.send_message(message.chat.id, 'Поделитесь контактом, что бы с вами быстро и легко можно с вами связаться',
                         reply_markup=replyKeyboard)
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
        user_data.phone_number = message.contact.phone_number
        string = f"{message.contact.first_name}, {message.contact.last_name}"
        user_data.fi = string
        user_data.user_id = message.contact.user_id
        replyKeyboard = types.ReplyKeyboardRemove()

        bot.send_message(message.chat.id, 'Далее...', reply_markup=replyKeyboard)
        bot.delete_message(message.chat.id, message.message_id + 1)

        user_data.state = 3

        service_choose(message)
    elif message.text == '/start':
        replyKeyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
        main(message)
    elif '/' in message.text and '/start' not in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
        keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='explain_geolocation'))
        bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)
    elif message.text and '/' not in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
        keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='send_contact'))
        bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)


# Выбор услуги
def service_choose(message):
    if user_data.state == 3:
        user_data.editing_services = True
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Заправить', callback_data='refuel'))
        keyboard.add(types.InlineKeyboardButton('Помыть', callback_data='wash'))
        keyboard.add(types.InlineKeyboardButton('Обслужить', callback_data='serve'))
        keyboard.add(types.InlineKeyboardButton('Перегнать', callback_data='overtake'))
        keyboard.add(types.InlineKeyboardButton('Срочная помощь на дороге', callback_data='emergency'))
        keyboard.add(types.InlineKeyboardButton('Заказать ✉️', callback_data='to_order'))
        bot.send_message(message.chat.id, 'Отметьте, чем вам помочь:', reply_markup=keyboard)
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
        types.InlineKeyboardButton(f'Помыть{" ✅" if "wash" in user_data.services else ""}', callback_data='wash'))
    keyboard.add(
        types.InlineKeyboardButton(f'Обслужить{" ✅" if "serve" in user_data.services else ""}', callback_data='serve'))
    keyboard.add(types.InlineKeyboardButton(f'Перегнать{" ✅" if "overtake" in user_data.services else ""}',
                                            callback_data='overtake'))
    keyboard.add(
        types.InlineKeyboardButton(f'Срочная помощь на дороге{" ✅" if "emergency" in user_data.services else ""}',
                                   callback_data='emergency'))
    keyboard.add(types.InlineKeyboardButton('Заказать ✉️', callback_data='to_order'))
    return keyboard


# Заказ
def to_order(message):
    username = message.chat.username
    user_data.username = username
    phone_number = user_data.phone_number
    if db_requests.get_user_tg(user_data.tg_id) is None:
        if (user_data.lon is not None) and (user_data.lat is not None):
            geolocation = f"{user_data.lon}:{user_data.lat}"
        elif user_data.geolocation_text is not None:
            geolocation = user_data.geolocation_text
        db_requests.add_user(username, phone_number, geolocation,
                             user_data.tg_id)  # Добавление нового пользователя в бд

    user_data.editing_services = False
    bot.send_message(message.chat.id, 'Опишите проблему и ситуацию')
    user_data.state = 4
    bot.register_next_step_handler(message, to_order_listener)


# Прослушиватель отправленной проблемы
def to_order_listener(message):
    if user_data.state == 4:
        if message.text and '/' not in message.text:
            user_data.description = message.text

            if (user_data.lon is not None) and (user_data.lat is not None):
                geolocation = f"{user_data.lon}:{user_data.lat}"
            elif user_data.geolocation_text is not None:
                geolocation = user_data.geolocation_text
            tmp_services = ', '.join(map(str, user_data.services))
            db_requests.add_order(tmp_services, user_data.tg_id, db_requests.get_user_id(user_data.tg_id), geolocation,
                                  user_data.geolocation_explain, user_data.description)

            bot.send_message(message.chat.id, "С вами свяжутся в течении 15 минут")
            send_to_chat(message)
        elif message.text == '/start':
            replyKeyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
            main(message)
        elif '/' in message.text and '/start' not in message.text:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
            keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='to_order'))
            bot.send_message(message.chat.id, 'Не удалось распознать текст', reply_markup=keyboard)
    else:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        replyKeyboard.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id,
                         'Вы нарушили порядок составления заявки, пожалуйста перезапустите процесс заявки - /start',
                         reply_markup=replyKeyboard)


# Отправка заявки в чат Админов
def send_to_chat(message):
    service_translation = {
        'refuel': 'Заправить',
        'wash': 'Помыть',
        'serve': 'Обслужить',
        'overtake': 'Перегнать',
        'emergency': 'Срочная помощь на дороге'
    }
    user_info = db_requests.get_user_info(user_data.tg_id)
    order = db_requests.get_last_order(user_data.tg_id)
    user_data.username = user_info['username']
    user_data.phone_number = user_info['phone_number']

    user_data.description = order['description']
    if len(order['geolocation']) == 19 and ':' in order['geolocation']:
        parts = order['geolocation'].split(':')
        if len(parts) == 2:
            user_data.lon = parts[0]
            user_data.lat = parts[1]
    else:
        user_data.geolocation_text = order['geolocation']
    user_data.geolocation_explain = order['geolocation_explain']
    user_data.services = order['services'].split(', ')
    russian_services = [service_translation.get(service, 'Неизвестная услуга') for service in user_data.services]
    user_data.services = ", ".join(russian_services)
    if user_data.lat and user_data.lon:
        sent_message = bot.send_message(admin_chat_id,
                                        f"⚡️Новый заказ № {db_requests.get_last_order(user_data.tg_id)['order_id']}⚡️ \nНикнейм - {user_data.username} \nНомер телефона - {user_data.phone_number} \nПроблема - {user_data.description}\nУточнения - {user_data.geolocation_explain} \nВиды работ - {user_data.services} \n")
        bot.send_location(admin_chat_id, user_data.lat, user_data.lon)
    else:
        sent_message = bot.send_message(admin_chat_id,
                                        f"⚡️Новый заказ № {db_requests.get_last_order(user_data.tg_id)['order_id']}⚡️ \nНикнейм - {user_data.username} \nНомер телефона - {user_data.phone_number} \nПроблема - {user_data.description}\nМестоположение - {user_data.geolocation_text} \nУточнения - {user_data.geolocation_explain} \nВиды работ - {user_data.services} \n")
    db_requests.add_order_message_id(sent_message.message_id, db_requests.get_last_order(user_data.tg_id)['order_id'])


bot.infinity_polling()
