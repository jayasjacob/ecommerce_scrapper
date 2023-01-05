import json
from config import *
import requests

def sendToDb(tok,item):
    print("Hai waiting to send to DB")
    data = json.loads(item)
    item = data
    if item['stores'][0]['storePrice'] != '' and item['stores'][0]['store_mrp'] != '' and item['stores'][0]['storeTechnicalDetails'] != {}:
        header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
        url_by_prod_id = api_base_url + '/product?stores.storeProductId=' + item['stores'][0]['storeProductId']
        res_prod_id = requests.get(url_by_prod_id, headers=header)

        prod_info = res_prod_id.json()

        if prod_info != []:
            db_price = str(prod_info[0]['stores'][0]['storePrice']).replace(".00", "").replace(".0","").replace(",", "")
            scraped_price = str(item['stores'][0]['storePrice']).replace(".00", "").replace(".0","").replace(",", "")

            if db_price.find('.') > 0:
                db_price = db_price.split('.')[0]

            if scraped_price.find('.') > 0:
                scraped_price = scraped_price.split('.')[0]

            if scraped_price != None and scraped_price != '' and int(scraped_price) > 0 and int(db_price) != int(
                    scraped_price) \
                    or prod_info[0]["product_name"] != item['product_name'] \
                    or prod_info[0]["description"] != item['description'] \
                    or len(prod_info[0]["photos"]) < len(item['photos']) \
                    or prod_info[0]["stores"][0]["storeProductId"] != item['stores'][0]["storeProductId"] \
                    or prod_info[0]["stores"][0]["storeDescription"] != item['stores'][0]["storeDescription"] \
                    or prod_info[0]["stores"][0]["rating"] != item['stores'][0]["rating"] \
                    or prod_info[0]["stores"][0]["instock"] != item['stores'][0]["instock"] \
                    or prod_info[0]['stores'][0]['storePrice'] == '' or prod_info[0]['stores'][0][
                'storePrice'] == ' ' or \
                    prod_info[0]['stores'][0]['storePrice'] == None or prod_info[0]["stores"][0]["storePrice"] != \
                    item['stores'][0]["storePrice"] \
                    or prod_info[0]['stores'][0]['store_mrp'] == '' or prod_info[0]['stores'][0][
                'store_mrp'] == ' ' or \
                    prod_info[0]['stores'][0]['store_mrp'] == None or prod_info[0]["stores"][0]["store_mrp"] != \
                    item['stores'][0]["store_mrp"]:

                prod_info[0]['stores'][0]['storePrice'] = scraped_price
                payload2 = item
                payload2["product_id"] = prod_info[0]['product_id']
                # pprint.pprint(payload2)
                # print("Base URL" + BASE_URL)
                # print("PROD_ID:" + str(prod_info[0]['product_id']))
                res = requests.patch(
                    api_base_url + '/product' + '/' + prod_info[0]['product_id'],
                    data=json.dumps(payload2), headers=header)
                print("Updated the data : ",item['stores'][0]["storeProductId"])
            else:
                print("No update for :",item['stores'][0]["storeProductId"])

        elif res_prod_id.json() == []:
            print("Created the data:",item['stores'][0]["storeProductId"])

            if item['product_name'] != '' and item['product_id'] != '' and item['stores'] != [] and item[
                'stores'] != '' and item['stores'][0]["storeProductId"] != '' and item['stores'][0][
                "storeLink"] != '' and item['stores'][0]["storePrice"] != '' and item['category'] != '' and item[
                'subcategory'] != '' and item["description"] != '' and item["description"] != [] and item[
                "photos"] != None and item["photos"] != [] and item['photos'][0] != '':
                if item['stores'][0]['storeName'] == '' or item['stores'][0]['storeName'] == None:
                    item['stores'][0]['storeName'] = 'amazon'

                if str(item['stores'][0]['storePrice']).find('.') > 0:
                    item['stores'][0]['storePrice'] = str(item['stores'][0]['storePrice']).split('.')[0]

                if '&tag=' not in item['stores'][0]['storeLink']:
                    item['stores'][0]['storeLink'] = item['stores'][0]['storeLink'] + "&tag=revmeup-21"
                else:
                    item['stores'][0]['storeLink'] = item['stores'][0]['storeLink'].split('&tag=')[
                                                         0] + "&tag=revmeup-21"
                payload = json.dumps(item)
                res = requests.post(api_base_url + '/product'
                                    , data=payload,
                                    headers=header)

        with open('SuccessProducts.json', 'a') as outfile_1:
            json.dump(item, outfile_1, ensure_ascii=False, indent=4)

    else:
        with open('./data/ErrorProducts.json', 'a') as outfile:
            json.dump(item, outfile, ensure_ascii=False, indent=4)