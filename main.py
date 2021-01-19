# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# pytaml, TwitterAPI
# https://github.com/geduldig/TwitterAPI
import pprint

import requests
import yaml
import json

from pymongo import MongoClient
from TwitterAPI import TwitterAPI, TwitterPager

prettyPrinter = pprint.PrettyPrinter(indent=4)
# mongo setup:
# TODO: move connection string to configuration
mongoClient = MongoClient('mongodb://localhost:27017')
mongoDb = mongoClient.influ


def load_api_config(yaml_file):
    with open(yaml_file, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            # print(config)
            return config
        except yaml.YAMLError as exc:
            print(exc)


def build_api():
    api_config = load_api_config('/home/axnow/ttconfig.yaml')
    api = TwitterAPI(api_config['tt-api']['key'], api_config['tt-api']['secret'], auth_type='oAuth2')
    return api


def list_lists(api, account):
    print(f'Trying to get list of lists for account @{account}')
    res = []
    pager = TwitterPager(api, 'lists/ownerships', {'screen_name': account, 'count': 20})
    for response in pager.get_iterator(wait=5):
        res.extend(response['lists'])
    return res
    # response = api.request('lists/ownerships', {'screen_name': account})
    # if response.status_code == requests.codes.ok:
    #     print(f'Headers:\n{response.headers}\n============\n')
    #     json_print(response)
    #
    # else:
    #     print(f'Failed to perform request, result code: {response.status_code}, response: {response.text}')


def fetch_list_members(api, list_slug, owner_screen_name):
    print(f'Trying to fetch list {list_slug}')
    members = []
    pager = TwitterPager(api, 'lists/members', {'slug': list_slug, 'owner_screen_name': owner_screen_name})
    for member in pager.get_iterator(wait=5):
        members.append(member)
        print(f'Got another answer: {member}')
    print(f'Fetched successfully {len(members)} items.')
    for m in members:
        print(m.text)


# Press the green button in the gutter to run the script.
def test_api():
    api = build_api()
    # r = api.request('statuses/show/:%d' % 210462857140252672)
    # jsonPrint(r)
    #
    lists = list_lists(api, 'dziennikarz')
    prettyPrinter.pprint(lists)
    # fetch_list_members(api, 'dziennikarze', 'dziennikarz')
    # print(r.text)


def json_print(r):
    print(json.dumps(r.json(), indent=4, sort_keys=True))


def headerPrettyPrint(response):
    prettyPrinter.pp(response.headers)


if __name__ == '__main__':
    test_api()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
