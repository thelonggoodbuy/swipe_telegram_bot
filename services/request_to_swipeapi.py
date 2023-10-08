import httpx
import json

from pymongo import MongoClient

from services.get_secret_values import return_secret_value

import time


mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')

client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection




class OrdinaryRequestSwipeAPI():
    def __call__(self, method, url, chat_id, **kwargs):
        with httpx.Client() as client:
            auth_data = bot_aut_collection.find_one({"chat_id": chat_id})
            print('-----CALL-----')
            return self.send_request(method, url, client, chat_id, auth_data, **kwargs)

            
    def send_request(self, method, url, client, chat_id, auth_data, **kwargs):
        if auth_data:
            client.headers['Authorization'] = f"Bearer {auth_data['access_token']}"
        response = getattr(client, method)(url, **kwargs)
        match response.status_code:
            case 401:
                print('---FIRST---401---')
                self.handling_401(method, url, client, chat_id, auth_data, **kwargs)
            case _:
                return response


    def handling_401(self, method, url, client, chat_id, auth_data, **kwargs):
        data = {'refresh': auth_data['refresh_token']}
        refresh_url = f"{base_url_secret}/api/token/refresh/"
        response = client.post(refresh_url, data=data, timeout=10.0)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            new_access_token = response_data['access']
            print('=================NEW=ACCESSS=TOKEN============')
            print(new_access_token)
            print('==============================================')
            bot_aut_collection.update_one({"chat_id": chat_id},\
                                    {"$set": {"access_token": new_access_token}}, upsert=False)
            
            print('-----OLD------')
            print(auth_data['access_token'])
            print('-----NEW-----')
            print(new_access_token)
            print('-------------')

            client.headers['Authorization'] = f"Bearer {new_access_token}"
            print('------url---------------')
            print(url)
            print('------method---------------')
            print(method)
            print('------client-header---------------')
            print(client.headers['Authorization'])
            # time.sleep(10)

            response = getattr(client, method)(url, **kwargs)
            print('======NEW===RESPONSE===')
            print(response.status_code)
            print(response.text)
            print('=======================')
            return response
        

class RegistrationRequestSwipeAPI(OrdinaryRequestSwipeAPI):
    def __call__(self, method, url, chat_id, **kwargs):
        with httpx.Client() as client:
            auth_data = None
            return self.send_request(method, url, client, chat_id, auth_data, **kwargs)