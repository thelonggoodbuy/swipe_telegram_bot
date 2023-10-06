from request_to_swipeapi import RequestSwipeAPI
# from .get_secret_values import return_secret_value
import get_secret_values


# base_url_secret = get_secret_values.return_secret_value('BASE_URL')



method = 'post'
url = f"http://127.0.0.1:8000/users/auth/login_simple_user/"

my_request = RequestSwipeAPI()
chat_id = 967388608
data = {"email": "initial_builder@gmail.com",
        "password": "initial_password"}

response = my_request(method, url, chat_id, data=data, check_perm = False)

print('------RESP-----------')
print(response)
print('------STATUS---------')
# print(response.status_code)
print('------DATA-----------')
print(response.text)
print('---------------------')