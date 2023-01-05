# -*- coding: utf-8 -*-
import json
from datetime import datetime
import random
import string
import re

import requests
import scrapy
from ..config import *

from ..items import GadgetsnowItem


class GadgetsnowScraperSpider(scrapy.Spider):
    name = 'gadgetsnow_scraper'
    start_urls = ['https://shop.gadgetsnow.com/']
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"}

    def start_requests(self):
        for url in self.start_urls: yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)
        # print("hai")

    def parse(self, response):
        # print("hello")
        categories = response.css(".overflowhidden li a::attr('href')").getall()
        brands = response.css(".list-brands-logo li a::attr('href')").getall()
        # print(categories)
        # print(brands)
        urls = []
        for item in categories:
            urls.append("https://shop.gadgetsnow.com" + item)

        for item in brands:
            urls.append("https://shop.gadgetsnow.com" + item)

        # print(urls)
        for url in urls: yield scrapy.Request(url=url, callback=self.parse_pages, headers=self.headers)

    def parse_pages(self, response):
        product_urls = response.css(".product-anchor::attr('href')").getall()
        scrap_urls = []
        for item in product_urls:
            scrap_urls.append("https://shop.gadgetsnow.com" + item)

        for url in scrap_urls:
            yield scrapy.Request(url=url, callback=self.parse_elec, headers=self.headers)

    def parse_elec(self, response):
        items = GadgetsnowItem()

        # regular expression to remove html tags
        clean = re.compile('<.*?>')

        # extract images
        items['photos'] = response.css(".cloud-zoom-gallery").css("a::attr('href')").extract()

        # url
        items['iurl'] = response.url

        # category
        category = response.css("tr:nth-child(2) td+ td").extract()
        category = re.sub(clean, '', category[0])
        items['category'] = category

        # subcategory
        subcategory = response.css("tr:nth-child(1) td+ td").extract()
        brand_name = response.css("tr:nth-child(1) td+ td").extract()

        subcategory = re.sub(clean, '', subcategory[0])
        brand_name = re.sub(clean, '', brand_name[0])

        items['subcategory'] = subcategory.strip()
        items['brand_name'] = brand_name.strip()

        # product_name
        product_name = response.css('h1').extract()
        product_name = re.sub(clean, '', product_name[0])
        items['product_name'] = product_name.strip()

        # rating
        rating = response.css('.rating-value span:nth-child(1)').extract()
        try:
            rating = re.sub(clean, '', rating[0])
            rating = rating.strip()
        except:
            try:
                rating = re.sub(clean, '', rating)
                rating = rating.strip()
            except:
                rating = ""
        items['rating'] = rating

        # price
        price = response.css('.offerprice').extract()
        try:
            price = re.sub(clean, '', price[0])
            price = price.strip().replace("Offer Price :", "").strip().replace("`", "").strip()
        except:
            try:
                price = re.sub(clean, '', price)
                price = price.strip().replace("Offer Price :", "").strip().replace("`", "").strip()
            except:
                price = ""

        items['price'] = price

        # description
        description = response.css('.keyfeat').extract()
        try:
            description = description[0].strip()
            description = re.sub(clean, '', description).strip()
        except:
            try:
                description = description.strip()
                description = re.sub(clean, '', description).strip()
            except:
                description = ""
        items['description'] = description

        # timestamp
        items['timestamp'] = datetime.now()

        # additional_details
        title = response.css('.all-camel-case').extract()
        details = response.css('.all-camel-case+ dd').extract()
        storeAdditionalDetails = {}
        for i in range(len(title)):
            title[i] = re.sub(clean, '', title[i]).strip()
            details[i] = re.sub(clean, '', details[i]).strip()
            storeAdditionalDetails[title[i]] = details[i]
        items['additional_details'] = storeAdditionalDetails

        # MRP
        MRP = response.css('.oldp').extract()
        try:
            MRP = re.sub(clean, '', MRP[0]).strip()
        except:
            try:
                MRP = re.sub(clean, '', MRP).strip()
            except:
                MRP = ""

        items['MRP'] = MRP

        # generating random product id
        items['product_id'] = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))

        stores_todb = [{
            "storeProductId": items['product_id'],
            "storeLink": items['iurl'],
            "storeName": "gadgetsnow",
            "storePrice": items['price'],
            "store_mrp": items['MRP'],
            "store_logo": "https://www.gadgetsnow.com/",
            "storeDescription": items['description'],
            "reviews": "",
            "rating": items['rating'],
            "instock": "instock",
            "storeTechnicalDetails": items['additional_details'],
        }]

        data_db_form = {
            "product_name": items['product_name'],
            "product_id": items['product_id'],
            "timestamp": str(items['timestamp']),
            "brand_name": items['brand_name'],
            "stores": stores_todb,
            "category": items['category'],
            "subcategory": items['subcategory'],
            "description": items['description'],
            "photos": items['photos'],
        }

        # send to DB
        BASE_URL = Credentials.api_base_url
        # Auth.
        url = BASE_URL + "/user/login"
        response = requests.post(url, json={
            "userid": Credentials.userid,
            "password": Credentials.password
        })
        a = response.json()
        tok = a['token']
        header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}

        res = requests.get(BASE_URL + '/externalproduct?product_name=' + items['product_name'], headers=header)
        if not res.json():
            payload = json.dumps(data_db_form)
            res = requests.post(BASE_URL + '/externalproduct', data=payload, headers=header)
            print(res.status_code)
            print('sending to db : ', items['product_id'])
        else:
            pass
        yield items