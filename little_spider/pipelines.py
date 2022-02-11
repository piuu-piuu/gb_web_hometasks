# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


# pipelines and their prioriy (lower better)
# are put into settings.py

class MainparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.lm

    def process_item(self, item, spider):
        collection = self.mongobase['results']
        # if item wasn't preconverted to dict,
        # have to do it for Mongo
        collection.insert_one(dict(item))
        return item


class LMImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        # main parser is enough to put into Mongo (because it's last?),
        # the following is not needed here:
        # collection = self.mongobase['Taps']
        # collection.insert_one(item)
        return item

    # def file_path(self, request, response=None, info=None, *, item=None):
    #     return ''
