from telethon import TelegramClient, sync
from config import Config


class Client:
    config = Config.getConfig()
    client = None

    @staticmethod
    def getClient():
        """ Static access method. """
        if Client.client is None:
            Client()

        return Client.client

    def __init__(self):
        """ Virtually private constructor. """
        if Client.client is not None:
            raise Exception("This class is a singleton!")
        else:
            # API CONNECTION #
            api_id = Client.config.get("api_id")
            api_hash = Client.config.get("api_hash")
            phone = Client.config.get('phone')
            Client.client = TelegramClient(phone, api_id, api_hash)
            Client.client.connect()

            # LOGIN
            if not Client.client.is_user_authorized():
                Client.client.send_code_request(phone)
                Client.client.sign_in(phone, input('Enter the code: '))
