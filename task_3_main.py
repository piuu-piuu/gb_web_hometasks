import hhparser as hh
from pymongo import MongoClient
import pprint as pp


def init_db():
    global parse_string
    global db
    parse_string = '2d 3d artist'
    client = MongoClient('127.0.0.1', 27017)
    db = client[parse_string.replace(' ', '_')]


def update_db():
    if db.jobs == None:
        db.jobs.insert_many(hh.parse_jobs(parse_string))
    else:
        for job in hh.parse_jobs(parse_string):
            if not db.jobs.find_one({'link': job['link']}):
                db.jobs.insert_one(job)


def expected_cash(db, alot=50000):
    for job in db.jobs.find({'$and':
                             [{'salary_currency': "руб."},
                              {'$or':
                               [{'salary_min': {'$gt': alot}}, {'salary_max': {'$gt': alot}}
                                ]}]}):
        pp.pprint(job)


init_db()
update_db()
expected_cash(db)
