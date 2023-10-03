from Bot.Shared.Connections import *
from Bot.Services.HelpServices import *

# Начало
@bot.message_handler(commands=['start'])
def start(message):
    delete_user_data(message.chat.id)
    adding_user_data(message.chat.id)
    delete_first_message(message.chat.id)
    user = get_requests.get_prop("users", "*", "tg_id", message.chat.id)
    if user is None:
        insert_requests.add_user(message.from_user.username, message.chat.id)
    global user_data
    user_data = UserData()

    user = get_requests.get_prop("users", "*", "tg_id", message.chat.id)
    insert_requests.add_order_begin(user[0], message.chat.id, message.from_user.username)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Решите мою задачу', callback_data='solve_problem'))
    sent_message = bot.send_message(message.chat.id,
                                    'Мы решим вашу проблему в дороге помоем ваш байк, заправим, а так же перегоним из любой точки в другую.',
                                    reply_markup=keyboard)
    add_first_message(message.chat.id, sent_message.message_id)


# -----------------------------------------------------------------------------------------

# Функция для отправки геолокации
def send_geolocation(message):
    user = get_requests.get_user_info(message.chat.id)
    if step_handler(message, 0, get_requests):
        if user[4] is not None:
            replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
            btn1 = types.KeyboardButton(f"{user[4]}")
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


# Прослушиватель, когда геоданные будет отправлены
@bot.message_handler(content_types=['location'])
def send_geolocation_listener(message):
    if step_handler(message, 0, get_requests):
        order = get_requests.get_last_order(message.chat.id)
        if message.location:
            update_requests.update_one_prop("users", "geolocation_coordinates",
                                            f"{message.location.longitude}:{message.location.latitude}", "tg_id",
                                            message.chat.id)  # Обновление геолокации пользователя

            replyKeyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id,
                             '<b>Шаг 2 из 5.</b>\nУточните где найти вас и название отеля, этаж, комната.',
                             reply_markup=replyKeyboard, parse_mode="html")

            update_requests.update_one_prop("users", "step", 1, "tg_id", message.chat.id)
            update_requests.update_one_prop("orders", "geolocation_coordinates",
                                            f"{message.location.longitude}:{message.location.latitude}", "id", order[0])

            explain_geolocation(message)

        elif message.text and '/' not in message.text:
            update_requests.update_one_prop("users", "geolocation", message.text, "tg_id",
                                            message.chat.id)  # Обновление геолокации пользователя

            replyKeyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id,
                             '<b>Шаг 2 из 5.</b>\nУточните где найти вас и название отеля, этаж, комната.',
                             reply_markup=replyKeyboard, parse_mode="html")
            update_requests.update_one_prop("users", "step", 1, "tg_id", message.chat.id)
            update_requests.update_one_prop("orders", "geolocation", message.text, "id", order[0])
            explain_geolocation(message)

        elif message.text == '/start':
            replyKeyboard = types.ReplyKeyboardRemove()
            sent_message = bot.send_message(message.chat.id, 'Загрузка...', reply_markup=replyKeyboard)
            bot.delete_message(message.chat.id, sent_message.message_id)
            start(message)

        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Прекратить заполнение', callback_data='cancel'))
            keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='solve_problem'))
            bot.send_message(message.chat.id, 'Не удалось распознать запрос', reply_markup=keyboard)


# Уточнение информации по поводу местонахождения
def explain_geolocation(message):
    if step_handler(message, 1, get_requests):
        bot.register_next_step_handler(message, explain_geolocation_listener)


def explain_geolocation_listener(message):
    if step_handler(message, 1, get_requests):
        if message.text and '/' not in message.text:
            update_requests.update_one_prop("users", "step", 2, "tg_id", message.chat.id)
            order = get_requests.get_last_order(message.chat.id)
            update_requests.update_one_prop("orders", "geolocation_explain", message.text, "id", order[0])
            send_contact(message)
        elif message.text == '/start':
            replyKeyboard = types.ReplyKeyboardRemove()
            sent_message = bot.send_message(message.chat.id, 'Загрузка...', reply_markup=replyKeyboard)
            bot.delete_message(message.chat.id, sent_message.message_id)
            start(message)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Прекратить заполнение', callback_data='cancel'))
            keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='explain_geolocation'))
            bot.send_message(message.chat.id, 'Не удалось распознать запрос', reply_markup=keyboard)


# Отправка контакта
@bot.message_handler(content_types=['contact'])
def send_contact(message):
    if step_handler(message, 2, get_requests):
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        replyKeyboard.add(types.KeyboardButton("Поделиться", request_contact=True))
        bot.send_message(message.chat.id,
                         '<b>Шаг 3 из 5.</b>\nПоделитесь контактом, что бы с вами быстро и легко можно с вами связаться',
                         reply_markup=replyKeyboard, parse_mode="html")
        bot.register_next_step_handler(message, send_contact_listener)


# Прослушиватель отправленного контакта
def send_contact_listener(message):
    if step_handler(message, 2, get_requests):
        if message.contact:
            update_requests.update_one_prop("users", "phone_number", message.contact.phone_number, "tg_id",
                                            message.chat.id)  # Обновление номера

            replyKeyboard = types.ReplyKeyboardRemove()
            sent_message = bot.send_message(message.chat.id, 'Загрузка...', reply_markup=replyKeyboard)
            bot.delete_message(message.chat.id, sent_message.message_id)
            update_requests.update_one_prop("users", "step", 3, "tg_id", message.chat.id)

            order = get_requests.get_last_order(message.chat.id)
            update_requests.update_one_prop("orders", "phone_number", message.contact.phone_number, "id", order[0])

            service_choose(message)

        elif message.text == '/start':
            replyKeyboard = types.ReplyKeyboardRemove()
            sent_message = bot.send_message(message.chat.id, 'Загрузка...', reply_markup=replyKeyboard)
            bot.delete_message(message.chat.id, sent_message.message_id)
            start(message)

        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Прекратить заполнение', callback_data='cancel'))
            keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='send_contact'))
            bot.send_message(message.chat.id, 'Не удалось распознать запрос', reply_markup=keyboard)


