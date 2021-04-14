# mongo setup:
# TODO: move connection string to configuration

from pymongo import MongoClient

mongoConnectionUrl = 'mongodb://localhost:27017'
mongoClient = None
mongoDb = None
db_name = 'influ'


profiles=None


def connect_mongo(connectionUrl=None):
    if connectionUrl:
        global mongoConnectionUrl
        mongoConnectionUrl = connectionUrl
    global mongoClient
    mongoClient = MongoClient(connectionUrl)


def connect_db(name='influ'):
    global db_name
    db_name = name
    if not mongoClient:
        connect_mongo()
    global mongoDb
    mongoDb = mongoClient[db_name]
    global profiles
    profiles=mongoDb.profiles



def show_db():
    print(f'Current db_name: {db_name}')


def test_repository():
    print(f'Repository works...')


def select_profiles(query):
    return list(profiles.find(query))


def store_profile(tt_profile):
    mongoDb['profiles'].update_one({'_id': tt_profile['_id']}, {'$set': tt_profile}, upsert=True)
