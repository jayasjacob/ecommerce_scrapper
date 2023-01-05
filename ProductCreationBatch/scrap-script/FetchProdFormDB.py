# Authentication API call-
import json
import pprint

import requests
url = "https://apistaging.revmeup.in/api/v1/user/login"
response = requests.post(url, json={
    "userid": "ZKh5adE6Lvb2lQGrru9LEKWQUXq2",
    "password": "ZKh5adE6Lvb2lQGrru9LEKWQUXq2"
})
a = response.json()
tok = a['token']
header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}

#Getting the available Products from the database
url2 = 'https://apistaging.revmeup.in/api/v1/product?stores.storeTechnicalDetails'
l = requests.get(url2, headers=header)
prod_info = l.json()
pprint.pprint(prod_info)
# storing the product data into "DB_prod.json" file
# with open('./data/DB_prod.json', 'w') as outfile:
#     json.dump(prod_info, outfile, ensure_ascii=False, indent=4)