# Выбор услуги
def service_choose(message):
    if step_handler(message, 3, get_requests):
        update_requests.update_one_prop('users', 'editing_services', 1, 'tg_id', message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Заправить', callback_data='refuel'))
        keyboard.add(types.InlineKeyboardButton('Помыть', callback_data='wash'))
        keyboard.add(types.InlineKeyboardButton('Обслужить', callback_data='serve'))
        keyboard.add(types.InlineKeyboardButton('Перегнать', callback_data='overtake'))
        keyboard.add(types.InlineKeyboardButton('Срочная помощь на дороге', callback_data='emergency'))
        keyboard.add(types.InlineKeyboardButton('Заказать ✉️', callback_data='to_order'))
        bot.send_message(message.chat.id, '<b>Шаг 4 из 5.</b>\nОтметьте, чем вам помочь:', reply_markup=keyboard,
                         parse_mode="html")


# Обновление состояния кнопок при нажатии на них
def generate_updated_keyboard(callback):
    services = getting_user_data(callback.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f'Заправить{" ✅" if "refuel" in services else ""}',
                                            callback_data='refuel'))
    keyboard.add(
        types.InlineKeyboardButton(f'Помыть{" ✅" if "wash" in services else ""}',
                                   callback_data='wash'))
    keyboard.add(
        types.InlineKeyboardButton(f'Обслужить{" ✅" if "serve" in services else ""}',
                                   callback_data='serve'))
    keyboard.add(types.InlineKeyboardButton(f'Перегнать{" ✅" if "overtake" in services else ""}',
                                            callback_data='overtake'))
    keyboard.add(
        types.InlineKeyboardButton(
            f'Срочная помощь на дороге{" ✅" if "emergency" in services else ""}',
            callback_data='emergency'))
    keyboard.add(types.InlineKeyboardButton('Заказать ✉️', callback_data='to_order'))
    return keyboard


# Заказ
def to_order(message):
    if step_handler(message, 3, get_requests):
        order = get_requests.get_last_order(message.chat.id)
        services = ', '.join(map(str, getting_user_data(message.chat.id)))

        update_requests.update_one_prop('users', 'editing_services', 0, 'tg_id', message.chat.id)
        update_requests.update_one_prop("orders", 'services', services, "id", order[0])

        bot.send_message(message.chat.id, '<b>Шаг 5 из 5.</b>\nОпишите проблему и ситуацию', parse_mode="html")
        update_requests.update_one_prop("users", "step", 4, "tg_id", message.chat.id)
        bot.register_next_step_handler(message, to_order_listener)


# Прослушиватель отправленной проблемы
def to_order_listener(message):
    order = get_requests.get_last_order(message.chat.id)
    if step_handler(message, 4, get_requests):
        if message.text and '/' not in message.text:
            update_requests.update_one_prop("orders", "description", message.text, "id", order[0])
            bot.send_message(message.chat.id, "С вами свяжутся в течении 15 минут")
            send_to_chat(message)
        elif message.text == '/start':
            replyKeyboard = types.ReplyKeyboardRemove()
            sent_message = bot.send_message(message.chat.id, 'Загрузка...', reply_markup=replyKeyboard)
            bot.delete_message(message.chat.id, sent_message.message_id)
            start(message)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Прекратить заполнение', callback_data='cancel'))
            keyboard.add(types.InlineKeyboardButton('Повторить', callback_data='to_order'))
            bot.send_message(message.chat.id, 'Не удалось распознать запрос', reply_markup=keyboard)


# -----------------------------------------------------------------------------------------

# Отправка заявки в чат Админов
def send_to_chat(message):
    user = get_requests.get_user_info(message.chat.id)
    order = get_requests.get_last_order(message.chat.id)
    geolocation_coordinates = order[7]
    lon = None
    lat = None
    if geolocation_coordinates is not None:
        if len(geolocation_coordinates) == 19 and ':' in geolocation_coordinates:
            parts = geolocation_coordinates.split(':')
            if len(parts) == 2:
                lon = parts[0]
                lat = parts[1]

    services = translate_services(order)

    chat_link = f"https://t.me/{user[2]}"

    if lat and lon:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
        keyboard.add(types.InlineKeyboardButton(text="Договорился", callback_data='deal'))
        sent_message = bot.send_message(admin_chat_id,
                                        f"⚡️️Заказ № {order[0]}⚡️ \nНикнейм - @{order[4]} \nНомер телефона - {order[5]} \nПроблема - {order[9]}\nУточнения - {order[8]} \nВиды работ - {services} \n",
                                        reply_markup=keyboard)
        bot.send_location(admin_chat_id, lat, lon, reply_to_message_id=sent_message.message_id)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
        keyboard.add(types.InlineKeyboardButton(text="Договорился", callback_data='deal'))
        sent_message = bot.send_message(admin_chat_id,
                                        f"⚡️️Заказ № {order[0]}⚡️ \nНикнейм - @{order[4]} \nНомер телефона - {order[5]} \nПроблема - {order[9]}\nМестоположение - {order[6]} \nУточнения - {order[8]} \nВиды работ - {services} \n",
                                        reply_markup=keyboard)

    update_requests.update_order_message_id(sent_message.message_id,
                                            get_requests.get_last_order(message.chat.id)[0])
