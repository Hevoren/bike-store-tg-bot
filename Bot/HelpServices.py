import json
from DB.UserData import UserData
from telebot import types

user_data = UserData()


class HelpServices:
    def add_first_message(self, tg_id, first_message_id):
        with open("DB/first_messages.json", 'r') as locst:
            data = json.load(locst)

        data.append({
            "tg_id": tg_id,
            "first_message_id": first_message_id,
        })

        with open("DB/first_messages.json", 'w') as locst:
            json.dump(data, locst)

    def get_first_message(self, tg_id):
        with open("DB/first_messages.json", 'r') as locst:
            data = json.load(locst)
        first_message_id = None
        for obj in data:
            if "tg_id" in obj and obj["tg_id"] == tg_id:
                first_message_id = obj["first_message_id"]
                break

        return first_message_id

    def delete_first_message_by_tg_id(self, tg_id):
        file_path = "DB/first_messages.json"

        with open(file_path, 'r') as locst:
            data = json.load(locst)

        new_data = [obj for obj in data if "tg_id" not in obj or obj["tg_id"] != tg_id]

        with open(file_path, 'w') as locst:
            json.dump(new_data, locst)

    def adding_json(self, user_id, tg_id, order_message_id, rate_message_id):
        with open("DB/messages_storage.json", 'r') as locst:
            data = json.load(locst)

        # Append new data to the list
        data.append({
            "tg_id": tg_id,
            "user_id": user_id,
            "order_message_id": order_message_id,
            "rate_message_id": rate_message_id
        })

        # Write the updated data back to the JSON file
        with open("DB/messages_storage.json", 'w') as locst:
            json.dump(data, locst)

    def getting_json(self, rate_message_id):
        with open("DB/messages_storage.json", 'r') as locst:
            data = json.load(locst)
        order_message_id = None
        for obj in data:
            if "rate_message_id" in obj and obj["rate_message_id"] == rate_message_id:
                if "order_message_id" in obj:
                    order_message_id = obj["order_message_id"]
                break

        return order_message_id

    def translate_services(self, order):
        services = order['services'].split(', ')
        russian_services = [user_data.service_translation.get(service, 'Неизвестная услуга') for service in services]
        return ", ".join(russian_services)

    def state_machine(self, order, services, bot, admin_chat_id, callback, update_requests, insert_requests,
                      get_requests):
        chat_link = f"https://t.me/{callback.from_user.username}"
        if order['state'] == 1:
            update_requests.update_order_state(order['id'], 2)
            insert_requests.add_dealing_order(callback.from_user.id, order['id'])

            keyboards = types.InlineKeyboardMarkup()
            keyboards.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
            keyboards.add(types.InlineKeyboardButton(text="Я на месте", callback_data='deal'))
            bot.send_message(order['tg_id'], 'Фиксик уже в пути и уже скоро будет у вас')
            self.keyboard_message(bot, keyboards, order, services, admin_chat_id, callback)
        elif (order['state'] == 2) and (get_requests.get_prop("execution_orders", "*", "order_id", order['id'])[
                                            'tg_id'] == callback.from_user.id):
            update_requests.update_order_state(order['id'], 3)
            keyboards = types.InlineKeyboardMarkup()
            keyboards.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
            keyboards.add(types.InlineKeyboardButton(text="Выполнил", callback_data='deal'))
            self.keyboard_message(bot, keyboards, order, services, admin_chat_id, callback)
            bot.send_message(order['tg_id'], 'Фиксик приехал и готов выполнять свою работу')
        elif (order['state'] == 3) and (get_requests.get_prop("execution_orders", "*", "order_id", order['id'])[
                                            'tg_id'] == callback.from_user.id):
            update_requests.update_order_state(order['id'], 4)
            keyboards = types.InlineKeyboardMarkup()
            keyboards.add(types.InlineKeyboardButton(text="Написать клиенту", url=chat_link))
            keyboards.add(types.InlineKeyboardButton(text="Выполнено ✅", callback_data='asdasd'))
            self.keyboard_message(bot, keyboards, order, services, admin_chat_id, callback)
            self.rate_work(order['tg_id'], callback.message.message_id, get_requests, bot)

    def keyboard_message(self, bot, keyboards, order, services, admin_chat_id, callback):
        if order['geolocation'] != 'None':
            location_text = f"Местоположение - {order['geolocation']}\n"
        elif order['geolocation'] == 'None':
            location_text = ""


        message_text = (
            f"⚡️️Заказ № {order['id']}⚡️ \n"
            f"Никнейм - @{order['username']} \n"
            f"Номер телефона - {order['phone_number']} \n"
            f"Проблема - {order['description']} \n"
            f"{location_text}"
            f"Уточнения - {order['geolocation_explain']} \n"
            f"Виды работ - {services} \n"
        )

        bot.edit_message_text(message_text, admin_chat_id, callback.message.message_id, reply_markup=keyboards)

    def rate_work(self, tg_id, order_message_id, get_requests, bot):
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
        self.adding_json(user['id'], tg_id, order_message_id, rate_message_id)
