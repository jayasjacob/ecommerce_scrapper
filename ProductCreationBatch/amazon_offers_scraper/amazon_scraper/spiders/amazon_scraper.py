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


class AmazonSpider(scrapy.Spider):
    print("------------------------I am --------------")
    handle_httpstatus_list = [404]
    name = 'amazon_scraper'
    start_urls = [
        'https://www.amazon.in/s?k=offers+phones&qid=1607251222&ref=sr_pg_1']
    headers = {'referer': 'http://www.google.com',
               # 'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
               # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"
               'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
               }

    def start_requests(self):
        print("worked")
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers=self.headers
            )
    def expiry_time(self,time1, time2):
        months = [" Jan", " Feb", " Mar", " Apr", " May", " Jun", " Jul", " Aug", "Sep", " Oct", " Nov", " Dec"]
        count=0
        d1=[]
        d2=[]
        for t in range(len(time1)):
            if time1[t]== "," :
                d1.append(time1[count:t])
                count = t+1
        d1.append(time1[-4:])
        count=0
        for t in range(len(time2)):
            if time2[t]== "," :
                d2.append(time2[count:t])
                count=t+1
        d2.append(time2[-4:])
        print(d1)
        print(d2)
        if (int(d1[2])<=int(d2[2]) and months.index(d1[1])<=months.index(d2[1]) and int(d1[0])<=int(d2[0])):
            return 1
        else:
            return 0



    def parse(self, response):
        print("----- i came hear------")
        image = response.css(".s-image ::attr(src)").extract()
        #print(image)
        NAME = response.css(".a-size-medium.a-color-base.a-text-normal::text").extract()
        name = []
        for x in NAME:
            if "\n" not in x:
                name.append(x)

        Offers = response.css(".a-color-price::text").extract()

        offers = []
        for x in Offers:
            if (x[-1] == "F"):
                offers.append(x)

        Price2 = response.css(".a-offscreen::text").extract()
        Price1 = [x[1:] for x in Price2]

        price = response.css(".a-price-whole::text").extract()

        Price = []
        count = 0
        for x in range(len(Price1) - 1):
            if (count < len(price) and price[count] == Price1[x]):
                if (count + 1 < len(price)):
                    if (price[count + 1] != Price1[x + 1]):
                        Price.append(Price1[x + 1])
                    else:
                        Price.append("Not given")
                count = count + 1
        Price.append(Price1[-1])
        original_price = []
        for y in Price:
            l = []
            for z in y:
                if (z != ','):
                    l.append(z)
            original_price.append(''.join(l[1:]))

        PID = response.css("div::attr(data-asin)").getall()
        product_id = []
        for x in PID:
            if (len(x) == 10):
                product_id.append(x)
        LINK = response.css(".a-link-normal.a-text-normal ::attr(href)").getall()
        product_link=[]
        for x in range (len(LINK)):
            if(x%2!=1):
                product_link.append(LINK[x])

        print(len(name))
        print(len(price))
        print(len(product_id))
        print(len(Price))
        print(len(product_link))
        row_data = zip(name, price, product_id, Price, product_link)

        data = []
        for item in row_data:
            scraped_info = {
                "NAME": item[0],
                "PRICE": item[1],
                "ASIN ID": item[2],
                "ORIGINAL PRICE": item[3],
                "PRODUCT_LINK": item[4]

            }
            data.append(str(scraped_info) + "\n")
            # print(scraped_info)
        #print(data)
        for item in row_data:
            yield {
                "NAME": item[0],
                # "OFFERS":item[1],
                "PRICE": item[1],
                "ASIN ID": item[2],
                "ORIGINAL PRICE": item[3],
                "PRODUCT_LINK": item[4]
            }
        with open("data.txt", "a", encoding='utf8') as file:
            file.writelines(data)
        file.close()
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
        '''res=requests.post(BASE_URL + '/product_renewed'
                            , data=payload,
                            headers=header)'''
        data_add = []
        missing_data = []
        row_data1 = zip(name, price, product_id, Price, product_link)
        for item in row_data1:
            url_by_prod_id = BASE_URL + '/product?stores.storeProductId=' + item[2]
            res_prod_id = requests.get(url_by_prod_id, headers=header)
            info = res_prod_id.json()
            if (len(info) == 0):
                missing_data.append(item[2])
                yield Request(
                    response.urljoin(str(item[4])),  # -> url of product that doesnot exist in the db
                    callback=self.parse_product,
                    headers=self.headers

                )
        #print(product_link)
        #print(len(product_link))
        #print(len(product_id))
        print("----------------MISSING DATA-----------------------------", missing_data, "--------------MISSING DATA---------------")
        row_data2 = zip(name, price, product_id, Price, product_link,image)
        hot_deals=[]
        #print("=======================",list(row_data2), "====================")
        for item in row_data2:
            url_by_prod_id = BASE_URL + '/product?stores.storeProductId=' + item[2]
            res_prod_id = requests.get(url_by_prod_id, headers=header)
            info = res_prod_id.json()
            if(len(info)!=0):
                add = {
                "NAME": item[0],
                "PRICE": item[1],
                "ASIN ID": item[2],
                "ORIGINAL PRICE": item[3],
                "PRODUCT_LINK": item[4],
                "Image":item[5],
                "PRODUCT_ID": info[0]['product_id']
                }
            hot_deals.append(add)
            data_add.append(str(add) + "\n")
        #print(data_add)
        #print("-----------------------", data_add, "----------------------")
        with open("data_add.txt", "a", encoding='utf8') as file1:
            file1.writelines(data_add)
        file1.close()
        # HANDLING HOT DEALS API
        #DELETING THE DATABASE
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
        y=str(datetime.datetime.now())
        current_date = str(int(y[8:10])) + ", " + months[int(y[5:7]) - 1] + ", " + y[:4]
        product_id=[]
        #print("-----------", current_date, "---------------")
        for i in fetched_hot_deals:
            product_id.append(i["product_id"])
            expiry_date = i['expirydate']
            exp= self.expiry_time(expiry_date, current_date)
            print(exp)
            if expiry_date == current_date or exp==1:
                id = i['hotDealId']
                requests.delete(BASE_URL + '/hotdeals/' + id, headers=header_1)
        #print(product_id)
        #print(hot_deals)
        #HOT DEALS INSERTION
        for x in hot_deals:
            BASE_URL = Credentials.api_base_url
            # Auth.
            url2 = BASE_URL + "/user/login"
            resp1 = requests.post(url2, json={
                "userid": Credentials.userid,
                "password": Credentials.password
            })
            a = resp1.json()
            tok = a['token']
            header = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}

            items={
                "dealBackgroundImage": "https://cdn.revmeup.in/Miscellaneous/banner.png",
                "expirydate": t,
                "category": "Daily Offers",
                "hotDealName": "Electronics",
                "newPrice": x["PRICE"],
                "offerBackgroundImage": "https://s3.us-east-2.wasabisys.com/cdn.revmeup.in/Miscellaneous/pricetag.png",
                "oldPrice": x["ORIGINAL PRICE"],
                "productImage": x["Image"],
                "productName": x["NAME"],
                "product_id": x["PRODUCT_ID"],
                "storeImage": "https://cdn.zeplin.io/5eca77e2e0303147915e799a/assets/A9DBDA18-FE59-4E9E-95E3-1BB9B438A10A.png",
                "storeName": "Amazon"
            }
            payload = json.dumps(items)
            posted=[]
            patched=[]
            #res1=requests.get(BASE_URL + '/hotdeals', headers=header_1)
            if x["PRODUCT_ID"] in product_id:
                for i in fetched_hot_deals:
                    if x["PRODUCT_ID"]==i["product_id"]:
                        print("FETCHED--------------------", i["product_id"], "-------------------FETCHED")
                        print("x[product]-----------", x["PRODUCT_ID"], "x[PRODUCT_ID]-----------------")

                        patched.append(i["product_id"])
                        id = i['hotDealId']
                        res_update = requests.patch(BASE_URL + '/hotdeals/' + id, data=payload, headers=header)
            else:
                posted.append(items["product_id"])
                res_post = requests.post(BASE_URL + "/hotdeals", data=payload, headers=header)
        print("PATCHED------------PATCHED--------PATCHED",patched,"PATCHED------------PATCHED-------")
        print("POSTED----------------------",posted,"POSTED--------------------------")
        NEXT_PAGE_SELECTOR = '.a-last a::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract()
        print('---------------hibye--------------------', next_page, '----------------------------------------')

        if next_page:
            yield Request(
                response.urljoin(str(next_page)),
                callback=self.parse,
                headers=self.headers
            )

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
        stores = [{
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
        }]
        #print("hibibibibibibibiibbibiibibibbi",product_name," ",product_id," ", brand_name," ", stores," ", category," ", subcategory," ", description,
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

        # //send to db -- code form amazon scaper
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

        payload = json.dumps(items)
        #print("----------------------", payload, "-------------------------")
        res = requests.post(BASE_URL + '/product/', data=payload, headers=header)
        # Returing the scraped values to the scraper
        #yield items