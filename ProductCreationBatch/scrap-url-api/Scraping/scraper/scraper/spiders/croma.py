import re
import os
import scrapy
import string
import random
import subprocess
from datetime import datetime
from ..items import ScraperItem


class CromaSpider(scrapy.Spider):
    name = 'croma'
    # The url for scrap
    start_urls = []

    path=os.path.join(os.path.dirname(__file__),'url.txt')
    file = open(path)
    start_urls.append(file.read())
    file.close()

    def parse(self, response):
        # Initializing the item list
        items = ScraperItem()

        # getting product name
        product_name = response.css('h1::text').get()

        items['product_name'] = product_name.strip()
        pass
