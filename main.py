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


#
# def save_list(tt_list, members):
#     print(f'Trying to save list {tt_list["full_name"]} with {len(members)}')
#     tt_list['members'] = members
#     tt_list['_id'] = tt_list['id']
#     prettyPrinter.pprint(tt_list)


def fetch_lists_with_members(account, list_slugs):
    lists_by_slug = {}
    if not list_slugs:
        user_lists = tt.list_lists(account)
        lists_by_slug = {l['slug']: l for l in user_lists}
        list_slugs = list(lists_by_slug.keys())
    res = []
    for slug in list_slugs:
        tt_list = tt.fetch_list(account,slug)
        if not tt_list:
            tt_list = tt.fetch_list(account, list_slugs)
        print(f'Fetching members for list {account}/{slug}...')
        list_members = tt.fetch_list_members_by_slug(slug, account)
        res.append((tt_list, list_members))
    return res


def fetch_lists(account, list_slugs=[]):
    if not list_slugs:
        return tt.list_lists(account)
    else:
        tt_lists = []
        for slug in list_slugs:
            tt_lists.append(tt.fetch_list(account, slug))
        return tt_lists


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


def do_fetch_and_save_lists():
    api = build_api()
    res = fetch_lists_with_members('dziennikarz')
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
        repository.store_list(tt_list)
    tt_profile_list = list(tt_profiles.values())
    print(f'Saving profiles, got {len(tt_profile_list)}'
          f' items ({list(map(lambda p: p["name"], tt_profile_list))[0:50]})')
    for tt_profile in tt_profiles.values():
        repository.store_profile(tt_profile)


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


def test_list_fetching():
    show_lists("dziennikarz")
    show_lists("Europarl_PL")
    fetch_lists_with_members("Europarl_PL", ["polscy-eurodeputowani"])


if __name__ == '__main__':
    #
    print('Loading configuration')
    configuration.load_configuration()
    print('Configuration loaded.')
    # test_available_calls()
    repository.connect()

    test_list_fetching()
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
