from TwitterAPI import TwitterAPI, TwitterPager
import configuration
import time

GET_USERS_LIMIT = 100
GET_USERS_DELAY = 3

tt_api11 = None
tt_api2 = None


def ensure_tt_initialized():
    global tt_api11, tt_api2
    if not tt_api11 or not tt_api2:
        print(f'Twitter connection not initialized, initializing...')
        init_tt()


def init_tt():
    print(f'Initialiizing tt api...')
    global tt_api2
    tt_api2 = build_api('2')
    global tt_api11
    tt_api11 = build_api('1.1')
    print(f'Initialized tt_api successfully.')


def build_api(version):
    api_config = configuration.config
    api = TwitterAPI(api_config['tt-api']['key'], api_config['tt-api']['secret'], auth_type='oAuth2',
                     api_version=version)
    return api


# LIST MANAGEMENT
def fetch_list(owner_screen_name, list_slug):
    ensure_tt_initialized()
    print(f"Fetching list {owner_screen_name}/{list_slug}")
    resp = tt_api11.request("lists/show", {"owner_screen_name": owner_screen_name, "slug": list_slug})
    list_json = resp.json()
    print(f"Successfully got result list {owner_screen_name}/{list_slug}, id: {list_json['id']}")
    return list_json


def list_lists(account):
    ensure_tt_initialized()
    print(f'Trying to get list of lists for account @{account}')
    res = []
    pager = TwitterPager(tt_api11, 'lists/ownerships', {'screen_name': account, 'count': 100})
    for response in pager.get_iterator(wait=5):
        res.extend(response['lists'])
    return res


def fetch_list_members_by_request(request):
    members = []
    if not 'count' in request:
        request['count'] = 5000  # maximum permitted value is 5000 here
    pager = TwitterPager(tt_api11, 'lists/members', request)
    for member in pager.get_iterator(wait=5):
        members.append(member)
        # print(f'Got another answer: {member}')
    print(f'Fetched successfully {len(members)} items.')
    return members


# def fetch_list_members(api, list_slug, owner_screen_name):
def fetch_list_members_by_slug(list_slug, owner_screen_name):
    print(f'Trying to fetch list {list_slug}')
    return fetch_list_members_by_request({'slug': list_slug, 'owner_screen_name': owner_screen_name})


# def fetch_list_members(api, list_slug, owner_screen_name):
def fetch_list_members_by_list_id(list_id):
    print(f'Trying to fetch list with id {list_id}')
    return fetch_list_members_by_request({'id': list_id})


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


def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def fetch_users_by_ids(ids):
    ensure_tt_initialized()
    print(f'Fetching users by ids, got {len(ids)} users to fetch ({ids[:10]}{"..." if len(ids) > 10 else ""}).')
    ids = list(set(ids))
    chunks = list(chunk_list(ids, GET_USERS_LIMIT))
    default_user_expansion = ['created_at', 'description', 'entities', 'id', 'location', 'name', 'pinned_tweet_id',
                              'profile_image_url', 'protected', 'public_metrics', 'url', 'username', 'verified',
                              'withheld']

    user_expansion_str = ",".join(default_user_expansion)
    res = list()
    for ids_chunk in chunks:
        time.sleep(GET_USERS_DELAY)
        response = tt_api2.request('users', {'ids': ",".join([str(id) for id in ids_chunk]),
                                             'user.fields': user_expansion_str})
        print(f'got response: {response}, status code: {response.status_code}, text={response.text}')
        response.response.raise_for_status()
        val = response.json()['data']
        res.extend(val)
    return res
