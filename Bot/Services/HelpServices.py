import json
from Bot.Shared.Connections import *


def add_first_message(tg_id, first_message_id):
    with open("DB/JSON/first_messages.json", 'r') as locst:
        data = json.load(locst)

    data.append({
        "tg_id": tg_id,
        "first_message_id": first_message_id,
    })

    with open("DB/JSON/first_messages.json", 'w') as locst:
        json.dump(data, locst)


def get_first_message(tg_id):
    with open("DB/JSON/first_messages.json", 'r') as locst:
        data = json.load(locst)
    first_message_id = None
    for obj in data:
        if "tg_id" in obj and obj["tg_id"] == tg_id:
            first_message_id = obj["first_message_id"]
            break

    return first_message_id


def delete_first_message_from_json(tg_id):
    file_path = "DB/JSON/first_messages.json"

    with open(file_path, 'r') as locst:
        data = json.load(locst)

    new_data = [obj for obj in data if "tg_id" not in obj or obj["tg_id"] != tg_id]

    with open(file_path, 'w') as locst:
        json.dump(new_data, locst)


# ---------------------------------------------

def adding_rate_message_json(user_id, tg_id, order_message_id, rate_message_id):
    with open("DB/JSON/messages_storage.json", 'r') as locst:
        data = json.load(locst)

    # Append new data to the list
    data.append({
        "tg_id": tg_id,
        "user_id": user_id,
        "order_message_id": order_message_id,
        "rate_message_id": rate_message_id
    })

    with open("DB/JSON/messages_storage.json", 'w') as locst:
        json.dump(data, locst)


def getting_rate_message_json(rate_message_id):
    with open("DB/JSON/messages_storage.json", 'r') as locst:
        data = json.load(locst)
    order_message_id = None
    for obj in data:
        if "rate_message_id" in obj and obj["rate_message_id"] == rate_message_id:
            if "order_message_id" in obj:
                order_message_id = obj["order_message_id"]
            break

    return order_message_id


# ------------------------------------------------

def adding_user_data(tg_id):
    with open("DB/JSON/user_data.json", 'r') as locst:
        data = json.load(locst)

    data.append({
        "tg_id": tg_id,
        "services": []
    })

    with open("DB/JSON/user_data.json", 'w') as locst:
        json.dump(data, locst)


def getting_user_data(tg_id):
    with open("DB/JSON/user_data.json", 'r') as locst:
        data = json.load(locst)
    for obj in data:
        if obj is not None and "tg_id" in obj and obj["tg_id"] == tg_id:
            return obj["services"]
    return None


def update_user_data(tg_id, service):
    with open("DB/JSON/user_data.json", 'r') as locst:
        data = json.load(locst)

    for user in data:
        if user["tg_id"] == tg_id:
            if service in user["services"]:
                user["services"].remove(service)
            else:
                user["services"].append(service)
            break

    with open("DB/JSON/user_data.json", 'w') as locst:
        json.dump(data, locst)


def delete_user_data(tg_id):
    file_path = "DB/JSON/user_data.json"

    with open(file_path, 'r') as locst:
        data = json.load(locst)

    index_to_remove = None
    for index, user_datae in enumerate(data):
        if user_datae["tg_id"] == tg_id:
            index_to_remove = index
            break

    if index_to_remove is not None:
        del data[index_to_remove]

        with open(file_path, 'w') as locst:
            json.dump(data, locst)


# -------------------------------------------

def translate_services(order):
    services = order[3].split(', ')
    russian_services = [user_data.service_translation.get(service, 'Неизвестная услуга') for service in services]
    return ", ".join(russian_services)


def delete_first_message(tg_id):
    first_message_id = get_first_message(tg_id)
    if first_message_id:
        try:
            bot.delete_message(tg_id, first_message_id)
            delete_first_message_from_json(tg_id)
        except Exception as e:
            delete_first_message_from_json(tg_id)


def step_handler(message, step, get_requests):
    user = get_requests.get_user_info(message.chat.id)
    if user[7] == step:
        return True
    else:
        replyKeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        replyKeyboard.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id,
                         'Вы нарушили порядок составления заявки, пожалуйста перезапустите процесс заявки - /start',
                         reply_markup=replyKeyboard)
