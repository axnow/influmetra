from TwitterAPI import TwitterAPI, TwitterPager
import configuration

GET_USERS_LIMIT = 100

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
    api = TwitterAPI(api_config['tt-api']['key'], api_config['tt-api']['secret'], auth_type='oAuth2', api_version='2')
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
    response = tt_api.request('users', {'ids': ",".join([str(id) for id in chunks[0]]),
                                        'user.fields': user_expansion_str})
    print(f'got response: {response}, status code: {response.status_code}, text={response.text}')
    response.response.raise_for_status()
    val = response.json()['data']
    return val
