# -*- coding:utf-8 -*-
import os
import sys
from urllib.parse import unquote, parse_qs
import json
import webbrowser

import requests
from requests_oauthlib import OAuth1


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


class Hatena(object):
    def __init__(self, config_file_name='config.json'):
        self.config_file = os.path.join(os.path.dirname(__file__), config_file_name)

        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                self.json_data = json.loads(f.read())
            self.consumer_key = self.json_data.get('CONSUMER_KEY', None)
            self.consumer_secret = self.json_data.get('CONSUMER_SECRET', None)
            self.access_token = self.json_data.get('ACCESS_TOKEN', None)
            self.access_token_secret = self.json_data.get('ACCESS_TOKEN_SECRET', None)
        else:
            self.config()
            self.consumer_key = self.json_data.get('CONSUMER_KEY', None)
            self.consumer_secret = self.json_data.get('CONSUMER_SECRET', None)

    def _get_request_token(self, scope):
        url = 'https://www.hatena.com/oauth/initiate'
        scope = {'scope': ','.join(scope)} if scope is not None else None
        auth = OAuth1(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            callback_uri='oob'
        )

        response = requests.post(url, params=scope, auth=auth)

        if response.ok:
            content = parse_qs(response.text)
            return content['oauth_token'][0], content['oauth_token_secret'][0]
        else:
            return response.text

    def oauth(self, scope=['read_public'], device='pc'):
        (request_token, request_token_secret) = self._get_request_token(scope)
        urls = {
            'pc': 'https://www.hatena.ne.jp/oauth/authorize',
            'smart': 'https://www.hatena.ne.jp/touch/oauth/authorize',
            'mobile': 'http://www.hatena.ne.jp/mobile/oauth/authorize'
        }

        _response = requests.get(urls[device], params={'oauth_token': request_token})

        webbrowser.open(unquote(_response.url))
        oauth_verifier = input('input verifier code: ')

        url = 'https://www.hatena.com/oauth/token'
        auth = OAuth1(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=request_token,
            resource_owner_secret=request_token_secret,
            verifier=oauth_verifier
        )

        response = requests.post(url, auth=auth)

        if response.ok:
            content = parse_qs(response.text)
            self.access_token = self.json_data['ACCESS_TOKEN'] = content['oauth_token'][0]
            self.access_token_secret = self.json_data['ACCESS_TOKEN_SECERT'] = content['oauth_token_secret'][0]
            with open(self.config_file, 'w') as f:
                f.write(json.dumps(self.json_data, indent=2, sort_keys=True))
            return response
        else:
            return response.text

    def config(self):
        self.json_data = {
            'CONSUMER_KEY': input('CONSUMER KEY:'),
            'CONSUMER_SECRET': input('CONSUMER SECRET KEY')
        }
        with open(self.config_file, 'w') as f:
            f.write(json.dumps(self.json_data, indent=2, sort_keys=True))
