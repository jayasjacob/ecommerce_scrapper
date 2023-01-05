import datetime
import re
import string
import random
import scrapy
from ..items import Product
from ..smtp import SendMail
from ..hotdeals_creation import Hotdeals
from ..add_Alert import addAlert
from getpass import getpass
# EMAIL = input("please enter your email :")
# PASS = getpass("please enter your password :")

# Authentication API call-
import json
import requests
from ..config import *
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
prod_info = l.json()
# storing the product data into "DB_prod.json" file
with open('./data/DB_prod.json', 'w') as outfile:
    json.dump(prod_info, outfile, ensure_ascii=False, indent=4)


class Scraper(scrapy.Spider):
    name = "amazon_scraper"
    # setting header for our scraper
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
               # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"
               }

    def start_requests(self):
        # creating dictionary for storing parsed data from revmeup database      { productURL(key) : { Whole Product Node } }
        Item = {}
        # reading database
        product_file = open("./data/DB_prod.json", 'r')
        jsondata = product_file.read()
        obj = json.loads(jsondata)
        # parsing data for amazon
        for val in obj:
            try:
                print('product id : ' + val['product_id'])
                storeLink = val['stores'][0]['storeLink']
                Item[storeLink] = val
            except:
                pass

        # Fetching Data from Amazon URLs
        for url in Item: yield scrapy.Request(url=url, callback=self.parse_amazon,
                                              meta={'product_amazon_current_node': Item[url]}, headers=self.headers)

        # for url in Item2: yield scrapy.Request(url=url, callback=self.parse_flipkart, meta={'product_flipkart' : Item2[url]}, headers=self.headers)

    def parse_amazon(self, response):
        # Getting Data From Website
        product_name = response.xpath("//span[@id='productTitle']//text()").get() or response.xpath("//h1[@id='title']//text()").get()
        product_name = str(product_name)
        try:product_name = product_name.strip()
        except:pass
        # Adding Rating
        rating = response.xpath("//div[@id='averageCustomerReviews_feature_div']").xpath("//span[@class='a-icon-alt']//text()").get()
        # Adding Reviews
        reviews = response.xpath("//div[@class='a-expander-content reviewText review-text-content a-expander-partial-collapse-content']/span//text()").getall()
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
        # Adding Colors "TODO"
        # colour = response.xpath("//div[@id='variation_color_name']/div/span[@class='selection']//text()").get() or "not defined"
        # Adding Instock Status
        instock = response.xpath("//div[@id='availability']").xpath("//span[@class='a-size-medium a-color-success']//text()").get() or "Out Stock"
        instock = instock.strip()
        # instock = instock.strip() == "In stock."
        # Adding Description
        description_raw = response.xpath("//div[@id='featurebullets_feature_div']//span[@class='a-list-item']//text()").getall()
        description = ''
        for description_temp in description_raw:
            description += description_temp.strip() + ', '
        description = description[:-2]
        # Adding Brand Name
        try:
            brand_name = technical_details["Brand"]
        except:
            try:
                brand_name = technical_details["Manufacturer"]
            except:
                brand_name = "Not Available"
        # ADDING PHOTOS
        photos = response.css('#altImages').css('::attr(src)').extract()
        for i in range(len(photos)):
            photos[i] = photos[i].rsplit('.', 2)[0] + "." + photos[i].split(".")[-1]
        # Adding Store logo
        store_logo = "https://i.pinimg.com/564x/42/a7/86/42a7861bb1a403af534b18986ab4e198.jpg"
        # Adding Timestamp
        timeStamp = ""
        asin = response.xpath("//*[@id='prodDetails']/div[2]/div[2]/div[1]/div[2]/div/div/table/tbody/tr[1]/td[2]//text()").extract() or response.xpath("//*[@id='prodDetails']/div/div[2]/div[1]/div[2]/div/div/table/tbody/tr[1]/td[2]//text()").extract()
        for i in asin:
            asin = ''
            asin += i
        # setting categories and sub categories
        iurl = response.url
        category = 'Electronics'
        subcategory = "others"
        try:
            subcategory = response.meta.get('product_amazon_current_node')["subcategory"]
        except:
            subcategory = "others"
        data = response.xpath('//*[@id="wayfinding-breadcrumbs_container"]//text()').extract()
        data = [re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*›]", "", file) for file in data]
        data = list(map(lambda s: s.strip(), data))
        for item in data:
            if item == " ''" or item == "":
                data.remove(item)
        if "keywords=" in iurl:
            subcategory = iurl.split("keywords=")[1].split("&qid=")[0].replace('+', ' ')
        try:
            subcategory = data[1]
            category = data[0]
        except:
            subcategory = iurl.split("keywords=")[1].replace("+", " ")
            category = "Electronics"



        # Adding Current MRP
        trim = re.compile(r'[^\d.,]+')
        MRP = response.css('#price .a-text-strike').css('::text').extract()
        MRP = str(MRP)
        MRP = trim.sub('', MRP)
        MRP = MRP.replace(".00", "").replace(",", "")
        # Adding Current Price
        price = response.xpath("//span[@id='priceblock_ourprice']//text()") or response.xpath("//span[@id='priceblock_dealprice']//text()")
        if len(price) > 1:
            price = price[1].get()
        elif len(price) == 1:
            price = price[0].get()
        else:
            price = price.get()
        price = str(price)
        price = trim.sub(' ', price)
        price = price.replace(".00", "").replace(",", "").replace(" ", "").replace("$", "").replace("₹", "")
        price = price.replace(".00", "").replace(",", "")
        try:
            price = price[1:]
        except:
            price = str(price)
        try:
            MRP = MRP[1:]
        except:
            MRP = MRP
        # CREATING STORES FOR PAYLOAD
        if "/dp/" in iurl:
            storeProductID = iurl.split("/dp/")[1].split("/ref")[0]
        else:
            if response.meta.get('product_amazon_current_node')['stores'][0]["storeProductId"] != None or response.meta.get('product_amazon_current_node')['stores'][0]["storeProductId"] != '':
                storeProductID = response.meta.get('product_amazon_current_node')['stores'][0]["storeProductId"]
            else:
                try:storeProductID = additional_details["ASIN"]
                except: storeProductID =  iurl.split("/dp/")[1].split("/")[0]
        amazonStore = {
            "storeProductId": storeProductID,
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
        }
        # current_payload = {
        #     "product_name": product_name,
        #     "product_id": response.meta.get('product_amazon_current_node')["product_id"],
        #     "timestamp": timeStamp,
        #     "brand_name": brand_name,
        #     "stores": stores,
        #     "category": category,
        #     "subcategory": subcategory,
        #     "description": description,
        #     "photos": photos,
        # }
        # getting oldPrice and StoreProdID
        current_node = (response.meta.get('product_amazon_current_node'))

        product_id = current_node["product_id"]
        old_price = current_node['stores'][0]['storePrice']
        NEW_price = amazonStore["storePrice"].replace(".00", "").replace(",", "")
        old_price = old_price.replace(".00", "").replace(",", "")

        stores_current_node = current_node["stores"]
        stores_current_node[0] = amazonStore



        hotdeals_payload = {}
        # Comp. opld and new prices
        # old_price = int(old_price)

        # NEW_price = current_payload["stores"][0]["storePrice"]


        if old_price == '' or old_price ==None or old_price==' ' \
                or NEW_price == '' or NEW_price ==None or NEW_price==' ' \
                or int(old_price) != int(NEW_price) \
                or current_node["product_name"] != product_name\
                or current_node["brand_name"] != brand_name \
                or current_node["description"] != description\
                or len(current_node["photos"]) < len(photos) \
                or current_node["stores"][0]["storeProductId"] != amazonStore["storeProductId"] \
                or current_node["stores"][0]["storeDescription"] != amazonStore["storeDescription"]\
                or current_node["stores"][0]["rating"] != amazonStore["rating"] \
                or current_node["stores"][0]["instock"] != amazonStore["instock"] \
                or current_node["stores"][0]["storeTechnicalDetails"] != amazonStore["storeTechnicalDetails"]\
                or current_node["stores"][0]["storeAdditionalDetails"] != amazonStore["storeAdditionalDetails"]\
                or current_node['stores'][0]['storePrice'] == '' or current_node['stores'][0]['storePrice'] == ' ' or current_node['stores'][0]['storePrice'] == None or current_node["stores"][0]["storePrice"]!= amazonStore["storePrice"]\
                or current_node['stores'][0]['store_mrp'] == '' or current_node['stores'][0]['store_mrp'] == ' ' or current_node['stores'][0]['store_mrp'] == None or current_node["stores"][0]["store_mrp"]!= amazonStore["store_mrp"] \
                :

            if current_node["product_name"] != product_name : current_node["product_name"] = product_name
            if current_node["brand_name"] != brand_name: current_node["brand_name"] = brand_name
            if current_node["description"] != description: current_node["description"] = description
            if len(current_node["photos"]) < len(photos): current_node["photos"] = photos
            # for patch request to databse
            r = requests.patch(BASE_URL +  '/product/' + current_node['product_id'],
                               data=json.dumps(current_node), headers=header)  # updating price in db

            # ............          calculating values for hotdeals payload........................
            if old_price != '' and old_price != ' ' and old_price != None and NEW_price != '' and NEW_price != ' ' and NEW_price != None:
                old_price = int(old_price)
                NEW_price = int(NEW_price)
                offer_percentage = (old_price - NEW_price) * 100 / old_price
                coins = 0.01 * NEW_price
                today = datetime.datetime.now()
                current_date = today.strftime("%d/%m/%Y")

                # ............          calculating values for hotdeals payload........................


                # .....        if offer> 5% , we add to hotdeals in revme db..............
                # if offer_percentage > 5 and old_price > NEW_price:
                #     hotDeals = Hotdeals()
                #     hotDeals.hotdeals_creation(item = current_node, old_price = old_price,  header=header, position=0 , offer_percentage= offer_percentage)

                if old_price > NEW_price:
                    addAlert(current_node, old_price , 0)




        yield Product(currentNode = current_node)
