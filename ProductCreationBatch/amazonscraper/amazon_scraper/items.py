# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonScraperItem(scrapy.Item):
    ims = scrapy.Field()
    stores = scrapy.Field()
    iurl = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    product_name = scrapy.Field()
    rating = scrapy.Field()
    price = scrapy.Field()
    colour = scrapy.Field()
    instock = scrapy.Field()
    description = scrapy.Field()
    photos = scrapy.Field()
    images = scrapy.Field()
    asin = scrapy.Field()
    product_id = scrapy.Field()
    additional_details = scrapy.Field()
    technical_details = scrapy.Field()
    timestamp = scrapy.Field()
    MRP = scrapy.Field()
    brand_name = scrapy.Field()
