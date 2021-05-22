# mongo setup:
# TODO: move connection string to configuration

from pymongo import MongoClient

mongoConnectionUrl = 'mongodb://localhost:27017'
mongoClient = None
mongoDb = None
db_name = 'influ'

profiles = None
lists = None


def connect_mongo(connection_url=None):
    if connection_url:
        global mongoConnectionUrl
        mongoConnectionUrl = connection_url
    global mongoClient
    mongoClient = MongoClient(connection_url)


def connect_db(name='influ'):
    global db_name
    db_name = name
    if not mongoClient:
        connect_mongo()
    global mongoDb
    mongoDb = mongoClient[db_name]
    global profiles
    profiles = mongoDb.profiles
    global lists
    lists = mongoDb.lists


def show_db():
    print(f'Current db_name: {db_name}')


def test_repository():
    print(f'Repository works...')


def profiles_by_tags(tags, projection=None):
    return select_profiles({'influmetra.tags': {'$all': tags}}, projection)


def select_profiles(query, projection=None):
    return list(profiles.find(query, projection=projection))


def store_profile(tt_profile):
    profiles.update_one({'_id': tt_profile['_id']}, {'$set': tt_profile}, upsert=True)


def store_list(tt_list):
    lists.update_one({'_id': tt_list['_id']}, {'$set': tt_list}, upsert=True)
