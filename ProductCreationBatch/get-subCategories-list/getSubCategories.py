import requests
import json

# development
# BASE_URL = 'https://apistaging.revmeup.in/api/v1'
# production
BASE_URL = 'https://api.revmeup.in/api/v1'
USERID = 'ZKh5adE6Lvb2lQGrru9LEKWQUXq2'
PASSWORD = 'ZKh5adE6Lvb2lQGrru9LEKWQUXq2'

url = BASE_URL + "/user/login"
response = requests.post(url, json={
    "userid": USERID,
    "password": PASSWORD
})
a = response.json()
tok = a['token']
header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}

url = BASE_URL + '/product/subcategory'
response_api = requests.get(url, headers=header)

response_list = list(response_api.json())

with open('response.txt','w')as file:
    for i in response_list:
        file.write(i)
        file.write('\n')

