# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PoorvikaMobilesItem(scrapy.Item):
    # define the fields for your item here like:
    stores = scrapy.Field()
    storelink = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    product_name = scrapy.Field()
    storeprice = scrapy.Field()
    description = scrapy.Field()
    photos = scrapy.Field()
    storeproductid = scrapy.Field()
    product_id = scrapy.Field()
    rating = scrapy.Field()
    reviews = scrapy.Field()
    spec_title = scrapy.Field()
    spec_detail = scrapy.Field()
    brand = scrapy.Field()
