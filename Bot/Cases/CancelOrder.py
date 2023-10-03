from Bot.Shared.Connections import *


@bot.message_handler(commands=['cancel_order'])
def cancel_order(message):
    keyboard = types.InlineKeyboardMarkup()
    order = get_requests.get_last_order(message.chat.id)
    if order is not None and order[10] != 0:
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='cancel_order'))
        keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='cancel'))
        bot.send_message(message.chat.id, 'Вы уверены, что хотите отменить заказ?', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'У вас нет последних заказов')


def canceling_order(message):
    order = get_requests.get_last_order(message.chat.id)
    if order[10] in [1]:
        bot.delete_message(message.chat.id, message.message_id)
        update_requests.update_one_prop('orders', 'state', 0, 'id', order[0])
        bot.send_message(admin_chat_id, f"Заказ №{order[0]} - <b>Отменен</b>", parse_mode="html")
        bot.send_message(message.chat.id, f"Заказ №{order[0]} - <b>Отменен</b>", parse_mode="html")
    elif order[10] in [0, 2, 3, 4]:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, 'Невозможно отменить завершеный, отмененный или выполняющийся заказ')


def cancel(callback):
    update_requests.update_one_prop("users", "is_asking", 0, "tg_id", callback.from_user.id)
    update_requests.update_one_prop("users", "step", 0, "tg_id", callback.from_user.id)
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    keyboard = types.ReplyKeyboardRemove()
    sent_message = bot.send_message(callback.message.chat.id, 'Отмена...', reply_markup=keyboard)
    bot.delete_message(callback.message.chat.id, sent_message.message_id)
