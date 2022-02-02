from avitology import search_avito
from pymongo import MongoClient


def init_db():
    global db
    global search_string
    global category
    search_string = 'Зенит'
    category = 'Плёночные фотоаппараты'
    client = MongoClient('127.0.0.1', 27017)
    db = client[search_string]


def update_db():
    if db.avito == None:
        db.avito.insert_many(search_avito(search_string, category))
    else:
        for item in search_avito(search_string, category):
            if not db.avito.find_one({'item_link': item['item_link']}):
                db.avito.insert_one(item)


init_db()
update_db()
