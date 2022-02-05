# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from curses.ascii import isalpha
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies0502

    def process_item(self, item, spider):
        salary = self.process_salary(item.get('salary'), spider)
        item['salary_min'], item['salary_max'], item['cur'] = salary
        del item['salary']
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    @staticmethod
    def process_salary(dirty_salary, spider):
        min_salary, max_salary, cur = None, None, None
        if spider.name == 'hhru':
            for index, value in enumerate(dirty_salary):
                if value.strip() == 'от':
                    min_salary = int(dirty_salary[index+1])
                if value.strip() == 'до':
                    max_salary = int(dirty_salary[index+1])
            if len(dirty_salary) > 1:
                cur = dirty_salary[-2]
        if spider.name == 'sjru':
            min_salary = int(dirty_salary[2].replace(
                '\xa0', '').replace('руб.', ''))
            cur = 'руб.'
        return min_salary, max_salary, cur
