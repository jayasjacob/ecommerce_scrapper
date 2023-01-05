from subprocess import Popen, PIPE, STDOUT
import os
import json
import requests
from .ApiSearch import AmazonSearch


# scrap driver accepts baseurl, urlinput, username and password of the users
def scrap_url(base_url, url_input, username, password):
    # write URL to file
    global result
    try:
        path = os.path.join(os.path.dirname(__file__), 'scraper/scraper/spiders/url.txt')
        output = open(path, "w")
        output.write(url_input)
        output.close()
    except:
        return -2

        # checks if the URL belongs to Amazon or Flipkart

    # result = ""

    if url_input.find('amazon') > -1:
        try:
            print('API Product Search')
            s_url = url_input
            ASIN = ""
            try:
                try:
                    ASIN = s_url.split("/dp/")[1].split("/")[0].split('?')[0]
                except:
                    ASIN = s_url.split("/dp/")[1].split("/")[0]
            except:
                try:
                    ASIN = s_url.split("/product/")[1].split("/")[0].split('?')[0]
                except:
                    ASIN = s_url.split("/product/")[1].split("/")[0]

            path = os.path.join(os.path.dirname(__file__), 'scraper/scraper/spiders/data.json')
            file = open(path, 'w')
            items = [json.loads(AmazonSearch.get_items(ASIN))]
            json.dump(items, file)
            file.close()

        except:
            if url_input.find('amazon') > -1:
                # If amazon url, then run the amazon scrapper
                command = "cd " + os.path.dirname(__file__) + "/scraper/ && scrapy crawl amazon"
                os.system(command)

    elif url_input.find('flipkart') > -1:
        # if flipkart url, then trigger the flipkart scrapper
        command = "cd " + os.path.dirname(__file__) + "/scraper/ && scrapy crawl flipkart"
        os.system(command)

    else:
        # if the url is of a different store
        return -1

    try:
        path = os.path.join(os.path.dirname(__file__), 'scraper/scraper/spiders/data.json')
        output = open(path, "r")
        try:
            result = json.loads(output.read())[0]
        except:
            result = json.loads((output.read()))
        output.close()
    except:
        return -2

    # checking from DB
    # Generating Authentication token
    url = base_url + "/user/login"
    response = requests.post(url, json={
        "userid": username,
        "password": password
    })

    auth_response = response.json()
    if auth_response['status'] == 'fail':
        return -3

    header = {'Authorization': 'Bearer ' + auth_response['token'], 'content-type': "application/json"}

    # print(result['product_name'])
    # print(result['stores'][0]['storePrice'])
    # print(result)
    if result['product_name'] != None:

        if url_input.find('amazon') > -1:
            try:
                try:
                    result['stores'][0]['storePrice'] = str(int(result['stores'][0]['storePrice']))
                    result['stores'][0]['store_mrp'] = str(int(result['stores'][0]['store_mrp']))
                except:
                    pass
                # print(result['stores'][0]['storePrice'])
                # print(result['stores'][0]['storePrice'])
                if result['stores'][0]['storePrice'] != '' and result['stores'][0]['store_mrp'] != '' and \
                        result['stores'][0]['storeTechnicalDetails'] != {}:
                    header = {'Authorization': 'Bearer ' + auth_response['token'],
                              'content-type': "application/json"}

                    # Query for the parsed product to the api
                    url_by_prod_id = base_url + '/product?stores.storeProductId=' + result['stores'][0][
                        'storeProductId']
                    res_prod_id = requests.get(url_by_prod_id, headers=header)

                    prod_info = res_prod_id.json()

                    if prod_info != []:
                        db_price = prod_info[0]['stores'][0]['storePrice'].replace(".00", "").replace(",", "")
                        scraped_price = result['stores'][0]['storePrice'].replace(".00", "").replace(",", "")

                        prod_info[0]['stores'][0]['storePrice'] = scraped_price
                        payload2 = result
                        payload2["product_id"] = prod_info[0]['product_id']
                        res = requests.patch(base_url + '/product' + '/' + prod_info[0]['product_id'],
                                             data=json.dumps(payload2), headers=header)
                        return [result]

                    elif res_prod_id.json() == []:
                        if result['product_name'] != '' and result['product_id'] != '' and result[
                            'stores'] != [] and \
                                result['stores'] != '' and result['stores'][0]["storeProductId"] != '' and \
                                result['stores'][0]["storeLink"] != '' and result['stores'][0]["storePrice"] != '' \
                                and result['category'] != '' and result['subcategory'] != '' and result[
                            "description"] != '' \
                                and result["description"] != [] and result["photos"] != None and result[
                            "photos"] != [] \
                                and result['photos'][0] != '':
                            if result['stores'][0]['storeName'] == '' or result['stores'][0]['storeName'] == None:
                                result['stores'][0]['storeName'] = 'amazon'

                            if '&tag=' not in result['stores'][0]['storeLink']:
                                result['stores'][0]['storeLink'] = result['stores'][0][
                                                                       'storeLink'] + "&tag=revmeup-21"
                            else:
                                result['stores'][0]['storeLink'] = result['stores'][0]['storeLink'].split('&tag=')[
                                                                       0] + "&tag=revmeup-21"
                            payload = json.dumps(result)
                            res = requests.post(base_url + '/product', data=payload, headers=header)
                            return [result]
                else:
                    return -5
            except:
                return -5
        elif url_input.find('flipkart') > -1:
            try:
                url_by_prod_id = base_url + '/product?stores.storeProductId=' + result['stores']['storeProductId']
                res_prod_id = requests.get(url_by_prod_id, headers=header)
                data = res_prod_id.json()

                if data != []:
                    try:
                        model_numb = result['stores']['storeAdditionalDetails']['Model Number']
                        # getting model number from payload
                    except:
                        model_numb = []

                    if model_numb != []:  # checking model number is not empty
                        url2 = base_url + '/product?stores.storeTechnicalDetails.Item model number=' + model_numb  # queriying db with model number
                        l = requests.get(url2, headers=header)
                        product_details = l.json()

                        if product_details == []:  # checking if product details  null
                            url2 = base_url + '/product?stores.storeTechnicalDetails.Model number=' + model_numb
                            l = requests.get(url2, headers=header)
                            return data

                        if product_details != []:
                            flipkart_store = result['stores']

                            product_details[0]['stores'].append(flipkart_store)
                            patch_url = base_url + '/product/' + product_details[0]['product_id']
                            l = requests.patch(patch_url, data=json.dumps(product_details[0]), headers=header)

                            url_2 = base_url + '/product?stores.storeTechnicalDetails.Model number=' + model_numb
                            l = requests.get(url2, headers=header)
                            return data
                else:
                    payload = json.dumps(result)
                    res = requests.post(base_url + '/product/', data=payload, headers=header)
                    return res.json()
            except:
                return -5
        else:
            return -1
    else:
        return -4
