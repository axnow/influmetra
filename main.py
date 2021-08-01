# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# pytaml, TwitterAPI
# https://github.com/geduldig/TwitterAPI
import pprint

import configuration
import json

import repository

import tt
from repository import INFLUMETRA_PROPERTY

prettyPrinter = pprint.PrettyPrinter(indent=4)


def test_api():
    lists = tt.list_lists('dziennikarz')
    prettyPrinter.pprint(lists)
    # fetch_list_members(api, 'dziennikarze', 'dziennikarz')
    # print(r.text)


def json_print(r):
    print(json.dumps(r.json(), indent=4, sort_keys=True))


def object_pretty_print(response):
    prettyPrinter.pprint(response.headers)


def fetch_list_with_members(account, slug):
    tt_list = tt.fetch_list(account, slug)
    if not tt_list:
        raise Exception(f'Unable to fetch list {account}/{slug}')
    print(f'Fetching members for list {account}/{slug}...')
    list_members = tt.fetch_list_members_by_slug(slug, account)
    return tt_list, list_members


def fetch_lists_with_members(account, list_slugs):
    if not list_slugs:
        user_lists = tt.list_lists(account)
        list_slugs = [tt_list['slug'] for tt_list in user_lists]
    res = list()
    for slug in list_slugs:
        tt_list, list_members = fetch_list_with_members(account, slug)
        res.append((tt_list, list_members))
    return res


def fetch_and_save_list(account, slug, tags):
    tt_list, tt_members_objects = fetch_list_with_members(account, slug)
    member_ids = [tt_member['id'] for tt_member in tt_members_objects]
    repository.save_list(tt_list, tags, member_ids, timestamp=None)


def fetch_lists(account, list_slugs=[]):
    if not list_slugs:
        return tt.list_lists(account)
    else:
        tt_lists = []
        for slug in list_slugs:
            tt_lists.append(tt.fetch_list(account, slug))
        return tt_lists


def test_followers_api():
    api = build_api()
    ardanowski_id = "1055378302876241921"
    print(f'Fetching followers of {ardanowski_id}')
    followers = fetch_followers_ids(api, ardanowski_id)

    prettyPrinter.pprint(followers)
    print(f'Got total number of followers: {len(followers)}')


def test_available_calls():
    limits = tt.check_available_calls()
    print(f'got limit response: ')
    prettyPrinter.pprint(limits)


def read_lists_definition():
    list_file = 'list_tags.json'
    with open(list_file) as file:
        data = json.load(file)
    return data


# Refresh all the profiles on the list, with update
def refresh_profiles(ids):
    profiles = tt.fetch_users_by_ids(ids)
    for (profile, timestamp) in profiles:
        update_profile(profile, timestamp)
    print(f'Successfully updated {len(profiles)} profiles.')


# Update profile with a new value
def update_profile(profile, timestamp):
    profile_id = profile['id']
    old_profile = repository.get_profile(profile_id)
    if old_profile:
        influ = old_profile[INFLUMETRA_PROPERTY]
        if not influ:
            influ = dict()
        influ['timestamp'] = timestamp
        profile[INFLUMETRA_PROPERTY] = influ
    repository.add_profile_history_entry(profile_id, profile, timestamp)
    repository.update_profile(profile)


def refresh_profiles_by_tags(tags):
    resp = repository.profiles_by_tags(tags)
    ids = [i['id'] for i in resp]
    print(f'Got from repository: response: {resp}, converted to ids: {ids}')
    # raise Exception('Just testing...')
    users = tt.fetch_users_by_ids(ids)
    print(f'Successfully got users: {users}')


def print_list(tt_list):
    printout = dict()
    for item in ["slug", "name", 'member_count']:
        printout[item] = tt_list[item]
    prettyPrinter.pprint(printout)


def show_lists(account):
    print(f'Lists for {account}', )
    tt_lists = fetch_lists(account)
    print(f'Got {len(tt_lists)} lists for {account}')
    for tt_list in tt_lists:
        print_list(tt_list)


#
# def test_list_fetching():
#     # show_lists("dziennikarz")
#     # show_lists("Europarl_PL")
#     tt_list, tt_list_members = fetch_list_with_members("Europarl_PL", "polscy-eurodeputowani")
#     print(f'Got successfully list for europarliment, with {len(tt_list_members)} members.')
#     print_list(tt_list)
#     prettyPrinter.pprint(tt_list_members)
#
#
# def test_fetch_and_save_list():
#     lists = [
#         ("Europarl_PL", "polscy-eurodeputowani", ['mep'])
#     ]
#     for account, slug, tags in lists:
#         print(f'Fetching and saving list: {account}/{slug} with tags: {tags}')
#         fetch_and_save_list(account, slug, tags)


def update_and_save_lists():
    ldefs = read_lists_definition()
    for ldef in ldefs:
        fetch_and_save_list(ldef['owner'], ldef['slug'], ldef['tags'])


def update_list_members_profiles():
    lists = repository.select_lists(projection={'full_name': 1, 'tags': 1, 'members': 1})
    print(f'Fetched {len(lists)} lists from repository')
    # profile_id_set = set()
    profile_id_tags=dict()
    for tt_list in lists:
        for m_id in tt_list['members']:
            if not m_id in profile_id_tags:
                profile_id_tags[m_id]=set(tt_list['tags'])
            else:
                for tag in tt_list['tags']:
                    profile_id_tags[m_id].add(tag)
            # profile_id_set.add(m_id)
    member_count = sum([len(l['members']) for l in lists])
    print(f'After reducing to set got {len(profile_id_tags)} vs original member sum: {member_count}')
    print(f'Preparing to fetch')
    profile_ids = list(profile_id_tags.keys())
    # profile_ids = profile_ids[:10]
    profiles = tt.fetch_users_by_ids(profile_ids)
    print(f'Got {len(profiles)} items in result.')
    saved=0
    for tt_profile in profiles:
        tags = list(profile_id_tags[int(tt_profile['id'])])
        repository.save_profile(tt_profile, tags)
        saved += 1
        if saved % 100 == 0:
            print(f'Successfully saved {saved} profiles, last one: {tt_profile["id"]} {tt_profile["name"]}')
    #and now try to add tags to profiles.


if __name__ == '__main__':
    #
    print('Loading configuration')
    configuration.load_configuration()
    print('Configuration loaded.')
    # test_available_calls()
    repository.connect()

    update_list_members_profiles()
    # update_and_save_lists()
    # test_fetch_and_save_list()
    # test_list_fetching()
    exit(0)
    refresh_profiles_by_tags(['posel'])

    print('Repository testing:')
    print('Connecting to db')
    repository.connect()
    res = repository.profiles_by_tags(['posel'], ['name'])
    prettyPrinter.pprint(res)
    #
    # repository.connect_db()
    # # res = repository.select_profiles({})
    # res = repository.profiles_by_tags(['posel'], ['name'])
    # prettyPrinter.pprint(res)
    # # test_repository()
    # # connect_db('asdef')
    # # show_db()
    # # test_followers_api()
    # # test_available_calls()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
