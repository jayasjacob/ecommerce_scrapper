import json
import requests

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

with open('response.txt', 'w')as file:
    for item in response_list:
        try:
            print("URL Exists")
            if item["stores"][0]["storeLink"].find("&tag=revmeup-21") > -1:
                print('Url is Fine')
            elif item["stores"][0]["storeLink"].find("tag=revmeup-21") > -1:
                print('Fixing URL')
                old_url = item["stores"][0]["storeLink"]
                new_url = old_url.replace("tag=revmeup-21","&tag=revmeup-21")
                item["stores"][0]["storeLink"] = new_url
                res = requests.patch(BASE_URL + '/product/' + item['product_id'], data=json.dumps(item), headers=header)
                file.write("Item Fixed : "+str(item["product_id"])+" : response code : "+str(res.status_code))
                file.write('\n')
            else:
                print('Fixing URL')
                old_url = item["stores"][0]["storeLink"]
                new_url = old_url+"&tag=revmeup-21"
                item["stores"][0]["storeLink"] = new_url
                res = requests.patch(BASE_URL + '/product/' + item['product_id'], data=json.dumps(item), headers=header)
                file.write("Item Fixed : " + str(item["product_id"]) + " : response code : " + str(res.status_code))
                file.write('\n')
        except:
            print("Fixing Product URL : ",item["product_id"] )
            print(item)
            item["stores"][0]["storeLink"] = "www.amazon.in?tag=revmeup-21"
            res = requests.patch(BASE_URL + '/product/' + item['product_id'], data=json.dumps(item), headers=header)
            print(res.status_code)