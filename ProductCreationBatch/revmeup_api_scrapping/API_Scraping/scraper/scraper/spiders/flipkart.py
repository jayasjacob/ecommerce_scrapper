import re
import os
import scrapy
import string
import random
import subprocess
from datetime import datetime
from ..items import ScraperItem

class FlipkartSpider(scrapy.Spider):
    name = 'flipkart'
    start_urls = []

    path=os.path.join(os.path.dirname(__file__),'url.txt')
    file = open(path)
    start_urls.append(file.read())
    file.close()

    def parse(self, response):
        # Initializing the item list
        items = ScraperItem()

        # Product Name
        product_name = response.css("._35KyD6::text").get()
        product_name = str(product_name)

        try:
            description = response.css("._3u-uqB::text").get().strip()
        except:
            description = product_name

        #getting store price
        storeprice = response.css('._3qQ9m1::text').extract()
        storeprice = str(storeprice)
        storeprice=storeprice.replace(".00","").replace(",","")

        # getting store link
        storeLink = response.url

        # getting photo url
        photos = response.css('div._2_AcLJ::attr(style)').extract()

        # finding index of 'https' in photo url for getting photo url
        l = photos[0].find("https")

        # finding index of 'pid' in store link for getting store product id
        k = storeLink.find("pid")

        # getting rating
        rating = response.css('.hGSR34::text').extract()

        # getting reviews
        reviews = response.css('.qwjRop div div::text').extract()

        #generating random product id
        product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))

        #getting specification titles for storeAdditionalDetails
        spec_title = response.css(".col.col-3-12::text").extract()

        ##getting specification details for storeAdditionalDetails
        spec_detail = response.css("._3YhLQA::text").extract()

        #storing specification as a map
        storeAdditionalDetails = {}
        for i in range(len(spec_title)):
            storeAdditionalDetails[spec_title[i]] = spec_detail[i]

        stores = {
            "rating" : "NA" if not rating else rating[0],
            "reviews" : reviews,
            "storeProductId": storeLink[k + 4:k + 20],
            "storeLink": storeLink,
            "storeName": "Flipkart",
            "storePrice": storeprice[3:][:-2],
            "storeAdditionalDetails" : storeAdditionalDetails
        }

        #checking if store product id start with 'M' for subcategory to be mobiles
        if storeLink[k + 4:k + 20].startswith('M'):
            sub = 'mobiles'

        # checking if store product id start with 'T' for subcategory to be tablets
        elif storeLink[k + 4:k + 20].startswith('T'):
            sub= 'tablets'

        # checking if store product id start with 'COM' for subcategory to be laptops
        elif storeLink[k + 4:k + 20].startswith('COM'):
            sub = 'laptops'

        # checking if store product id start with 'CAM','DLL','RCT','POI' for subcategory to be cameras
        elif storeLink[k + 4:k + 20].startswith('CAM') \
             or storeLink[k + 4:k + 20].startswith('DLL')\
             or storeLink[k + 4:k + 20].startswith('RCT')\
             or storeLink[k + 4:k + 20].startswith('POI'):
             sub= 'cameras'

        # checking if 'earphone' or 'headset' in storelink for subcategory to be earphones
        elif 'earphone' in storeLink or 'headset' in storeLink:
            sub='earphones'

        #else subcategory is speaker
        else:
            sub = 'speaker'

        # Adding the values to the scraper items
        items['product_name'] = product_name
        items['product_id'] = product_id
        items['timestamp'] = str(datetime.now())
        items['brand_name'] = product_name
        items['stores'] = stores
        items['category'] = 'electronics'
        items['subcategory'] = sub
        items['description'] = description
        items['photos'] = photos

        # Returing the scraped values to the scraper
        yield items
