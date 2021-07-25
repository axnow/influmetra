# mongo setup:
# TODO: move connection string to configuration
import datetime

from pymongo import MongoClient
import configuration

mongo_client = None
mongo_db = None
db_name = None
profiles = None
lists = None

INFLUMETRA_PROPERTY = 'influmetra'


def connect():
    config = configuration.config
    connect_mongo(config)
    connect_db(config['mongo']['db'])


def connect_mongo(config):
    mongo_config = config['mongo']
    url = mongo_config['url']
    global mongo_client
    mongo_client = MongoClient(url)


def connect_db(name='influ'):
    global db_name
    db_name = name
    if not mongo_client:
        connect_mongo()
    global mongo_db
    mongo_db = mongo_client[db_name]
    global profiles
    profiles = mongo_db.profiles
    global lists
    lists = mongo_db.lists


def profiles_by_tags(tags, projection=None):
    return select_profiles({'influmetra.tags': {'$all': tags}}, projection)


def select_profiles(query, projection=None):
    return list(profiles.find(query, projection=projection))


def store_profile(tt_profile):
    profiles.update_one({'_id': tt_profile['_id']}, {'$set': tt_profile}, upsert=True)


def store_list(tt_list):
    lists.update_one({'_id': tt_list['_id']}, {'$set': tt_list}, upsert=True)


def save_list(tt_list_object, tags, member_ids, timestamp):
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.datetime.now()

    mongo_entry = {'_id': tt_list_object['id'], 'list': tt_list_object, 'tags': tags, 'timestamp': timestamp,
                   'full_name': tt_list_object['full_name']}
    if member_ids:
        mongo_entry['members'] = member_ids
    lists.update_one({'_id': mongo_entry['_id']}, {"$set": mongo_entry}, upsert=True)
