# Import statements
import datetime
import string
import requests
import json
import random
from .config import *
BASE_URL = Credentials.api_base_url
url = "https://apistaging.revmeup.in/api/v1/user/login"
response = requests.post(url, json={
    "userid": "ZKh5adE6Lvb2lQGrru9LEKWQUXq2",
     "password": "ZKh5adE6Lvb2lQGrru9LEKWQUXq2"
 })
a = response.json()
tok = a['token']
header_1 = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
get_hot_deals = requests.get(BASE_URL + '/hotdeals', headers=header_1)
fetched_hot_deals = get_hot_deals.json()
# Create Hotdeals, Function accepts no parameters.
class Hotdeals():
    def __init__(self):
        pass

    # Method to create hotdeals, acceps the parameters (
    # item - The details of the item
    # Header - API header for sending the data to the DB
    # position - Position of the store
    # Offer_percentage - The percentage of the offer
    # Previous price of the product or item
    def hotdeals_creation(self, item, header, position, offer_percentage, old_price):
        # Storing the current date
        today = datetime.datetime.now()
        current_date = today.strftime("%d/%m/%Y")

        # Creating the dictionary
        hotdeals_payload = {}
        exp = datetime.datetime.now() + datetime.timedelta(days=7)

        # Adding the different fields to the dictionary
        hotdeals_payload['hotDealId'] = ''.join(random.sample(string.ascii_lowercase + string.digits, 15))
        hotdeals_payload['hotDealDescription'] = offer_percentage.__str__() + " % off on" + item['product_name']
        hotdeals_payload['date_created'] = current_date
        hotdeals_payload['hotDealName'] = item['product_name']
        hotdeals_payload['offer'] = offer_percentage.__str__() + " %"
        hotdeals_payload['product_id'] = item['product_id']
        hotdeals_payload['photos'] = item["photos"]
        hotdeals_payload['hotDealPrice'] = item["stores"][position]["storePrice"]
        hotdeals_payload['oldPrice'] = old_price.__str__()
        hotdeals_payload['newPrice'] = item["stores"][position]["storePrice"]
        hotdeals_payload["expirydate"] = str(exp.strftime("%d/%m/%Y"))

        # Creating the coins for the hotdeal
        coins = 0.01 * int(item["stores"][position]["storePrice"])
        if coins <= 50:
            hotdeals_payload['revcoins'] = "50"
        else:
            hotdeals_payload['revcoins'] = coins.__str__()

        # Type of the hotdeal
        hotdeals_payload['type'] = "MODEST_DEALS"

        # Sending the data of the hotdeals to the DB
        # The API call has the URL to the DB
        # Actual data
        # Header including the token for the transaction
        #patching data if its there else creating data
        try:
            if fetched_hot_deals[0]['product_id'] == hotdeals_payload['product_id']:
                hot_deal_id = fetched_hot_deals[0]['hotDealId']
                payload_2 = hotdeals_payload
                payload_2['hotDealId'] = hotdeals_payload['hotDealId']
                requests.patch(BASE_URL + '/hotdeals/' + hot_deal_id, data=json.dumps(payload_2), headers=header_1)
            else:
                r = requests.post(BASE_URL + '/hotdeals', data=json.dumps(hotdeals_payload),
                                  headers=header)
        except:
            r = requests.post(BASE_URL + '/hotdeals', data=json.dumps(hotdeals_payload),
                              headers=header)

        # print(r.status_code)
        #*******Deleting Expired items*****************


        for i in fetched_hot_deals:
            expiry_date = i['expirydate']
            if expiry_date == current_date:
                id = i['hotDealId']
                requests.delete(BASE_URL + '/hotdeals/' + id, headers=header_1)


