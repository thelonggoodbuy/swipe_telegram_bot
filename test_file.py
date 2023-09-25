import httpx

with httpx.Client() as client:
	url = "http://159.89.29.63/users/auth/login_simple_user/"
	data = {"email": "initial_builder@gmail.com", "password": "initial_password"}
	response = client.post(url, data=data)
print('----------------------------')
print(response)
print(response.status_code)
print(response.text)
print('----------------------------')
