# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GadgetsnowItem(scrapy.Item):
    photos = scrapy.Field()
    stores = scrapy.Field()
    iurl = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    product_name = scrapy.Field()
    rating = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    product_id = scrapy.Field()
    additional_details = scrapy.Field()
    timestamp = scrapy.Field()
    MRP = scrapy.Field()
    brand_name = scrapy.Field()