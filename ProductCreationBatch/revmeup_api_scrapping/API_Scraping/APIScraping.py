from subprocess import Popen, PIPE, STDOUT
import os
import json
import requests
from .config import *


def scrap_url(url_input,username,password):
    result = ""
    if url_input.find('amazon') > -1:

        try:
            command = "cd API_Scraping/scraper/ && rm data.json"
            os.system(command)
        except:
            pass

        command = "cd API_Scraping/scraper/ && rm ./scraper/spiders/url.txt && echo '" + url_input + "' >> ./scraper/spiders/url.txt ;"
        os.system(command)

        command = "cd API_Scraping/scraper/ && scrapy crawl amazon -o ./data.json"
        os.system(command)

        path = os.path.join(os.path.dirname(__file__), 'scraper/data.json')
        output = open(path, "r")
        result = json.loads(output.read())[0]
        output.close()

    elif url_input.find('flipkart') > -1:

        try:
            command = "cd API_Scraping/scraper/ && rm data.json"
            os.system(command)
        except:
            pass

        command = "cd API_Scraping/scraper/ && rm ./scraper/spiders/url.txt && echo '" + url_input + "' >> ./scraper/spiders/url.txt ;"
        os.system(command)

        command = "cd API_Scraping/scraper/ && scrapy crawl flipkart -o ./data.json"
        os.system(command)

        path = os.path.join(os.path.dirname(__file__), 'scraper/data.json')
        output = open(path, "r")
        try:
            result = json.loads(output.read())[0]
        except:
            result =json.loads((output.read()))
        output.close()

    else:
        return "Invalid URL"

    # checking from DB
    # Generating Authentication token
    BASE_URL = Credentials.api_base_url
    # Auth.
    url = BASE_URL + "/user/login"
    response = requests.post(url, json={
        "userid": username,
        "password": password
    })

    auth_response = response.json()
    if auth_response['status'] == 'fail':
        return { 'error' : 'Connecting to DB : '+str(auth_response)}

    header = {'Authorization': 'Bearer ' + auth_response['token'], 'content-type': "application/json"}

    if url_input.find('amazon') > -1:
        url_by_prod_id = BASE_URL + '/product?stores.storeProductId=' + result['stores'][0]['storeProductId']
        res_prod_id = requests.get(url_by_prod_id, headers=header)
        data = res_prod_id.json()

        if data != []:
            if result['stores'][0]['storeProductId'] == data[0]['stores'][0]['storeProductId']:
                # return {'from': 'DB', 'data': data}
                return data
            else:
                payload = json.dumps(result)
                res = requests.post(BASE_URL + '/product/', data=payload, headers=header)
                return res.json()
        else:
            payload = json.dumps(result)
            res = requests.post(BASE_URL + '/product/', data=payload, headers=header)
            return res.json()
    elif url_input.find('flipkart') > -1:
        # print(result)
        url_by_prod_id = BASE_URL + '/product?stores.storeProductId=' + result['stores']['storeProductId']
        res_prod_id = requests.get(url_by_prod_id, headers=header)
        data = res_prod_id.json()

        if data != []:
            # if result['stores']['storeProductId'] == data[0]['stores'][0]['storeProductId']:
            #     # return {'from': 'DB', 'data': data}
            #     return data
            # else:
            #     payload = json.dumps(result)
            #     res = requests.post(BASE_URL + '/product/', data=payload, headers=header)
            #     return res.json()

            try:
                model_numb = result['stores']['storeAdditionalDetails']['Model Number']  # getting model number from payload
            except:
                model_numb = []
            if model_numb != []:  # checking model number is not empty
                url2 = 'https://apistaging.revmeup.in/api/v1/product?stores.storeTechnicalDetails.Item model number=' + model_numb  # queriying db with model number
                l = requests.get(url2, headers=header)
                product_details = l.json()

                if product_details == []:  # checking if product details  null
                    url2 = 'https://apistaging.revmeup.in/api/v1/product?stores.storeTechnicalDetails.Model number=' + model_numb
                    l = requests.get(url2, headers=header)
                    return data

                if product_details != []:
                    flipkart_store = result['stores']

                    product_details[0]['stores'].append(flipkart_store)
                    patch_url = 'https://apistaging.revmeup.in/api/v1/product/' + product_details[0]['product_id']
                    l = requests.patch(patch_url, data=json.dumps(product_details[0]), headers=header)

                    url_2 = 'https://apistaging.revmeup.in/api/v1/product?stores.storeTechnicalDetails.Model number=' + model_numb
                    l = requests.get(url2, headers=header)
                    return data
        else:
            payload = json.dumps(result)
            res = requests.post(BASE_URL + '/product/', data=payload, headers=header)
            return res.json()
    else:
        return "Invalid URL"


