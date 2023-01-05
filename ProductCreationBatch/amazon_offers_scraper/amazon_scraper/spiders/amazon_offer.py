import datetime
import re
import string
import random
import scrapy
from ..items import AmazonScraperItem
import rotating_proxies
import json
from ..config import *
from scrapy.http import TextResponse
import datetime
import pprint
import json
import requests
import scrapy, random, string
from ..items import AmazonScraperItem
from ..config import *
from scrapy import Selector
from scrapy import Request


def expiry_time(time1, time2):
    months = [" Jan", " Feb", " Mar", " Apr", " May", " Jun", " Jul", " Aug", "Sep", " Oct", " Nov", " Dec"]
    count = 0
    d1 = []
    d2 = []
    for t in range(len(time1)):
        if time1[t] == ",":
            d1.append(time1[count:t])
            count = t + 1
    d1.append(time1[-4:])
    count = 0
    for t in range(len(time2)):
        if time2[t] == ",":
            d2.append(time2[count:t])
            count = t + 1
    d2.append(time2[-4:])
    print(d1)
    print(d2)
    if ((int(d1[2]) < int(d2[2])) or (months.index(d1[1]) <= months.index(d2[1]) and int(d1[0]) <= int(d2[0]))):
        return 1
    else:
        return 0


class AmazonSpider(scrapy.Spider):
    print("------------------------I am --------------")
    handle_httpstatus_list = [404]
    name = 'amazon_scraper2'
    start_urls = [
        'https://www.amazon.in/s?k=offers+phones&qid=1607251222&ref=sr_pg_1']
    useragent_headers = {'referer': 'http://www.google.com',
               'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
               # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"
               # 'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
               }
    products = []

    def start_requests(self):
        print("worked")
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers=self.useragent_headers
            )


    def parse(self, response):
        LINK = response.css(".a-link-normal.a-text-normal ::attr(href)").getall()
        product_link = []
        for x in range(len(LINK)):
            if (x % 2 != 1):
                product_link.append(LINK[x])
        # BASE_URL = Credentials.api_base_url
        # # Auth.
        # url1 = BASE_URL + "/user/login"
        # resp = requests.post(url1, json={
        #     "userid": Credentials.userid,
        #     "password": Credentials.password
        # })
        # a = resp.json()
        # tok = a['token']
        # header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
        '''res=requests.post(BASE_URL + '/product_renewed'
                            , data=payload,
                            headers=header)'''

        for x in product_link:
            yield Request(
                response.urljoin(str(x)),  # -> url of product that doesnot exist in the db
                callback=self.parse_product,
                headers=self.useragent_headers

            )

    # DELETE FROM HOTDEALS
        BASE_URL = Credentials.api_base_url
        url_delete = "https://apistaging.revmeup.in/api/v1/user/login"
        resp3 = requests.post(url_delete, json={
            "userid": "ZKh5adE6Lvb2lQGrru9LEKWQUXq2",
            "password": "ZKh5adE6Lvb2lQGrru9LEKWQUXq2"
        })
        a = resp3.json()
        tok = a['token']
        header_1 = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
        get_hot_deals = requests.get(BASE_URL + '/hotdeals', headers=header_1)
        fetched_hot_deals = get_hot_deals.json()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        x = str(datetime.datetime.now() + datetime.timedelta(days=1))
        t = str(int(x[8:10])) + ", " + months[int(x[5:7]) - 1] + ", " + x[:4]
        y = str(datetime.datetime.now())
        current_date = str(int(y[8:10])) + ", " + months[int(y[5:7]) - 1] + ", " + y[:4]
        product_id = []
        # print("-----------", current_date, "---------------")
        for i in fetched_hot_deals:
            expiry_date = i['expirydate']
            exp= expiry_time(expiry_date,current_date)
            print(exp)
            if expiry_date == current_date or exp == 1:
                id = i['hotDealId']
                requests.delete(BASE_URL + '/hotdeals/' + id, headers=header_1)
        #NEXT_PAGE_SELECTOR = '.a-last a::attr(href)'
        #next_page = response.css(NEXT_PAGE_SELECTOR).extract()
        next_page_url = response.xpath("//ul[@class='a-pagination']/li[@class='a-last']/a").xpath("@href").get()
        print('---------------hibye--------------------', next_page_url, '----------------------------------------')

        if next_page_url:
            yield Request(
                response.urljoin(str(next_page_url)),
                callback=self.parse,
                headers=self.useragent_headers
                )

    # def expiry_time(self, time1, time2):
    #     months = [" Jan", " Feb", " Mar", " Apr", " May", " Jun", " Jul", " Aug", "Sep", " Oct", " Nov", " Dec"]
    #     count = 0
    #     d1 = []
    #     d2 = []
    #     for t in range(len(time1)):
    #         if time1[t] == ",":
    #             d1.append(time1[count:t])
    #             count = t + 1
    #     d1.append(time1[-4:])
    #     count = 0
    #     for t in range(len(time2)):
    #         if time2[t] == ",":
    #             d2.append(time2[count:t])
    #             count = t + 1
    #     d2.append(time2[-4:])
    #     print(d1)
    #     print(d2)
    #     if (int(d1[2]) <= int(d2[2]) and months.index(d1[1]) <= months.index(d2[1]) and int(d1[0]) <= int(d2[0])):
    #         return 1
    #     else:
    #         return 0


    def parse_product(self, response):
        items = {}

        # Extracting the product ID from the website
        product_name = response.xpath("//span[@id='productTitle']//text()").get() or response.xpath(
            "//h1[@id='title']//text()").get()

        try:
            product_name = product_name.strip()
        except:
            pass

        # adding unique product id
        product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 15))  # random 15 len alphanumeric id

        # Adding Reviews
        reviews = response.xpath(
            "//div[@class='a-expander-content reviewText review-text-content a-expander-partial-collapse-content']/span//text()").getall()

        # Adding Price
        price = response.xpath("//span[@id='priceblock_ourprice']//text()") or response.xpath(
            "//span[@id='priceblock_dealprice']//text()")

        # Adding Rating
        rating = response.xpath("//div[@id='averageCustomerReviews_feature_div']").xpath(
            "//span[@class='a-icon-alt']//text()").get()

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
        i = 0
        new_dict = {}
        for k, v in additional_details.items():
            if i < 2:
                new_dict[v] = k
                i += 1
            else:
                new_dict[k] = v
        additional_details = new_dict

        # Adding Instock Status
        instock = response.xpath("//div[@id='availability']").xpath(
            "//span[@class='a-size-medium a-color-success']//text()").get() or "Out Stock"
        instock = instock.strip()

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
                brand_name = "Not Available"

        # ADDING PHOTOS
        photos = response.css('#altImages').css('::attr(src)').extract()
        for i in range(len(photos)):
            photos[i] = photos[i].rsplit('.', 2)[0] + "." + photos[i].split(".")[-1]

        # Adding Store logo
        store_logo = "https://i.pinimg.com/564x/42/a7/86/42a7861bb1a403af534b18986ab4e198.jpg"

        # asin = response.css('#productDetails_detailBullets_sections1 tr:nth-child(1) td').css("::text").extract()

        # setting categories and sub categories
        iurl = response.url
        category = response.css("li:nth-child(1) .a-color-tertiary").css("::text").extract()
        try:
            category = category[0].strip()
        except:
            try:
                category = category.strip()
            except:
                category = "Electronics"
        subcategory_temp = response.css(".a-breadcrumb-divider+ li .a-color-tertiary").css("::text").extract()
        # if type(subcategory_temp) == list():
        try:
            subcategory = str(subcategory_temp[0].strip())
        except:
            subcategory = ''

        # Adding MRP
        MRP = response.css('#price .a-text-strike').css('::text').extract()

        trim = re.compile(r'[^\d.,]+')
        MRP = str(MRP)
        MRP = trim.sub('', MRP)
        MRP = MRP.replace(".00", "").replace(",", "")

        price = str(price)
        price = trim.sub(' ', price)
        price = price.replace(".00", "").replace(",", "")

        storeProductId = response.css('#productDetails_detailBullets_sections1 tr:nth-child(1) td').css(
            '::text').extract()

        try:
            try:
                storeProductId = storeProductId.strip()
            except:
                storeProductId = storeProductId[0].strip()
        except:
            try:
                try:
                    storeProductId = iurl.split("/dp/")[1].split("/")[0].split('?')[0]
                except:
                    storeProductId = iurl.split("/dp/")[1].split("/")[0]
            except:
                pass

        # CREATING STORES FOR PAYLOAD
        stores = {
            "storeProductId": storeProductId,
            "storeLink": iurl,
            "storeName": "amazon",
            "storePrice": price[1:],
            "store_mrp": MRP[1:],
            "store_logo": store_logo,
            "storeDescription": description,
            "reviews": reviews,
            "rating": rating,
            "instock": instock,
            "storeTechnicalDetails": technical_details,
            "storeAdditionalDetails": additional_details
        }
        # print("hibibibibibibibiibbibiibibibbi",product_name," ",product_id," ", brand_name," ", stores," ", category," ", subcategory," ", description,
        #       " ", photos)
        # Adding the values to the scraper items
        items['product_name'] = product_name
        items['product_id'] = product_id
        items['timestamp'] = str(datetime.datetime.now())
        items['brand_name'] = brand_name
        items['stores'] = stores
        items['category'] = category
        items['subcategory'] = subcategory
        items['description'] = description
        items['photos'] = photos
        self.products.append(items)
        # print("-------------PRODUCTS---------------------------",self.products,"-----PRODUCTS------------------------------")

        # //send to db -- code form amazon scaper\
        payload = json.dumps(items)
        BASE_URL = Credentials.api_base_url
        # Auth.
        url1 = BASE_URL + "/user/login"
        resp = requests.post(url1, json={
            "userid": Credentials.userid,
            "password": Credentials.password
        })
        a = resp.json()
        tok = a['token']
        header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}
        data_add = []
        url_by_prod_id = BASE_URL + '/product?stores.storeProductId=' + storeProductId
        res_prod_id = requests.get(url_by_prod_id, headers=header)
        info = res_prod_id.json()
        #print("---------INFO--------",info,"-------------INFO-----------")
        if (len(info) == 0 and len(stores["storePrice"])>3):
            res = requests.post(BASE_URL + '/product/'
                                , data=payload,
                                headers=header)
            print("POSTING")
        else:
            print("--------INFO PRODUCT_ID-------------",info[0]["product_id"],"iNFO-----------------------")
            print("_______NON UPDATED PRODUCT ID______",items["product_id"])
            # items["product_id"]=info[0]["product_id"]
            # payload = json.dumps(stores)
            # res = requests.patch(url_by_prod_id
            #                     , data=payload,
            #                     headers=header)
            # print("_____________UPDATED_________PRODUCT",items["product_id"])
            amazon_store = items['stores']
            # print(flipkart_store)

            info[0]['stores'][0]=amazon_store
            # pprint.pprint(product_details[0]['stores'][1])
            patch_url = 'https://apistaging.revmeup.in/api/v1/product/' + info[0]['product_id']
            l = requests.patch(patch_url, data=json.dumps(info[0]), headers=header)
            print("---STATUS---------",l.status_code,"------------STATUS------------")
        #res=res.json()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        x = str(datetime.datetime.now() + datetime.timedelta(days=1))
        t = str(int(x[8:10])) + ", " + months[int(x[5:7]) - 1] + ", " + x[:4]
        y = str(datetime.datetime.now())
        current_date = str(int(y[8:10])) + ", " + months[int(y[5:7]) - 1] + ", " + y[:4]

        BASE_URL = Credentials.api_base_url
        # Auth.
        url2 = BASE_URL + "/user/login"
        resp1 = requests.post(url2, json={
            "userid": Credentials.userid,
            "password": Credentials.password
        })
        a = resp1.json()
        tok = a['token']
        info = res_prod_id.json()
        hotdeal = {
            "dealBackgroundImage": "https://cdn.revmeup.in/Miscellaneous/banner.png",
            "expirydate": t,
            "category": "Daily Offers",
            "hotDealName": "Electronics",
            "newPrice": price[1:],
            "offerBackgroundImage": "https://s3.us-east-2.wasabisys.com/cdn.revmeup.in/Miscellaneous/pricetag.png",
            "oldPrice": MRP[1:],
            "productImage": photos[0],
            "productName": info[0]["product_name"],
            "product_id": info[0]["product_id"],
            "storeImage": "https://cdn.zeplin.io/5eca77e2e0303147915e799a/assets/A9DBDA18-FE59-4E9E-95E3-1BB9B438A10A.png",
            "storeName": "Amazon"
        }
        get_hot_deals = requests.get(BASE_URL + '/hotdeals', headers=header)
        fetched_hot_deals = get_hot_deals.json()
        payload = json.dumps(hotdeal)
        count = 0
        id = ""
        for i in fetched_hot_deals:
            if hotdeal['product_id'] == i["product_id"]:
                count = 1
                id = i['hotDealId']

        if (count == 1 and len(stores["storePrice"])>3):
            res_update = requests.patch(BASE_URL + '/hotdeals/' + id, data=payload, headers=header)
            print("updated")
        elif(count==0 and len(stores["storePrice"])>3):
            res_post = requests.post(BASE_URL + "/hotdeals", data=payload, headers=header)
            print(res_post.json())
            print("posted")

        yield hotdeal
