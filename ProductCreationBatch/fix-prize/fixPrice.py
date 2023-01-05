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

url = BASE_URL + '/product'
response_api = requests.get(url, headers=header)

response_list = list(response_api.json())

for item in response_list:
    try:
        if item["stores"][0]["storePrice"].find(".") > 0 or item["stores"][0]["storePrice"].find(',') > 0:
            print("Fixing Price : ",item["stores"][0]["storePrice"])
            price = item["stores"][0]["storePrice"]
            price = price.split('.')[0]
            item["stores"][0]["storePrice"] = price
            res = requests.patch(BASE_URL + '/product/' + item['product_id'], data=json.dumps(item), headers=header)
            print('Fixed Price : ',item["stores"][0]["storePrice"])
            print(".............................")
        else:
            pass
    except:
        pass