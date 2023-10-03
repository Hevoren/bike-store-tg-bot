from Bot.Shared.Connections import *

def state_machine(order, services, bot, admin_chat_id, callback, update_requests, insert_requests,
                  get_requests):
    chat_link = f"https://t.me/{callback.from_user.username}"
    if order[10] == 1:
        update_requests.update_order_state(order[0], 2)
        insert_requests.add_dealing_order(callback.from_user.id, order[0])

        keyboards = types.InlineKeyboardMarkup()
        keyboards.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
        keyboards.add(types.InlineKeyboardButton(text="Я на месте", callback_data='deal'))
        bot.send_message(order[2], 'Фиксик уже в пути и уже скоро будет у вас')
        keyboard_message(bot, keyboards, order, services, admin_chat_id, callback)
    elif (order[10] == 2) and (get_requests.get_prop("execution_orders", "*", "order_id", order[0])[
                                   1] == callback.from_user.id):

        update_requests.update_order_state(order[0], 3)
        keyboards = types.InlineKeyboardMarkup()
        keyboards.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
        keyboards.add(types.InlineKeyboardButton(text="Выполнил", callback_data='deal'))
        keyboard_message(bot, keyboards, order, services, admin_chat_id, callback)
        bot.send_message(order[2], 'Фиксик приехал и готов выполнять свою работу')
    elif (order[10] == 3) and (get_requests.get_prop("execution_orders", "*", "order_id", order[0])[
                                   1] == callback.from_user.id):

        update_requests.update_order_state(order[0], 4)
        keyboards = types.InlineKeyboardMarkup()
        keyboards.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
        keyboards.add(types.InlineKeyboardButton(text="Выполнено ✅", callback_data='asdasd'))
        keyboard_message(bot, keyboards, order, services, admin_chat_id, callback)
        rate_work(order[2], callback.message.message_id, get_requests, bot)


def keyboard_message(bot, keyboards, order, services, admin_chat_id, callback):
    location_text = None
    if order[6] != 'None':
        location_text = f"Местоположение - {order[6]}\n"
    elif order[6] == 'None':
        location_text = ""

    message_text = (
        f"⚡️️Заказ № {order[0]}⚡️ \n"
        f"Никнейм - @{order[4]} \n"
        f"Номер телефона - {order[5]} \n"
        f"Проблема - {order[9]} \n"
        f"{location_text}"
        f"Уточнения - {order[8]} \n"
        f"Виды работ - {services} \n"
    )

    bot.edit_message_text(message_text, admin_chat_id, callback.message.message_id, reply_markup=keyboards)


def rate_work(tg_id, order_message_id, get_requests, bot):
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
    help_services.adding_rate_message_json(user[0], tg_id, order_message_id, rate_message_id)


def rate_work_listener(order_message_id, order, services, callback):
    geolocation = order[6]

    if geolocation:
        location_text = f"Местоположение - {geolocation}\n"
    else:
        location_text = ""

    chat_link = f"https://t.me/{callback.from_user.username}"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
    message_text = (
        f"⚡️️Заказ № {order[0]}⚡️ \n"
        f"Никнейм - @{order[4]} \n"
        f"Номер телефона - {order[5]} \n"
        f"Проблема - {order[9]} \n"
        f"{location_text}"
        f"Уточнения - {order[8]} \n"
        f"Виды работ - {services} \n"
        f"Оценка работы - {callback.data}"
    )
    bot.edit_message_text(
        message_text,
        admin_chat_id, order_message_id,
        reply_markup=keyboard,
        parse_mode="html")
    bot.edit_message_text("Спасибо за отзыв!", callback.message.chat.id, callback.message.message_id)
