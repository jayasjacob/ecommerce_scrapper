from ..items import VijaysalesElectronicsItem
import json
from datetime import datetime
import requests
import scrapy, random, string
from ..config import *


class VijaysalesSpider(scrapy.Spider):
    name = 'vijaytablet'
    pageno = 20

    start_urls = ['https://www.vijaysales.com/Mobiles-Tablets/TABLETS/1/976']

    def parse(self, response, **kwargs):

        page = response.css("a.vj-cur-pnter::attr('href')").getall()

        for p in page:
            yield scrapy.Request(p, callback=self.parse_elec)

    # page = 'https://www.snapdeal.com/acors/json/product/get/search/175/'+ str(VijaysalesSpider.pageno)+ '/20?q=&sort=plrty'
    # if VijaysalesSpider.pageno <= 100:
    #   VijaysalesSpider.pageno += 20
    #  yield response.follow(page, callback=self.parse)

    def parse_elec(self, response):

        items = VijaysalesElectronicsItem()

        product_name = response.css('#ContentPlaceHolder1_h1ProductTitle::text').get()

        storeprice = response.css('#ContentPlaceHolder1_divPrdPriceStucture .row_ .amt::text').get()

        storeLink = response.url

        id = storeLink[::-1].find('/')

        photos = response.css('img#ContentPlaceHolder1_ProductImage').xpath("@src").get()

        spec_title = response.css(".sptyp::text").extract()

        spec_detail = response.css(".spval::text").extract()

        product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))

        # rating = response.css('span.avrg-rating::text').get()
        # reviews = response.css('#defaultReviewsCard p::text').extract()

        stores = {

            "rating": [],
            "reviews": [],
            'storeproductid': storeLink[-id:],
            "storeLink": storeLink,
            "storeName": "Vijaysales",
            "storePrice": storeprice,

        }

        items['product_name'] = product_name.strip()
        items['product_id'] = product_id
        items['stores'] = stores
        items['category'] = 'electronics'
        items['subcategory'] = 'tablet'
        items['brand_name'] = product_name.split()[0]
        items['description'] = {}

        for i in range(len(spec_title)):
            items['description'][spec_title[i].strip()] = spec_detail[i].strip()

        items['photos'] = photos

        # timestamp
        items['timestamp'] = str(datetime.now())

        data_db_form = {
            "product_name": items['product_name'],
            "product_id": items['product_id'],
            "timestamp": str(items['timestamp']),
            "brand_name": items['brand_name'],
            "stores": items['stores'],
            "category": items['category'],
            "subcategory": items['subcategory'],
            "description": "",
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

        # res = requests.get(BASE_URL + '/externalproduct?product_name=' + items['product_name'], headers=header)
        # if not res.json():
        payload = json.dumps(data_db_form)
        res = requests.post(BASE_URL + '/externalproduct', data=payload, headers=header)
        print(res.status_code)
        print('sending to db : ', items['product_id'])
        # else:
        #     pass

        yield items
