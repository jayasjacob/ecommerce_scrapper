import json
from datetime import datetime
import requests
import scrapy, random, string
from ..items import ReliancedigitalElectronicsItem
from ..config import *

class RelianceSpider(scrapy.Spider):
    name = 'reliancespeaker'
    pageno = 2
    start_urls = [
        'https://www.reliancedigital.in/party-speakers/c/S101822?searchQuery=:relevance:availability:Exclude%20out%20of%20Stock&page=0']

    def parse(self, response, **kwargs):

        page = response.css(".sp a::attr('href')").getall()
        for p in page:
            url = 'https://www.reliancedigital.in' + p
            yield scrapy.Request(url, callback=self.parse_elec)

        for page in [
            'https://www.reliancedigital.in/tv-speakers-sound-bars/c/S101811?searchQuery=:relevance:availability:Exclude%20out%20of%20Stock&page=0',
            'https://www.reliancedigital.in/specialty-speakers/c/S101821?searchQuery=:relevance:availability:Exclude%20out%20of%20Stock&page=0']:
            yield response.follow(page, callback=self.parse)

    def parse_elec(self, response):

        items = ReliancedigitalElectronicsItem()

        product_name = response.css('.pdp__title::text').get()
        storeprice = response.css('.pdp__offerPrice::text').extract()
        storeLink = response.url
        photos = response.css(".pdp__mainHeroImgContainer::attr('data-srcset')").get()
        id = storeLink[::-1][:storeLink[::-1].find('/')]
        # rating = response.css('.hGSR34::text').extract()
        # reviews = response.css('.qwjRop div div::text').extract()
        product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))
        spec_title = response.css(".pdp__tab-info__list__name::text").extract()
        spec_detail = response.css(".pdp__tab-info__list__value::text").extract()

        stores = {
            "rating": "NA",
            "reviews": [],
            "storeProductId": id[::-1],
            "storeLink": storeLink,
            "storeName": "RelianceDigital",
            "storePrice": storeprice[0][1:]
        }

        items['product_name'] = product_name
        items['product_id'] = product_id
        items['stores'] = stores
        items['category'] = 'electronics'
        items['subcategory'] = 'speakers'
        items['brand_name'] = product_name.split()[0]
        items['description'] = {}
        # timestamp
        items['timestamp'] = str(datetime.now())

        # for i in range(len(spec_title)):
        #     items['description'][spec_title[i]] = spec_detail[i]

        items["photos"] = 'https://www.reliancedigital.in' + photos

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

        res = requests.get(BASE_URL + '/externalproduct?product_name=' + items['product_name'], headers=header)
        if not res.json():
            payload = json.dumps(data_db_form)
            res = requests.post(BASE_URL + '/externalproduct', data=payload, headers=header)
            print(res.status_code)
            print('sending to db : ', items['product_id'])
        else:
            pass
        yield items
