# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# pytaml, TwitterAPI
# https://github.com/geduldig/TwitterAPI
import pprint

import requests
import yaml
import json

import repository
# from repository import *

from pymongo import MongoClient
from TwitterAPI import TwitterAPI, TwitterPager

prettyPrinter = pprint.PrettyPrinter(indent=4)


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
    pager = TwitterPager(api, 'lists/members',
                         {'slug': list_slug, 'owner_screen_name': owner_screen_name, 'count': 1000})
    for member in pager.get_iterator(wait=5):
        members.append(member)
        # print(f'Got another answer: {member}')
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


#
# def save_list(tt_list, members):
#     print(f'Trying to save list {tt_list["full_name"]} with {len(members)}')
#     tt_list['members'] = members
#     tt_list['_id'] = tt_list['id']
#     prettyPrinter.pprint(tt_list)


def fetch_lists_with_members(api, account):
    lists = list_lists(api, account)
    res = []
    # lists=list(lists)[0:2]
    for l in lists:
        print(f'Fetching members for list {l["full_name"]}...')
        list_members = fetch_list_members(api, l["slug"], account)
        res.append((l, list_members))
    return res


def extract_list_member_stub(member):
    stub_fields = ['id', 'name', 'screen_name']
    res = dict()
    for field in stub_fields:
        res[field] = member[field]
    return res


def prepare_list_for_store(tt_list, members):
    tt_list['members'] = list(map(extract_list_member_stub, members))
    tt_list['_id'] = tt_list['id']
    return tt_list


def fetch_followers_ids(api, user_id):
    print(f'Fetching followers of {user_id}')
    pager = TwitterPager(api, 'followers/ids', {'user_id': user_id})
    followers = []
    for follower in pager.get_iterator(wait=5):
        followers.append(follower)
        print(f'Got another answer: {follower}')
    print(f'Fetched successfully {len(followers)} items.')
    return followers


def test_followers_api():
    api = build_api()
    ardanowski_id = "1055378302876241921"
    print(f'Fetching followers of {ardanowski_id}')
    followers = fetch_followers_ids(api, ardanowski_id)

    prettyPrinter.pprint(followers)
    print(f'Got total number of followers: {len(followers)}')


def check_available_calls(api):
    resp = api.request('application/rate_limit_status', {"resources": "followers,statuses,friends,trends,help"})
    print(f'Got quota: {resp.get_quota()}')
    return resp.json()


def test_available_calls():
    api = build_api()
    limits = check_available_calls(api)
    print(f'got limit response: ')
    prettyPrinter.pprint(limits)



def do_fetch_and_save_lists():
    api = build_api()
    res = fetch_lists_with_members(api, 'dziennikarz')
    tt_lists = []
    tt_profiles = dict()
    for tt_list, member_list in res:
        tt_lists.append(prepare_list_for_store(tt_list, member_list))
        for member in member_list:
            id = member['id']
            member['_id'] = id
            tt_profiles[id] = member
    # print('\nLists:\n')
    # prettyPrinter.pprint(tt_lists)
    # print('\nProfiles:\n')
    # prettyPrinter.pprint(tt_profiles)

    print(f'Saving lists, got {len(tt_lists)} items ({list(map(lambda l: l["full_name"], tt_lists))})')
    for tt_list in tt_lists:
        mongoDb['lists'].update_one({'_id': tt_list['_id']}, {'$set': tt_list}, upsert=True)
    tt_profile_list = list(tt_profiles.values())
    print(f'Saving profiles, got {len(tt_profile_list)}'
          f' items ({list(map(lambda p: p["name"], tt_profile_list))[0:50]})')
    for tt_profile in tt_profiles.values():
        mongoDb['profiles'].update_one({'_id': tt_profile['_id']}, {'$set': tt_profile}, upsert=True)


if __name__ == '__main__':
    repository.connect_db()
    res = repository.select_profiles({})
    prettyPrinter.pprint(res)
    # test_repository()
    # connect_db('asdef')
    # show_db()
    # test_followers_api()
    # test_available_calls()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
