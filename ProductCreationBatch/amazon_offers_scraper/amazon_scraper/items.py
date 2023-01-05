# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonScraperItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    ASIN_ID=scrapy.Field()
    original_price= scrapy.Field()