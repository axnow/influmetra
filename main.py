# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# pytaml, TwitterAPI
# https://github.com/geduldig/TwitterAPI
import yaml
import json
from TwitterAPI import TwitterAPI

def load_api_config(yaml_file):
    with open(yaml_file, 'r') as stream:
        try:
            config=yaml.safe_load(stream)
            print(config)
            return config
        except yaml.YAMLError as exc:
            print(exc)



# Press the green button in the gutter to run the script.
def test_api():
    api_config=load_api_config('/home/axnow/ttconfig.yaml')
    api = TwitterAPI(api_config['tt-api']['key'], api_config['tt-api']['secret'], auth_type='oAuth2')
    r = api.request('statuses/show/:%d' % 210462857140252672)

    print(json.dumps(r.json(), indent=4, sort_keys=True))
    # print(r.text)


if __name__ == '__main__':
    test_api()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
