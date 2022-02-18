# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstapiderItem(scrapy.Item):
    # define the fields for your item here like:
    target_user_id = scrapy.Field()
    target_user_name = scrapy.Field()
    following_user_id = scrapy.Field()
    following_user_name = scrapy.Field()
    user_pic = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()



