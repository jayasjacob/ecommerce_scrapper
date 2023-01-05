# # import copy
# # import json
# # import pprint
# #
# # import requests
# #
# # url = "https://apistaging.revmeup.in/api/v1/user/login"
# # response = requests.post(url, json={
# #     "userid": "ZKh5adE6Lvb2lQGrru9LEKWQUXq2",
# #     "password": "ZKh5adE6Lvb2lQGrru9LEKWQUXq2"
# # })
# # a = response.json()
# # tok = a['token']
# # # Adding token for API requests
# # header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
# #
# # # Query for the parsed product to the api
# # url2 = 'https://apistaging.revmeup.in/api/v1/product?limit=1'
# # l = requests.get(url2, headers=header)
# # l.status_code
# # prod_info = l.json()
# # #
# # # storeData = {
# # #                 '_id': '5f60f0c04a37eb84c9931f',
# # #               'instock': 'In stock.',
# # #               'rating': '3.9 out of 5 stars',
# # #               'reviews': {},
# # #               'storeAdditionalDetails': {},
# # #               'storeTechnicalDetails': {},
# # #               'store_logo': 'https://i.pinimg.com/564x/42/a7/86/42a7861bb1a403af534b18986ab4e198.jpg',
# # #               'store_mrp': '1249'
# # #              }
# #
# #
# #
# # pprint.pprint(prod_info)
# #
# # payload = prod_info
# #
# # res = requests.patch('https://apistaging.revmeup.in/api/v1/product' + '/' + prod_info[0]['product_id'],
# #                      data=json.dumps(payload),
# #                      headers=header)
# #
# #
# # # Getting product data if exists
# # prod_info = l.json()
# # pprint.pprint(prod_info)
# #
# # storeAdditionalDetails = {'50 out of 5 stars': 'Best Sellers Rank',
# #                           '7886 in Computers & Accessories': 'See Top 100 in Computers & Accessories',
# #                           'ASIN': 'B08GDBK3LD'
# #                           }
# # i = 0
# # new_dict = {}
# # for k,v in storeAdditionalDetails.items():
# #     if i<2:
# #         new_dict[v] = k
# #         i+=1
# #     else:
# #         new_dict[k] = v
# #
# # storeAdditionalDetails = new_dict
# # print(storeAdditionalDetails)
# # # import re
# # #
# # # additional_details = ['\n',
# # #                        '\n    ',
# # #                        '\n         ',
# # #                        '\n            ',
# # #                        '\n                Electronics\n            ',
# # #                        '\n         ',
# # #                        '\n         ',
# # #                        '\n             ›\n         ',
# # #                        '\n         ',
# # #                        '\n            ',
# # #                        '\n                Mobiles & Accessories\n            ',
# # #                        '\n         ',
# # #                        '\n         ',
# # #                        '\n             ›\n         ',
# # #                        '\n         ',
# # #                        '\n            ',
# # #                        '\n'
# # #                        '                Smartphones & Basic Mobiles\n'
# # #                        '            ',
# # #                        '\n         ',
# # #                        '\n         ',
# # #                        '\n             ›\n         ',
# # #                        '\n         ',
# # #                        '\n             ',
# # #                        '\n                 Smartphones\n             ',
# # #                        '\n         ',
# # #                        '\n         ',
# # #                        '\n             ›\n         ',
# # #                        '\n         ',
# # #                        '\n             Samsung Galaxy M51\n         ',
# # #                        '\n    ',
# # #                        '\n',
# # #                        '\n']
# # #
# # # # trim = re.compile(r"[-()\"#/@;:<>{}`+=~|.!?,*]")
# # # # data = trim.sub("",data)
# # # # # data = data.translate({ord(i): None for i in '\\n'})
# # # #
# # # # print(data)
# # # additional_details = [re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*›]", "", file) for file in additional_details]
# # # additional_details = list(map(lambda s: s.strip(), additional_details))
# # # for item in additional_details:
# # #     if item == " ''" or item == "":
# # #         additional_details.remove(item)
# # # print(additional_details)
#
#
# with open ("keywords.txt", "r") as myfile:
#     keyword=myfile.readlines()
# content = [x.strip().replace(" ", "+") for x in keyword]
# print(content)
import csv
import json

import requests


class Credentials:
    userid =  "TJIfeTrxWrPAzxyMqviY8lqHdhg1"
    password = "TJIfeTrxWrPAzxyMqviY8lqHdhg1"
    api_base_url = "https://apistaging.revmeup.in/api/v1"

BASE_URL = Credentials.api_base_url
url = BASE_URL +  "/user/login"
response = requests.post(url, json={
    "userid": Credentials.userid,
    "password": Credentials.password
})
a = response.json()
tok = a['token']
header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}

#Getting the available Products from the database
url2 = BASE_URL +  '/product'
l = requests.get(url2, headers=header)
print(l)
prod_info = l.json()
# storing the product data into "DB_prod.json" file
with open('DB_prod.json', 'w') as outfile:
    json.dump(prod_info, outfile, ensure_ascii=False, indent=4)

# now we will open a file for writing
data_file = open('data_file.csv', 'w')

# create the csv writer object
csv_writer = csv.writer(data_file)

# Counter variable used for writing
# headers to the CSV file
count = 0

for emp in prod_info:
    if count == 0:
        # Writing headers of CSV file
        header = emp.keys()
        csv_writer.writerow(header)
        count += 1

    # Writing data of CSV file
    csv_writer.writerow(emp.values())

data_file.close()




# with open("./Keywords.txt", "r") as myfile:
#     keyword = myfile.readlines()
# content = [x.strip() for x in keyword]
# items = []
#
# with open("./keywords.txt", "a") as bad:
#     for item in content:
#         if item not in items:
#             items.append(item)
#             bad.writelines(item)
#             bad.write("\n")
# bad.close()
# myfile.close()
