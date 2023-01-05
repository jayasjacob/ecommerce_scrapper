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

for subCategory in response_list:
    if subCategory.find('=') > 0:
        print("Fixing Sub Category : ",subCategory)
        old_subCategory = subCategory
        subCategory = subCategory[:subCategory.find('&')]
        # update the product by requesting the product with the subcategory
        url = BASE_URL + '/product/?subcategory=' + old_subCategory
        l = requests.get(url, headers=header)
        data = l.json()
        for item in data:
            print("-->",item["subcategory"])
            item["subcategory"] = subCategory
            res = requests.patch(BASE_URL + '/product/' + item['product_id'],data=json.dumps(item), headers=header)
            print(res.status_code)
    else:
        print("Correct Sub Category : ",subCategory)