# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Compose


def clean_price(value):
    value = value.replace('\xa0', '')
    value = value.replace(' ', '')
    try:
        value = int(value)
    except:
        return value
    return value


class LMparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(
        clean_price), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
