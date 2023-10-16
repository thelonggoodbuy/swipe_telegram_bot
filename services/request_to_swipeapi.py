import httpx
import json

from pymongo import MongoClient
from services.get_secret_values import return_secret_value

mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')

client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection



class OrdinaryRequestSwipeAPI():
    def __call__(self, method, url, chat_id, **kwargs):
        with httpx.Client() as client:
            auth_data = bot_aut_collection.find_one({"chat_id": chat_id})
            return self.send_request(method, url, client, chat_id, auth_data, **kwargs)

            
    def send_request(self, method, url, client, chat_id, auth_data, **kwargs):
        if auth_data:
            client.headers['Authorization'] = f"Bearer {auth_data['access_token']}"
        response = getattr(client, method)(url, **kwargs)
        match response.status_code:
            case 401:
                return self.handling_401(method, url, client, chat_id, auth_data, **kwargs)
            case _:
                return response


    def handling_401(self, method, url, client, chat_id, auth_data, **kwargs):
        data = {'refresh': auth_data['refresh_token']}
        refresh_url = f"{base_url_secret}/api/token/refresh/"
        response = client.post(refresh_url, data=data, timeout=10.0)

        if response.status_code == 200:
            response_data = json.loads(response.text)
            new_access_token = response_data['access']
            bot_aut_collection.update_one({"chat_id": chat_id},\
                                    {"$set": {"access_token": new_access_token}}, upsert=False)
            
            auth_data = bot_aut_collection.find_one({"chat_id": chat_id})
            headers = {'Authorization': f"Bearer {auth_data['access_token']}"}
            response = client.get(url, headers=headers, timeout=10.0)
            return response
        


class RegistrationRequestSwipeAPI(OrdinaryRequestSwipeAPI):
    def __call__(self, method, url, chat_id, **kwargs):
        with httpx.Client() as client:
            auth_data = None
            return self.send_request(method, url, client, chat_id, auth_data, **kwargs)
        


class LoginRequestSwipeAPI():
    def __call__(self, method, url, chat_id, **kwargs):
        with httpx.Client() as client:
            return self.send_request(method, url, client, chat_id, **kwargs)

            
    def send_request(self, method, url, client, chat_id, **kwargs):
        response = getattr(client, method)(url, **kwargs)
        return response

    def handling_401(self, method, url, client, chat_id, auth_data, **kwargs):
        data = {'refresh': auth_data['refresh_token']}
        refresh_url = f"{base_url_secret}/api/token/refresh/"
        response = client.post(refresh_url, data=data, timeout=10.0)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            new_access_token = response_data['access']
            bot_aut_collection.update_one({"chat_id": chat_id},\
                                    {"$set": {"access_token": new_access_token}}, upsert=False)
            client.headers['Authorization'] = f"Bearer {new_access_token}"
            response = getattr(client, method)(url, **kwargs)
            return response
