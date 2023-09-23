import json
from DB.UserData import UserData

user_data = UserData()


class HelpServices:
    def adding_json(self, user_id, tg_id, order_message_id, rate_message_id):
        with open("DB/localstorage.json", 'r') as locst:
            data = json.load(locst)

        # Append new data to the list
        data.append({
            "tg_id": tg_id,
            "user_id": user_id,
            "order_message_id": order_message_id,
            "rate_message_id": rate_message_id
        })

        # Write the updated data back to the JSON file
        with open("DB/localstorage.json", 'w') as locst:
            json.dump(data, locst)

    def getting_json(self, rate_message_id):
        with open("DB/localstorage.json", 'r') as locst:
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
