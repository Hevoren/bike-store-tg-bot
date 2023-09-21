class UserData:
    def __init__(self):
        self.lat = None
        self.lon = None
        self.geolocation_text = None
        self.geolocation_explain = None
        self.visit = 0
        self.phone_number = None
        self.fi = None
        self.services = []
        self.editing_services = False
        self.description = None
        self.tg_id = 0
        self.username = None
        self.state = 0
        self.service_translation = {
            'refuel': 'Заправить',
            'wash': 'Помыть',
            'serve': 'Обслужить',
            'overtake': 'Перегнать',
            'emergency': 'Срочная помощь на дороге'
        }
        self.order_message_id = None
        self.order_id = None
        self.user_id_admin = None
        self.answering = False

