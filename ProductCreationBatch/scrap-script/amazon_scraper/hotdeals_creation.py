import datetime
import string

import requests
import json
from datetime import date
import random
from .config import *
BASE_URL = Credentials.api_base_url
class Hotdeals():
    def __init__(self):
        pass

    def hotdeals_creation(self,item,header, position, offer_percentage, old_price):
        #.......... posting hotdeals data in revme db...................
        today = datetime.datetime.now()
        current_date = today.strftime("%d/%m/%Y")
        hotdeals_payload = {}
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
        hotdeals_payload["expirydate"] =str(datetime.datetime.now() + datetime.timedelta(days=7))

        coins = 0.01 * int(item["stores"][position]["storePrice"])
        if coins <= 50:
            hotdeals_payload['revcoins'] = "50"
        else:
            hotdeals_payload['revcoins'] = coins.__str__()
        hotdeals_payload['type'] = "MODEST_DEALS"




        r = requests.post(BASE_URL +  '/hotdeals', data =json.dumps(hotdeals_payload), headers=header)
        print(r.status_code)

