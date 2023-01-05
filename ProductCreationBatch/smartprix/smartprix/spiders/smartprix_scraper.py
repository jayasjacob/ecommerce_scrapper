import json
import string

import requests
import scrapy
import  random
from ..items import SmartprixItem
from ..config import *


class SmartprixScraperSpider(scrapy.Spider):
    name = 'smartprix_scraper'
    no_of_pages = 15
    allowed_domains = ['smartprix.com']
    start_urls = ['http://smartprix.com/']
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"}


    def start_requests(self):
        # starting urls for scraping with respective items
        urls = []

        urls.append("https://www.smartprix.com/mobiles#q=earphones")

        for url in urls: yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)


    def parse(self, response,**kwargs):
        self.no_of_pages -= 1

        prod_urls = response.css('.info').css('::attr(href)').extract()

        # requesting further for individual each product
        for elec in prod_urls:
            final_url = response.urljoin(elec)
            yield scrapy.Request(url=final_url, callback=self.parse_elec, headers=self.headers)

        if (self.no_of_pages > 0):
            next_page_url = response.css('._3fVaIS').css("::attr(href)").extract()
            final_url = response.urljoin(next_page_url[0])
            yield scrapy.Request(url=final_url, callback=self.parse, headers=self.headers)


    def parse_elec(self, response):

        items = SmartprixItem()

        #getting product name
        product_name = response.css('.has-favorite-button').css('::text').extract()
        product_name = str(product_name)

        #getting store price
        storeprice = response.css('.price').css('::text').extract()
        storeprice = storeprice[0]
        storeprice = str(storeprice)
        storeprice=storeprice.replace(".00","").replace(",","")

        #getting store link
        storeLink = response.url

        #getting photo url
        photos = response.css('.small-imgs').css('::attr(src)').extract()

        #finding index of 'https' in photo url for getting photo url
        # l = photos[0].find("https")

        #finding index of 'pid' in store link for getting store product id
        # k = storeLink.find("pid")

        #getting rating
        rating = response.css('.rank-1-f').css('::text').extract()

        #getting reviews
        # reviews = response.css('.qwjRop div div::text').extract()

        #generating random product id
        product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))

        #getting specification titles for storeAdditionalDetails
        spec_title = response.css('.bold').css('::text').extract()
        additional_store_link = response.css('.big').css('::attr(href)').extract()

        ##getting specification details for storeAdditionalDetails
        spec_detail = response.css('.bold+ td').css('::text').extract()

        #storing specification as a map
        storeAdditionalDetails = {}
        for i in range(len(spec_title)):

                               storeAdditionalDetails[spec_title[i]] = spec_detail[i]


        stores = [{

            "rating" : "NA" if not rating else rating[0],
            # "reviews" : reviews,
            # "storeProductId": storeLink[k + 4:k + 20],
            "storeLink": storeLink,
            "storeName": "Smartprix",
            "storePrice": storeprice[1:],
            "storeAdditionalDetails" : storeAdditionalDetails,
            "additional_store_links":additional_store_link
        }]


        items['product_name'] = product_name
        items['product_id'] = product_id
        items['stores'] = stores
        items['category'] = 'electronics'



        # items['subcategory'] = sub
        items['brand'] = product_name.split()[0]
        items['description'] = product_name
        items["photos"] = photos

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
            payload = json.dumps(items)
            res = requests.post(BASE_URL + '/externalproduct', data=payload, headers=header)
            print(res.status_code)
            print('sending to db : ', items['product_id'])
        else:
            pass
        yield items


