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


# def fetch_list_members(api, list_slug, owner_screen_name):
def fetch_list_members(api, list_slug, owner_screen_name):
    print(f'Trying to fetch list {list_slug}')
    members = []
    pager = TwitterPager(api, 'lists/members', {'slug': list_slug, 'owner_screen_name': owner_screen_name, 'count': 500})
    for member in pager.get_iterator(wait=5):
        members.append(member)
        print(f'Got another answer: {member}')
    print(f'Fetched successfully {len(members)} items.')
    return members


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


def object_pretty_print(response):
    prettyPrinter.pprint(response.headers)


def save_list(tt_list, members):
    print(f'Trying to save list {tt_list["full_name"]} with {len(members)}')
    tt_list['members'] = members
    tt_list['_id'] = tt_list['id']
    prettyPrinter.pprint(tt_list)


def prepare_lists(api, account):
    lists = list_lists(api, account)
    res = []
    for l in lists:
        print(f'Fetching members for list {l["full_name"]}...')
        list_members = fetch_list_members(api, l["slug"], account)
        res.append((l, list_members))
    return res


def do_fetch_and_save_lists():
    api = build_api()
    res = prepare_lists(api, 'dziennikarz')
    prettyPrinter.pprint(res)


if __name__ == '__main__':
    do_fetch_and_save_lists()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
