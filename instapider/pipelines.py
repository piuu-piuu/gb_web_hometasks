# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import scrapy
from pymongo import MongoClient

class InstapiderPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.insta

    def process_item(self, item, spider):
        connections = self.mongobase['connections']
        userlist = self.mongobase['userlist']
        dict_item = dict(item)
        dict_connections = {'target_user_id' : str(dict_item['target_user_id']), 'following_user_id': str(dict_item['following_user_id'])}
        dict_userlist = {'user_id' : str(dict_item['user_id']), 'user_name' : dict_item['user_name'], 'user_pic' : dict_item['user_pic']}
        connections.insert_one(dict_connections)
        userlist.insert_one(dict_userlist)
        return item