import re
import os
import scrapy
import string
import random
import subprocess
from datetime import datetime
from ..items import ScraperItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    # The url for scrap
    start_urls = []

    path=os.path.join(os.path.dirname(__file__),'url.txt')
    file = open(path)
    start_urls.append(file.read())
    file.close()

    def parse(self, response):
        # Initializing the item list
        items = ScraperItem()

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
        reviews = response.xpath("//div[@class='a-expander-content reviewText review-text-content a-expander-partial-collapse-content']/span//text()").getall()

        # Adding Price
        price = response.xpath("//span[@id='priceblock_ourprice']//text()") or response.xpath("//span[@id='priceblock_dealprice']//text()")

        # Adding Rating
        rating = response.xpath("//div[@id='averageCustomerReviews_feature_div']").xpath(
            "//span[@class='a-icon-alt']//text()").get()

        #Adding technical details
        technical_details = response.css('#productDetails_techSpec_section_1 .a-size-base').css('::text').extract()
        technical_details = [re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*]", "", file) for file in technical_details]
        technical_details = list(map(lambda s: s.strip(), technical_details))
        technical_details = dict(zip(technical_details[::2], technical_details[1::2]))
        for k, v in dict(technical_details).items():
            if v == '' or k == '':
                del technical_details[k]

        #Adding additional details
        additional_details = response.css('#productDetails_detailBullets_sections1 td , #productDetails_detailBullets_sections1 .prodDetSectionEntry').css('::text').extract()
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
        MRP = MRP.replace(".00", "").replace(",","")

        price = str(price)
        price = trim.sub(' ', price)
        price = price.replace(".00", "").replace(",","")

        storeProductId = response.css('#productDetails_detailBullets_sections1 tr:nth-child(1) td').css('::text').extract()
        try:
            storeProductId = storeProductId[0].strip()
        except:
            storeProductId = storeProductId.strip()

        if storeProductId == None:
            try:
                storeProductId = iurl.split("/dp/")[1].split("/")[0].split('?')[0]
            except:
                storeProductId = iurl.split("/dp/")[1].split("/")

        #CREATING STORES FOR PAYLOAD
        stores = [{
            "storeProductId": storeProductId,
            "storeLink": iurl,
            "storeName": "amazon",
            "storePrice":  price[1:],
            "store_mrp" :  MRP[1:],
            "store_logo" : store_logo,
            "storeDescription" : description,
            "reviews": reviews,
            "rating": rating,
            "instock" : instock,
            "storeTechnicalDetails" : technical_details,
            "storeAdditionalDetails" : additional_details
        }]

        # Adding the values to the scraper items
        items['product_name'] = product_name
        items['product_id'] = product_id
        items['timestamp'] = str(datetime.now())
        items['brand_name'] = brand_name
        items['stores'] = stores
        items['category'] = category
        items['subcategory'] = subcategory
        items['description'] = description
        items['photos'] = photos

        # Returing the scraped values to the scraper
        yield items
