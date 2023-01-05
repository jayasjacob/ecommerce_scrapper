import datetime
import re
import string
import random
import scrapy
from ..items import AmazonScraperItem
# from ..hotdeals_creation import Hotdeals
# from ..add_Alert import addAlert
import pprint
import requests
import json
from ..config import *
import threading

from scrapy import signals
from scrapy.mail import MailSender
import smtplib
from ..smtp import SendMail
from getpass import getpass
import logging

# ************ Logging to external file****************
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
logger.addHandler(logging.FileHandler('status.log', 'a'))
print = logger.info
# ******************End of logging essentials*******************
BASE_URL = Credentials.api_base_url
# Auth.
url = BASE_URL + "/user/login"
response = requests.post(url, json={
    "userid": Credentials.userid,
    "password": Credentials.password
})
a = response.json()
tok = a['token']


class Scraper(scrapy.Spider):
    count_item_scraped = 0
    name = "amazon_scraper"
    # number of pages we want to scrape
    no_of_pages = 25
    # setting header for our scraper
    headers = {'referer': 'http://www.google.com',
               'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
               # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"
               }
    with open("./data/keywords.txt", "r") as myfile:
        keyword = myfile.readlines()
    content = [x.strip().replace(" ", "+") for x in keyword]
    items = content

    def start_requests(self):
        # starting urls for scraping with respective items
        urls = []
        for item in self.items:
            urls.append("https://www.amazon.in/Godrej-Refrigerator-EON-260C-RCIF/dp/B08CS43KGC/ref=asc_df_B08CS43KGC/?tag=googleshopmob-21&linkCode=df0&hvadid=397306049226&hvpos=&hvnetw=g&hvrand=12651131816019563181&hvpone=&hvptwo=&hvqmt=&hvdev=m&hvdvcmdl=&hvlocint=&hvlocphy=9062122&hvtargid=pla-932956226526&psc=1&ext_vrnc=hi")

        for url in urls: yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    # getting links of each indiviual product and then requesting it for more details
    def parse(self, response):
        self.no_of_pages -= 1

        prod_urls = response.xpath("//a[@class='a-link-normal a-text-normal']").xpath("@href").getall()

        # requesting further for individual each product
        for elec in prod_urls:
            elec = elec.split("&qid=")[0]
            # elec = elec.split("ref=")[0]
            final_url = response.urljoin(elec)
            DEFAULT_REQUEST_HEADERS = {
                'referer': 'http://www.google.com',
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
            }
            yield scrapy.Request(url=final_url, callback=self.parse_prod, headers=DEFAULT_REQUEST_HEADERS)

        if (self.no_of_pages > 0):
            next_page_url = response.xpath("//ul[@class='a-pagination']/li[@class='a-last']/a").xpath("@href").get()
            final_url = "https://www.amazon.in/Godrej-Refrigerator-EON-260C-RCIF/dp/B08CS43KGC/ref=asc_df_B08CS43KGC/?tag=googleshopmob-21&linkCode=df0&hvadid=397306049226&hvpos=&hvnetw=g&hvrand=12651131816019563181&hvpone=&hvptwo=&hvqmt=&hvdev=m&hvdvcmdl=&hvlocint=&hvlocphy=9062122&hvtargid=pla-932956226526&psc=1&ext_vrnc=hi"

            DEFAULT_REQUEST_HEADERS = {
                'referer': 'http://www.google.com',
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
            }
            yield scrapy.Request(url=final_url, callback=self.parse, headers=DEFAULT_REQUEST_HEADERS)

    def parse_prod(self, response):  # parsing the product detail by usinf xpath selectors
        count_exception = 0
        Scraper.count_item_scraped = 0
        counter_request_success = 0
        counter_request_faliure = 0
        product_name = response.xpath("//span[@id='productTitle']//text()").get() or response.xpath(
            "//h1[@id='title']//text()").get()
        product_name = str(product_name)
        try:
            product_name = product_name.strip()
        except:
            pass

        # brand = response.xpath("//a[@id='bylineInfo']//text()").get() or "not specified"

        # Adding Rating
        rating = response.xpath("//div[@id='averageCustomerReviews_feature_div']").xpath(
            "//span[@class='a-icon-alt']//text()").get()

        # Adding Reviews
        reviews = response.xpath(
            "//div[@class='a-expander-content reviewText review-text-content a-expander-partial-collapse-content']/span//text()").getall()

        # Adding Price
        try:
            price = response.xpath("//span[@id='priceblock_ourprice']//text()") or response.xpath(
                "//span[@id='priceblock_dealprice']//text()")
        except:
            price = "0"

        # Adding technical details
        technical_details = response.css('#productDetails_techSpec_section_1 .a-size-base').css('::text').extract()
        technical_details = [re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*]", "", file) for file in technical_details]
        technical_details = list(map(lambda s: s.strip(), technical_details))
        technical_details = dict(zip(technical_details[::2], technical_details[1::2]))
        for k, v in dict(technical_details).items():
            if v == '' or k == '':
                del technical_details[k]

        # Adding additional details
        additional_details = response.css(
            '#productDetails_detailBullets_sections1 td , #productDetails_detailBullets_sections1 .prodDetSectionEntry').css(
            '::text').extract()
        additional_details = [re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*]", "", file) for file in additional_details]
        additional_details = list(map(lambda s: s.strip(), additional_details))
        additional_details = dict(zip(additional_details[::2], additional_details[1::2]))
        for k, v in dict(additional_details).items():
            if v == '' or k == '':
                del additional_details[k]
        # i = 0
        # new_dict = {}
        # for k, v in additional_details.items():
        #     if i < 2:
        #         new_dict[v] = k
        #         i += 1
        #     else:
        #         new_dict[k] = v
        # additional_details = new_dict

        # Adding MRP
        MRP = response.css('#price .a-text-strike').css('::text').extract()

        # Adding Colors "TODO"
        # colour = response.xpath("//div[@id='variation_color_name']/div/span[@class='selection']//text()").get() or "not defined"

        # Adding Instock Status
        instock = response.xpath("//div[@id='availability']").xpath(
            "//span[@class='a-size-medium a-color-success']//text()").get() or "Out Stock"
        instock = instock.strip()
        # instock = instock.strip() == "In stock."

        # Adding Description
        description_raw = response.xpath(
            "//div[@id='featurebullets_feature_div']//span[@class='a-list-item']//text()").getall()
        description = ''
        for description_temp in description_raw:
            description += description_temp.strip() + ', '
        description = description[:-2]

        # Adding Brand Name "TODO"
        try:
            brand_name = technical_details["Brand"]
        except:
            try:
                brand_name = technical_details["Manufacturer"]
            except:
                count_exception += 1
                brand_name = "Not Available"

        # ADDING PHOTOS
        photos = response.css('#altImages').css('::attr(src)').extract()
        for i in range(len(photos)):
            photos[i] = photos[i].rsplit('.', 2)[0] + "." + photos[i].split(".")[-1]

        # Adding Store logo
        store_logo = "https://i.pinimg.com/564x/42/a7/86/42a7861bb1a403af534b18986ab4e198.jpg"

        # Adding Timestamp
        timeStamp = ""

        if len(price) > 1:
            price = price[1].get()
        elif len(price) == 1:
            price = price[0].get()
        else:
            price = price.get()
        asin = response.xpath(
            "//*[@id='prodDetails']/div[2]/div[2]/div[1]/div[2]/div/div/table/tbody/tr[1]/td[2]//text()").extract() or response.xpath(
            "//*[@id='prodDetails']/div/div[2]/div[1]/div[2]/div/div/table/tbody/tr[1]/td[2]//text()").extract()
        for i in asin:
            asin = ''
            asin += i

        # setting categories and sub categories
        iurl = response.url

        # category =  response.css(".a-breadcrumb-divider+ li .a-color-tertiary").css("::text").extract()
        # try: category = category[0].strip()
        # except: category = "Electronics"
        # subcategory =  response.css(".a-breadcrumb-divider+ li .a-color-tertiary").css("::text").extract()[1].strip()
        # try: subcategory = subcategory[0].strip()
        # except: subcategory = iurl.split("keywords=")[1]

        data = response.xpath('//*[@id="wayfinding-breadcrumbs_container"]//text()').extract()
        data = [re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*›]", "", file) for file in data]
        data = list(map(lambda s: s.strip(), data))
        for item in data:
            if item == " ''" or item == "":
                data.remove(item)
        subcategory = "None"
        try:
            subcategory = data[1]
            category = data[0]
        except:
            count_exception += 1
            subcategory = iurl.split("keywords=")[1].replace("+", " ")
            category = "Electronics"

        trim = re.compile(r'[^\d.,]+')
        MRP = str(MRP)
        MRP = trim.sub('', MRP)
        MRP = MRP.replace(".00", "").replace(",", "")

        price = str(price)
        price = trim.sub(' ', price)
        price = price.replace(".00", "").replace(",", "")
        try:
            price = price[1:]
        except:
            price = str(price)
            count_exception += 1
        # if price == "" or price == '': price = "0"
        try:
            MRP = MRP[1:]
        except:
            MRP = MRP
            count_exception += 1
        # CREATING STORES FOR PAYLOAD
        # storeProductId = iurl.split("/dp/")[1].split("/")[0]

        storeProductId = response.css('#productDetails_detailBullets_sections1 tr:nth-child(1) td').css(
            '::text').extract()
        try:
            storeProductId = storeProductId[0].strip()
        except:
            storeProductId = storeProductId.strip()

        if storeProductId == None:
            try:
                storeProductId = iurl.split("/dp/")[1].split("/")[0].split('?')[0]
            except:
                storeProductId = iurl.split("/dp/")[1].split("/")

        stores = [{
            "storeProductId": storeProductId,
            "storeLink": iurl,
            "storeName": "amazon",
            "storePrice": price,
            "store_mrp": MRP,
            "store_logo": store_logo,
            "storeDescription": description,
            "reviews": reviews,
            "rating": rating,
            "instock": instock,
            "storeTechnicalDetails": technical_details,
            "storeAdditionalDetails": additional_details
        }]

        # adding unique product id
        product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 15))  # random 15 len alphanumeric id

        # payload -> Parsed
        item = {
            "product_name": product_name,
            "product_id": product_id,
            "timestamp": timeStamp,
            "brand_name": brand_name,
            "stores": stores,
            "category": category,
            "subcategory": subcategory,
            "description": description,
            "photos": photos,
        }
        # -------------------- API CALL2 ( PROD NAME QUERY POST AND PATCH) ----------------------------
        # Adding token for API requests
        product_name = str(product_name)
        print('item')
        print(item)
        # -------------------- CHECKING FOR RENEWED PRODUCTS----------------------------
        if "(Renewed)" in product_name:
            if stores[0]['storePrice'] != '' and stores[0]['store_mrp'] != '' and stores[0][
                'storeAdditionalDetails'] != {} and stores[0]['storeTechnicalDetails'] != {}:
                header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
                # Query for the parsed product to the api

                # prod_info = res_prod_id.json()
                # pprint.pprint(prod_info)

                # Query for the parsed product to the api
                url_by_prod_id = BASE_URL + '/product_renewed?stores.storeProductId=' + item['stores'][0][
                    'storeProductId']
                res_prod_id = requests.get(url_by_prod_id, headers=header)
                if res_prod_id.status_code == 200:
                    counter_request_success += 1
                else:
                    counter_request_faliure += 1

                # pprint.pprint(res_prod_name.json())
                # pprint.pprint(res_prod_id.json())

                # Getting product data if exists

                # -------------------API CALL2 ENDS------------------------------

                # ----------------------------- API CALL Starts -----------------------------
                # Adding token for API requests
                # pprint.pprint(prod_info)
                prod_info = res_prod_id.json()
                print("id")
                print(prod_info)
                if prod_info != []:
                    db_price = prod_info[0]['stores'][0]['storePrice'].replace(".00", "").replace(",", "")
                    scraped_price = item['stores'][0]['storePrice'].replace(".00", "").replace(",", "")

                    if scraped_price != None and scraped_price != '' and int(scraped_price) > 0 and int(
                            db_price) != int(
                        scraped_price) \
                            or prod_info[0]["product_name"] != product_name \
                            or prod_info[0]["description"] != description \
                            or len(prod_info[0]["photos"]) < len(photos) \
                            or prod_info[0]["stores"][0]["storeProductId"] != item['stores'][0]["storeProductId"] \
                            or prod_info[0]["stores"][0]["storeDescription"] != item['stores'][0]["storeDescription"] \
                            or prod_info[0]["stores"][0]["rating"] != item['stores'][0]["rating"] \
                            or prod_info[0]["stores"][0]["instock"] != item['stores'][0]["instock"] \
                            or prod_info[0]["stores"][0]["storeTechnicalDetails"] != item['stores'][0][
                        "storeTechnicalDetails"] \
                            or prod_info[0]["stores"][0]["storeAdditionalDetails"] != item['stores'][0][
                        "storeAdditionalDetails"] \
                            or prod_info[0]['stores'][0]['storePrice'] == '' or prod_info[0]['stores'][0][
                        'storePrice'] == ' ' or \
                            prod_info[0]['stores'][0]['storePrice'] == None or prod_info[0]["stores"][0][
                        "storePrice"] != \
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
                            BASE_URL + '/product_renewed' + '/' + prod_info[0]['product_id'],
                            data=json.dumps(payload2), headers=header)
                        if res.status_code == 200:
                            counter_request_success += 1

                        else:
                            counter_request_faliure += 1

                            # ............          calculating values for hotdeals payload........................
                            # hotdeals_payload = {}
                            # if scraped_price != '' and db_price != '':
                            #     old_price = int(db_price)
                            #     price = int(scraped_price)
                            #     offer_percentage = (old_price - price) * 100 / old_price
                            #
                            #     # ---------- Price notification to the Firebase database
                            #     if old_price > price:
                            #         addAlert(prod_info[0], db_price, 0)
                            #
                            #     # .....        if offer> 5% , we add to hotdeals in revme db..............
                            #     if offer_percentage > 5 and old_price > price:
                            #         hotDeals = Hotdeals()
                            #         hotDeals.hotdeals_creation(item=item, old_price=old_price, header=header, position=0,
                            #                                    offer_percentage=offer_percentage)

                            print('updated / Res:' + res.__str__())
                    else:
                        print("Already present")

                elif res_prod_id.json() == []:
                    print("else if")

                    if item['product_name'] != '' and item['product_id'] != '' and item['stores'] != [] and item[
                        'stores'] != '' and item['stores'][0]["storeProductId"] != '' and item['stores'][0][
                        "storeLink"] != '' and item['stores'][0]["storePrice"] != '' and item['category'] != '' and \
                            item[
                                'subcategory'] != '' and item["description"] != '' and item["description"] != [] and \
                            item[
                                "photos"] != None and item["photos"] != [] and item['photos'][0] != '':
                        if item['stores'][0]['storeName'] == '' or item['stores'][0]['storeName'] == None:
                            item['stores'][0]['storeName'] = 'amazon'

                        if '&tag=' not in item['stores'][0]['storeLink']:
                            item['stores'][0]['storeLink'] = item['stores'][0]['storeLink'] + "&tag=revmeup-21"
                        else:
                            item['stores'][0]['storeLink'] = item['stores'][0]['storeLink'].split('&tag=')[
                                                                 0] + "&tag=revmeup-21"
                        payload = json.dumps(item)
                        # pprint.pprint(payload)
                        # print("Base URL" + BASE_URL)
                        # print("CREATE NEW PROD_ID:" + str(item[0]['product_id']))
                        res = requests.post(BASE_URL + '/product_renewed'
                                            , data=payload,
                                            headers=header)

                        print('Posted / Res:' + res.__str__())
                        if res.status_code == 200:
                            counter_request_success += 1
                        else:
                            counter_request_faliure += 1

        # elif "(CERTIFIED REFURBISHED)" in product_name:
        #     if stores[0]['storePrice'] != '' and stores[0]['store_mrp'] != '' and stores[0][
        #         'storeAdditionalDetails'] != {} and stores[0]['storeTechnicalDetails'] != {}:
        #         header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
        #         # Query for the parsed product to the api
        #
        #         # prod_info = res_prod_id.json()
        #         # pprint.pprint(prod_info)
        #
        #         # Query for the parsed product to the api
        #         url_by_prod_id = BASE_URL + '/product_renewed?stores.storeProductId=' + item['stores'][0]['storeProductId']
        #         res_prod_id = requests.get(url_by_prod_id, headers=header)
        #         if res_prod_id.status_code == 200:
        #             counter_request_success += 1
        #         else:
        #             counter_request_faliure += 1
        #
        #         # pprint.pprint(res_prod_name.json())
        #         # pprint.pprint(res_prod_id.json())
        #
        #         # Getting product data if exists
        #
        #         # -------------------API CALL2 ENDS------------------------------
        #
        #         # ----------------------------- API CALL Starts -----------------------------
        #         # Adding token for API requests
        #         # pprint.pprint(prod_info)
        #         prod_info = res_prod_id.json()
        #         print("id")
        #         print(prod_info)
        #         if prod_info != []:
        #             db_price = prod_info[0]['stores'][0]['storePrice'].replace(".00", "").replace(",", "")
        #             scraped_price = item['stores'][0]['storePrice'].replace(".00", "").replace(",", "")
        #
        #             if scraped_price != None and scraped_price != '' and int(scraped_price) > 0 and int(
        #                     db_price) != int(
        #                     scraped_price) \
        #                     or prod_info[0]["product_name"] != product_name \
        #                     or prod_info[0]["description"] != description \
        #                     or len(prod_info[0]["photos"]) < len(photos) \
        #                     or prod_info[0]["stores"][0]["storeProductId"] != item['stores'][0]["storeProductId"] \
        #                     or prod_info[0]["stores"][0]["storeDescription"] != item['stores'][0]["storeDescription"] \
        #                     or prod_info[0]["stores"][0]["rating"] != item['stores'][0]["rating"] \
        #                     or prod_info[0]["stores"][0]["instock"] != item['stores'][0]["instock"] \
        #                     or prod_info[0]["stores"][0]["storeTechnicalDetails"] != item['stores'][0][
        #                 "storeTechnicalDetails"] \
        #                     or prod_info[0]["stores"][0]["storeAdditionalDetails"] != item['stores'][0][
        #                 "storeAdditionalDetails"] \
        #                     or prod_info[0]['stores'][0]['storePrice'] == '' or prod_info[0]['stores'][0][
        #                 'storePrice'] == ' ' or \
        #                     prod_info[0]['stores'][0]['storePrice'] == None or prod_info[0]["stores"][0][
        #                 "storePrice"] != \
        #                     item['stores'][0]["storePrice"] \
        #                     or prod_info[0]['stores'][0]['store_mrp'] == '' or prod_info[0]['stores'][0][
        #                 'store_mrp'] == ' ' or \
        #                     prod_info[0]['stores'][0]['store_mrp'] == None or prod_info[0]["stores"][0]["store_mrp"] != \
        #                     item['stores'][0]["store_mrp"]:
        #
        #                 prod_info[0]['stores'][0]['storePrice'] = scraped_price
        #                 payload2 = item
        #                 payload2["product_id"] = prod_info[0]['product_id']
        #                 # pprint.pprint(payload2)
        #                 # print("Base URL" + BASE_URL)
        #                 # print("PROD_ID:" + str(prod_info[0]['product_id']))
        #                 res = requests.patch(
        #                     BASE_URL + '/product_renewed' + '/' + prod_info[0]['product_id'],
        #                     data=json.dumps(payload2), headers=header)
        #                 if res.status_code == 200:
        #                     counter_request_success += 1
        #
        #                 else:
        #                     counter_request_faliure += 1
        #
        #                 # ............          calculating values for hotdeals payload........................
        #                 hotdeals_payload = {}
        #                 if scraped_price != '' and db_price != '':
        #                     old_price = int(db_price)
        #                     price = int(scraped_price)
        #                     offer_percentage = (old_price - price) * 100 / old_price
        #
        #                     # ---------- Price notification to the Firebase database
        #                     if old_price > price:
        #                         addAlert(prod_info[0], db_price, 0)
        #
        #                     # .....        if offer> 5% , we add to hotdeals in revme db..............
        #                     if offer_percentage > 5 and old_price > price:
        #                         hotDeals = Hotdeals()
        #                         hotDeals.hotdeals_creation(item=item, old_price=old_price, header=header, position=0,
        #                                                    offer_percentage=offer_percentage)
        #
        #                     print('updated / Res:' + res.__str__())
        #             else:
        #                 print("Already present")
        #
        #         elif res_prod_id.json() == []:
        #             print("else if")
        #
        #             if item['product_name'] != '' and item['product_id'] != '' and item['stores'] != [] and item[
        #                 'stores'] != '' and item['stores'][0]["storeProductId"] != '' and item['stores'][0][
        #                 "storeLink"] != '' and item['stores'][0]["storePrice"] != '' and item['category'] != '' and \
        #                     item[
        #                         'subcategory'] != '' and item["description"] != '' and item["description"] != [] and \
        #                     item[
        #                         "photos"] != None and item["photos"] != [] and item['photos'][0] != '':
        #                 if item['stores'][0]['storeName'] == '' or item['stores'][0]['storeName'] == None:
        #                     item['stores'][0]['storeName'] = 'amazon'
        #
        #                 if '&tag=' not in item['stores'][0]['storeLink']:
        #                     item['stores'][0]['storeLink'] = item['stores'][0]['storeLink'] + "&tag=revmeup-21"
        #                 else:
        #                     item['stores'][0]['storeLink'] = item['stores'][0]['storeLink'].split('&tag=')[
        #                                                          0] + "&tag=revmeup-21"
        #                 payload = json.dumps(item)
        #                 # pprint.pprint(payload)
        #                 # print("Base URL" + BASE_URL)
        #                 # print("CREATE NEW PROD_ID:" + str(item[0]['product_id']))
        #                 res = requests.post(BASE_URL + '/product_renewed'
        #                                     , data=payload,
        #                                     headers=header)
        #
        #                 print('Posted / Res:' + res.__str__())
        #                 if res.status_code == 200:
        #                     counter_request_success += 1
        #                 else:
        #                     counter_request_faliure += 1

        else:
            print('item')
            print(item)

            if stores[0]['storePrice'] != '' and stores[0]['store_mrp'] != '' and stores[0][
                'storeAdditionalDetails'] != {} and stores[0]['storeTechnicalDetails'] != {}:
                header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
                # Query for the parsed product to the api

                # prod_info = res_prod_id.json()
                # pprint.pprint(prod_info)

                # Query for the parsed product to the api
                url_by_prod_id = BASE_URL + '/product?stores.storeProductId=' + item['stores'][0]['storeProductId']
                res_prod_id = requests.get(url_by_prod_id, headers=header)
                if res_prod_id.status_code == 200:
                    counter_request_success += 1
                else:
                    counter_request_faliure += 1

                # pprint.pprint(res_prod_name.json())
                # pprint.pprint(res_prod_id.json())

                # Getting product data if exists

                # -------------------API CALL2 ENDS------------------------------

                # ----------------------------- API CALL Starts -----------------------------
                # Adding token for API requests
                # pprint.pprint(prod_info)
                prod_info = res_prod_id.json()
                print("id")
                print(prod_info)
                if prod_info != []:
                    db_price = prod_info[0]['stores'][0]['storePrice'].replace(".00", "").replace(",", "")
                    scraped_price = item['stores'][0]['storePrice'].replace(".00", "").replace(",", "")

                    if scraped_price != None and scraped_price != '' and int(scraped_price) > 0 and int(
                            db_price) != int(
                        scraped_price) \
                            or prod_info[0]["product_name"] != product_name \
                            or prod_info[0]["description"] != description \
                            or len(prod_info[0]["photos"]) < len(photos) \
                            or prod_info[0]["stores"][0]["storeProductId"] != item['stores'][0]["storeProductId"] \
                            or prod_info[0]["stores"][0]["storeDescription"] != item['stores'][0]["storeDescription"] \
                            or prod_info[0]["stores"][0]["rating"] != item['stores'][0]["rating"] \
                            or prod_info[0]["stores"][0]["instock"] != item['stores'][0]["instock"] \
                            or prod_info[0]["stores"][0]["storeTechnicalDetails"] != item['stores'][0][
                        "storeTechnicalDetails"] \
                            or prod_info[0]["stores"][0]["storeAdditionalDetails"] != item['stores'][0][
                        "storeAdditionalDetails"] \
                            or prod_info[0]['stores'][0]['storePrice'] == '' or prod_info[0]['stores'][0][
                        'storePrice'] == ' ' or \
                            prod_info[0]['stores'][0]['storePrice'] == None or prod_info[0]["stores"][0][
                        "storePrice"] != \
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
                            BASE_URL + '/product' + '/' + prod_info[0]['product_id'],
                            data=json.dumps(payload2), headers=header)
                        if res.status_code == 200:
                            counter_request_success += 1

                        else:
                            counter_request_faliure += 1

                        # ............          calculating values for hotdeals payload........................
                        # hotdeals_payload = {}
                        # if scraped_price != '' and db_price != '':
                        #     old_price = int(db_price)
                        #     price = int(scraped_price)
                        #     offer_percentage = (old_price - price) * 100 / old_price
                        #
                        #     # ---------- Price notification to the Firebase database
                        #     if old_price > price:
                        #         addAlert(prod_info[0], db_price, 0)
                        #
                        #     # .....        if offer> 5% , we add to hotdeals in revme db..............
                        #     if offer_percentage > 5 and old_price > price:
                        #         hotDeals = Hotdeals()
                        #         hotDeals.hotdeals_creation(item=item, old_price=old_price, header=header, position=0,
                        #                                    offer_percentage=offer_percentage)
                        #
                        #     print('updated / Res:' + res.__str__())
                    else:
                        print("Already present")

                elif res_prod_id.json() == []:
                    print("else if")

                    if item['product_name'] != '' and item['product_id'] != '' and item['stores'] != [] and item[
                        'stores'] != '' and item['stores'][0]["storeProductId"] != '' and item['stores'][0][
                        "storeLink"] != '' and item['stores'][0]["storePrice"] != '' and item['category'] != '' and \
                            item[
                                'subcategory'] != '' and item["description"] != '' and item["description"] != [] and \
                            item[
                                "photos"] != None and item["photos"] != [] and item['photos'][0] != '':
                        if item['stores'][0]['storeName'] == '' or item['stores'][0]['storeName'] == None:
                            item['stores'][0]['storeName'] = 'amazon'

                        if '&tag=' not in item['stores'][0]['storeLink']:
                            item['stores'][0]['storeLink'] = item['stores'][0]['storeLink'] + "&tag=revmeup-21"
                        else:
                            item['stores'][0]['storeLink'] = item['stores'][0]['storeLink'].split('&tag=')[
                                                                 0] + "&tag=revmeup-21"
                        payload = json.dumps(item)
                        # pprint.pprint(payload)
                        # print("Base URL" + BASE_URL)
                        # print("CREATE NEW PROD_ID:" + str(item[0]['product_id']))
                        res = requests.post(BASE_URL + '/product'
                                            , data=payload,
                                            headers=header)

                        print('Posted / Res:' + res.__str__())
                        if res.status_code == 200:
                            counter_request_success += 1
                        else:
                            counter_request_faliure += 1

                # ----------------------------- API CALL ENDS -----------------------------
                # Dumping Data to Local JSON
                pp = AmazonScraperItem(product_name=product_name,
                                       product_id=product_id,
                                       timestamp=timeStamp,
                                       brand_name=brand_name,
                                       stores=stores,
                                       category=category,
                                       subcategory=subcategory,
                                       description=description,
                                       photos=photos)
                yield pp
                with open('./data/SuccessProducts.json', 'a') as outfile_1:
                    json.dump(item, outfile_1, ensure_ascii=False, indent=4)

            else:
                with open('./data/ErrorProducts.json', 'a') as outfile:
                    json.dump(item, outfile, ensure_ascii=False, indent=4)

        # ******** Logging Counter****************
        # print("Exception occured")
        # print(count_exception)
        # print(" Request Success Count")
        # print(counter_request_success)
        # print("Request failures")
        # print(counter_request_faliure)
