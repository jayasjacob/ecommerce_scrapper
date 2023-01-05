import pprint
import json
import requests
import scrapy,random,string
from ..items import FlipkartScraperItem
from ..config import  *
from scrapy import Selector
from scrapy import Request
# Auth.
# BASE_URL = Credentials.api_base_url
# url = BASE_URL + "/user/login"
# response = requests.post(url, json={
#     "userid": Credentials.userid,
#     "password": Credentials.password
# })
# a = response.json()
# tok = a['token']
# header_1 = {'Authorization': 'Bearer ' + tok, 'content-type': "application/json"}



class FlipkartSpider(scrapy.Spider):

    name = 'flipkart_scraper'
    start_urls = [
        'https://www.flipkart.com/search?q=offers&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off']
    #number of pages we want to scrape
    #no_of_pages = 15
    #setting header
    #for our scraper
    #headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"}

    #with open("./data/keywords.txt", "r") as myfile:
    #    keyword = myfile.readlines()
    #content = [x.strip().replace(" ", "+") for x in keyword]
    #items = content
    #def start_requests(self):

        # starting urls for scraping with respective items
     #   urls = []
     #   for item in self.items:
     #       urls.append("https://www.flipkart.com/search?q=" + item )

      #  for url in urls: yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)


    page=10
    i=0
    def parse(self, response):
        #name = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "_2cLu-l", " " ))]/text()').extract()

        name=response.css("._2cLu-l::text").extract()
        Offer =response.css("span::text").extract()
        Offers=[]
        for x in Offer:
            if(len(x)==7 and x[2]=='%'):
                Offers.append(x)
        product_id=response.css("div::attr(data-id)").getall()
        #product_id = response.css(."_1HmYoV _35HD7C").attrib['href']
        #product_id =response.css('a::attr(href)').getall()
        #Price = response.xpath('//div[@class="_1vC4OE"]/text()').extract()
        row_data = zip(name, Offers,product_id)  # , Offers)
        #print("-------------------------->",name,"----------------------------------",Offers,"--------------------------",product_id)
        for item in row_data:
            # create dictionary for storing the scraped info
            yield {
                # key:value
                "name": item[0],
                # "Price": item[1],
                # 'Rating': item[3],
                # 'Exchange_price': item[3],
                # 'Emi': item[4],
                'Offers': item[1],
                'product_id':item[2]
                # 'Sale': item[5]
                #  'Original_Price': item[3]
                #  'Discount':item[3],
                # 'company_name': item[3],
            }
        #print(scraped_info)

        NEXT_PAGE_SELECTOR = '._3fVaIS ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR)[-1].extract()
        if next_page:
            yield Request(
                response.urljoin(next_page),
                callback=self.parse
            )
        #yield scraped_info