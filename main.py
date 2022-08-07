import os
import json
import itertools
from dataclasses import dataclass

import requests as req
from dotenv import load_dotenv


@dataclass
class Client():
    username_url: str
    tweet_url: str
    bearer_token: str
    proxy: dict


class User():
    def __init__(self, username) -> None:
        self.username = username
    
    def get_id(self, client: Client) -> int:
        try:
            res = req.get(client.username_url+self.username, headers={'Authorization': client.bearer_token},
            proxies=client.proxy)
            data = res.json()
            self.user_id = data['data']['id']

            return self.user_id

        except Exception as ex:
            print(f'An error is occurred {ex}')

    def get_tweets(self, client: Client, params: dict):
        self.get_id(client)
        data = []

        while True:
            try:
                res = req.get(client.tweet_url.format(user_id=self.user_id), headers={'Authorization': client.bearer_token},
                params=params, proxies=client.proxy)

                data.append(res.json()['data'])
                meta = res.json()['meta']

                if meta.get('next_token') is None:
                    break

                params.update({'pagination_token': meta['next_token']})

            except Exception as ex:
                print(f'An error is occurred {ex}')
                
        return data


if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.environ.get('TOKEN')
    USERNAME = os.environ.get('USERNAME_FILE')

    my_client = Client(
    username_url='https://api.twitter.com/2/users/by/username/',
    tweet_url='https://api.twitter.com/2/users/{user_id}/tweets',
    bearer_token=TOKEN,
    proxy={'https': 'http://127.0.0.1:10809'}
    )
    user = User(USERNAME)

    data = list(itertools.chain(*user.get_tweets(my_client, 
    params={'max_results': 100})))

    with open(f'../Data/{user.username}.json', 'w') as file:
        file.write(json.dumps(data, indent=0))