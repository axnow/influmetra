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


def get_profile(id):
    return profiles.find_one({'_id': id})


def save_profile(tt_profile, tags=None, timestamp=datetime.datetime.now()):
    profile_id = int(tt_profile['id'])
    orig_profile = get_profile(profile_id)
    if orig_profile:
        mongo_entry = {
            'profile': tt_profile,
            'timestamp': timestamp,
            'name': tt_profile['name']
        }
        if tags:
            mongo_entry['tags'] = tags
        history_extension = {
            'profile_history': {'timestamp': orig_profile['profile'], 'profile': orig_profile['profile']}}
        profiles.update_one({'_id': profile_id}, {'$set': mongo_entry, '$push': history_extension})
    else:
        mongo_entry = {'_id': profile_id, 'profile': tt_profile, 'tags': tags if tags else [], 'timestamp': timestamp,
                       'name': tt_profile['name'], 'profile_history': []}
        profiles.update_one({'_id': profile_id}, {'$set': mongo_entry}, upsert=True)


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


def select_lists(query=None, projection=None):
    if not query:
        query = {}
    return list(lists.find(query, projection=projection))
