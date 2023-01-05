import pprint
import json
import requests
import scrapy,random,string
from ..items import FlipkartScraperItem
from ..config import  *


# Auth.
BASE_URL = Credentials.api_base_url
url = BASE_URL + "/user/login"
response = requests.post(url, json={
    "userid": Credentials.userid,
    "password": Credentials.password
})
a = response.json()
tok = a['token']
header_1 = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}



class FlipkartSpider(scrapy.Spider):

    name = 'flipkart_scraper'
    #number of pages we want to scrape
    no_of_pages = 15
    #setting header for our scraper
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"}

    with open("./data/keywords.txt", "r") as myfile:
        keyword = myfile.readlines()
    content = [x.strip().replace(" ", "+") for x in keyword]
    items = content
    def start_requests(self):

        # starting urls for scraping with respective items
        urls = []
        for item in self.items:
            urls.append("https://www.flipkart.com/search?q=" + item )

        for url in urls: yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)



    def parse(self, response, **kwargs):
        self.no_of_pages -= 1

        prod_urls =  response.css('._31qSD5').css("::attr(href)").extract()

        # requesting further for individual each product
        for elec in prod_urls:
            final_url = response.urljoin(elec)
            yield scrapy.Request(url=final_url, callback=self.parse_elec, headers=self.headers)

        if (self.no_of_pages > 0):
            next_page_url = response.css('._3fVaIS').css("::attr(href)").extract()
            try:
                final_url = response.urljoin(next_page_url[0])
                yield scrapy.Request(url=final_url, callback=self.parse, headers=self.headers)
            except:
                pass


    def parse_elec(self, response):

        items = FlipkartScraperItem()

        #getting product name
        product_name = response.css("._35KyD6::text").get()
        product_name = str(product_name)

        #getting store price
        storeprice = response.css('._3qQ9m1::text').extract()
        storeprice = str(storeprice)
        storeprice=storeprice.replace(".00","").replace(",","")

        #getting store link
        storeLink = response.url

        #getting photo url
        photos = response.css('div._2_AcLJ::attr(style)').extract()

        #finding index of 'https' in photo url for getting photo url
        l = photos[0].find("https")

        #finding index of 'pid' in store link for getting store product id
        k = storeLink.find("pid")

        #getting rating
        rating = response.css('.hGSR34::text').extract()

        #getting reviews
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


        stores = [{

            "rating" : "NA" if not rating else rating[0],
            "reviews" : reviews,
            "storeProductId": storeLink[k + 4:k + 20],
            "storeLink": storeLink+"&affid=meghana&affExtParam1=revmeup",
            "storeName": "Flipkart",
            "storePrice": storeprice[3:][:-2],
            "storeAdditionalDetails" : storeAdditionalDetails
        }]
        stores_forNew =[{
            "storeProductId": "",
            "storeLink": "www.amazon.in",
            "storeName": "amazon",
            "storePrice":  "",
            "store_mrp" :  "",
            "store_logo" : "https://i.pinimg.com/564x/42/a7/86/42a7861bb1a403af534b18986ab4e198.jpg",
            "storeDescription" : "",
            "reviews": [],
            "rating": "",
            "instock" : "",
            "storeTechnicalDetails" : [],
            "storeAdditionalDetails" : []
        },{

            "rating": "NA" if not rating else rating[0],
            "reviews": reviews,
            "storeProductId": storeLink[k + 4:k + 20],
            "storeLink": storeLink+"&affid=meghana&affExtParam1=revmeup",
            "storeName": "Flipkart",
            "storePrice": storeprice[3:][:-2],
            "storeAdditionalDetails": storeAdditionalDetails
        }]

        items['product_name'] = product_name
        items['product_id'] = product_id
        items['stores'] = stores
        items['category'] = 'electronics'

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

        items['subcategory'] = sub
        items['brand'] = product_name.split()[0]
        items['description'] = product_name
        items["photos"] = [photos[0][l:-1]]
        yield items
        #****************************API CALLS AND PATCHING******************************

        try:
            model_numb = items['stores']['storeAdditionalDetails']['Model Number']  # getting model number from payload
        except:
            model_numb = []
        if model_numb != []:  # checking model number is not empty
            url2 = BASE_URL+'/product?stores.storeTechnicalDetails.Item model number=' + model_numb  # queriying db with model number
            l = requests.get(url2, headers=header_1)
            product_details = l.json()

            if product_details == []:  # checking if product details  null
                url2 = BASE_URL+'/product?stores.storeTechnicalDetails.Model number=' + model_numb
                l = requests.get(url2, headers=header_1)
                product_details = l.json()

            if product_details != []:
                flipkart_store = items['stores']
                # print(flipkart_store)

                product_details[0]['stores'].append(flipkart_store)
                # pprint.pprint(product_details[0]['stores'][1])
                patch_url = BASE_URL+'/product/' + product_details[0]['product_id']
                l = requests.patch(patch_url, data=json.dumps(product_details[0]), headers=header_1)
                print(l.status_code)

                url_2 = BASE_URL+'/product?stores.storeTechnicalDetails.Model number=' + model_numb

                l = requests.get(url2, headers=header_1)
                product_details_1 = l.json()
                pprint.pprint(product_details_1)

            elif product_details == []:
                items['stores'] = stores_forNew
                post_url = BASE_URL+'/product'
                res = requests.post(post_url, data=items, header=header_1)
