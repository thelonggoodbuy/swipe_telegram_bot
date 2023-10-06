import httpx
import json


from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection



class RequestError():

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class RequestSwipeAPI():

    def __call__(self,
                method, 
                url,
                chat_id,
                data=None, 
                check_perm=True):
        

        with httpx.Client() as client:
            if check_perm == True:
                auth_data = bot_aut_collection.find_one({"chat_id": chat_id})
                try:
                    client.headers['Authorization'] = f"Bearer {auth_data['access_token']}"
                    response = getattr(client, method)(url, data)
                    match response.status_code:
                        case 200:
                            # return response
                            self.handling_200(response)
                        case 400:
                            # return response.text
                            self.handling_400(response)
                        case 401:
                            self.handling_401(response, auth_data, chat_id, method, url)
                            
                except TypeError:
                    nonregistrated_error = RequestError('Ви не зареєстровані')
                    response = nonregistrated_error

            else:
                kwargs = {"data": data}
                response = getattr(client, method)(url, **kwargs)
                match response.status_code:
                    case 200:
                        # return response
                        self.handling_200(response)
                    case 400:
                        # return response.text
                        self.handling_400(response)
                    case 401:
                        self.handling_401_without_check_perm(response)
            return response
        


    def handling_200(self, response):
        return response


    def handling_400(self, response):
        return response.text
    

    def handling_401(self, response, auth_data, chat_id, method, url):
        data = {'refresh': auth_data['refresh_token']}
        refresh_url = f"http://127.0.0.1:8000/api/token/refresh/"
        response = client.post(refresh_url, data=data, timeout=10.0)

        if response.status_code == 200:
            response_data = json.loads(response.text)
            new_access_token = response_data['access']
            bot_aut_collection.update_one({"chat_id": chat_id},\
                                    {"$set": {"access_token": new_access_token}}, upsert=False)
            client.headers['Authorization'] = f"Bearer {response_data['access']}"
            response = getattr(client, method)(url)

            if response.status_code == 200:
                return response
            
            elif response.status_code == 401:
                RequestError('Ви давно не заходили в систему. Залогінтесь знов')
                # return response.text

            
        elif response.status_code == 401:
            old_token_error = RequestError('Ви давно не заходили в систему. Залогінтесь знов')
            return old_token_error
        

    def handling_401_without_check_perm(self, response):
        return response.text