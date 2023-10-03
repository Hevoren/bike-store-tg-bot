from Bot.Shared.Connections import *


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


def connection_with_the_operator(message):
    update_requests.update_one_prop("users", "is_asking", 1, "tg_id", message.chat.id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
    bot.edit_message_text(f"Опишите суть проблемы", message.chat.id, message.message_id, reply_markup=keyboard)
    bot.register_next_step_handler(message, send_to_admin)


def send_to_admin(message):
    is_asking = get_requests.get_prop("users", "*", "tg_id", message.chat.id)['is_asking']
    if is_asking == 1:
        chat_link = f"https://t.me/{message.from_user.username}"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Написать", url=chat_link))
        bot.send_message(admin_chat_id, f"Поступила проблема от @{message.from_user.username}: {message.text}",
                         reply_markup=keyboard)
        bot.send_message(message.chat.id, f"Ваше сообщение успешно отправлено, через некоторое вермя вам ответят")
