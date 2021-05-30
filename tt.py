from TwitterAPI import TwitterAPI, TwitterPager
import configuration

tt_api = None


def ensure_tt_initialized():
    global tt_api
    if not tt_api:
        print(f'Twitter connection not initialized, initializing...')
        init_tt()


def init_tt():
    print(f'Initialiizing tt api...')
    global tt_api
    tt_api = build_api()
    print(f'Initialized tt_api successfully.')


def build_api():
    api_config = configuration.config
    api = TwitterAPI(api_config['tt-api']['key'], api_config['tt-api']['secret'], auth_type='oAuth2')
    return api


def list_lists(account):
    ensure_tt_initialized()
    print(f'Trying to get list of lists for account @{account}')
    res = []
    pager = TwitterPager(tt_api, 'lists/ownerships', {'screen_name': account, 'count': 20})
    for response in pager.get_iterator(wait=5):
        res.extend(response['lists'])
    return res


# def fetch_list_members(api, list_slug, owner_screen_name):
def fetch_list_members(list_slug, owner_screen_name):
    print(f'Trying to fetch list {list_slug}')
    members = []
    pager = TwitterPager(tt_api, 'lists/members',
                         {'slug': list_slug, 'owner_screen_name': owner_screen_name, 'count': 1000})
    for member in pager.get_iterator(wait=5):
        members.append(member)
        # print(f'Got another answer: {member}')
    print(f'Fetched successfully {len(members)} items.')
    return members


def fetch_followers_ids(api, user_id):
    print(f'Fetching followers of {user_id}')
    pager = TwitterPager(api, 'followers/ids', {'user_id': user_id})
    followers = []
    for follower in pager.get_iterator(wait=5):
        followers.append(follower)
        print(f'Got another answer: {follower}')
    print(f'Fetched successfully {len(followers)} items.')
    return followers


def check_available_calls():
    ensure_tt_initialized()
    resp = tt_api.request('application/rate_limit_status', {"resources": "followers,statuses,friends,trends,help"})
    print(f'Got quota: {resp.get_quota()}')
    return resp.json()
