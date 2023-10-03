from Bot.Cases.ToOrder import *
from Bot.Cases.CallAdministrator import *
from Bot.Cases.CancelOrder import *
from Bot.Cases.DealingOrder import *
from Bot.Services.HelpServices import *

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'solve_problem':
        delete_first_message(callback.message.chat.id)
        update_requests.update_one_prop("users", "step", 0, "tg_id", callback.from_user.id)
        send_geolocation(callback.message)

    elif callback.data == 'cancel':
        cancel(callback)

    elif callback.data == 'cancel_order':
        canceling_order(callback.message)

    elif callback.data == 'explain_geolocation':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        explain_geolocation(callback.message)

    elif callback.data == 'send_contact':
        send_contact(callback.message)

    elif callback.data in ['refuel', 'wash', 'serve', 'overtake', 'emergency']:
        service = callback.data
        user = get_requests.get_user_info(callback.from_user.id)
        if user[8] == 1:
            update_user_data(callback.from_user.id, service)
            updated_keyboard = generate_updated_keyboard(callback)
            bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                          message_id=callback.message.message_id,
                                          reply_markup=updated_keyboard)

    elif callback.data == 'to_order':
        to_order(callback.message)

    elif callback.data == 'help':
        connection_with_the_operator(callback.message)

    elif callback.data in ['1', '2', '3', '4', '5']:
        order_message_id = getting_rate_message_json(callback.message.message_id)
        update_requests.update_one_prop("orders", "rate", callback.data, "message_id", order_message_id)

        order = get_requests.get_prop("orders", "*", "message_id", order_message_id)
        services = translate_services(order)

        rate_work_listener(order_message_id, order, services, callback)

    elif callback.data == 'deal':
        order = get_requests.get_prop("orders", "*", "message_id", callback.message.message_id)

        services = translate_services(order)
        state_machine(order, services, bot, admin_chat_id, callback, update_requests,
                      insert_requests, get_requests)


# @bot.message_handler(func=lambda m: True)
# def echo_all(message):
#     user = get_requests.get_user_info(message.chat.id)
#     if message.text == '/start':
#         replyKeyboard = types.ReplyKeyboardRemove()
#         sent_message = bot.send_message(message.chat.id, 'Возврат назад...', reply_markup=replyKeyboard)
#         bot.delete_message(message.chat.id, sent_message.message_id)
#         start(message)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
