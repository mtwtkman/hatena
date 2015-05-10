# -*- coding:utf-8 -*-
import os
import sys
from urllib.parse import unquote, parse_qs
import json
import webbrowser

import requests
from requests_oauthlib import OAuth1


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


class OAuth(object):
    '''Hatena OAuth'''
    @property
    def consumer_key(self):
        return self._consumer_key

    @property
    def consumer_secret(self):
        return self._consumer_secret

    @property
    def access_token(self):
        return self._access_token

    @property
    def access_token_secret(self):
        return self._access_token_secret

    @property
    def scope(self):
        return self._scope

    @property
    def user_id(self):
        return self._user_id

    def __init__(self, config_file_name='config.json'):
        self.config_file = os.path.join(os.path.dirname(__file__), config_file_name)
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                self.json_data = json.loads(f.read())
            self._consumer_key = self.json_data.get('CONSUMER_KEY', None)
            self._consumer_secret = self.json_data.get('CONSUMER_SECRET', None)
            self._access_token = self.json_data.get('ACCESS_TOKEN', None)
            self._access_token_secret = self.json_data.get('ACCESS_TOKEN_SECRET', None)
            self._user_id = self.json_data.get('USER_ID', None)
            self._scope = self.json_data.get('SCOPE', None)
        else:
            self._consumer_key, self._consumer_secret = self.config()
            self._access_token = None
            self._access_token_secret = None
            self._scope = None
        self.request_token = None
        self.request_token_secret = None
        self.callback_uri = None
        self.verifier = None

    def get_request_token(self, scope=['read_public'], callback_uri='oob'):
        allowed_scope = ['read_private', 'read_public', 'write_private', 'write_public']
        if not set(scope).issubset(set(allowed_scope+['all'])):
            return 'invalid scope.'
        self.callback_uri = callback_uri
        self._scope = allowed_scope if 'all' in scope else list(set(scope))

        url = 'https://www.hatena.com/oauth/initiate'
        params = {'scope': ','.join(self._scope)} if self._scope is not None and isinstance(self._scope, list) else None
        auth = OAuth1(
            client_key=self._consumer_key,
            client_secret=self._consumer_secret,
            callback_uri=self.callback_uri
        )

        response = requests.post(url, params=params, auth=auth)
        if response.ok:
            content = parse_qs(response.text)
            self.request_token = content['oauth_token'][0]
            self.request_token_secret = content['oauth_token_secret'][0]
            return self.request_token, self.request_token_secret
        else:
            return response.text

    def get_verifier(self, device='pc'):
        urls = {
            'pc': 'https://www.hatena.ne.jp/oauth/authorize',
            'touch': 'https://www.hatena.ne.jp/touch/oauth/authorize',
            'mobile': 'http://www.hatena.ne.jp/mobile/oauth/authorize'
        }
        if self.callback_uri != 'oob':
            return requests.Request('GET', urls[device], params={'oauth_token': self.request_token}).prepare().url

        response = requests.get(urls[device], params={'oauth_token': self.request_token})
        if response.ok:
            webbrowser.open(unquote(response.url))
            self.oauth_verifier = input('input verifier code: ')
            return self.oauth_verifier
        else:
            return response.text

    def get_access_token(self, verifier=None):
        if not (self.request_token and self.request_token_secret):
            return 'Missing `request_token` and `request_token_secret`'
        url = 'https://www.hatena.com/oauth/token'
        auth = OAuth1(
            client_key=self._consumer_key,
            client_secret=self._consumer_secret,
            resource_owner_key=self.request_token,
            resource_owner_secret=self.request_token_secret,
            verifier=self.oauth_verifier if self.callback_uri == 'oob' else verifier
        )

        access_response = requests.post(url, auth=auth)

        if access_response.ok:
            content = parse_qs(access_response.text)
            self._access_token = self.json_data['ACCESS_TOKEN'] = content['oauth_token'][0]
            self._access_token_secret = self.json_data['ACCESS_TOKEN_SECRET'] = content['oauth_token_secret'][0]
            self._user_id = self.json_data['USER_ID'] = content['url_name'][0]
            self.json_data['SCOPE'] = self._scope
            with open(self.config_file, 'w') as f:
                f.write(json.dumps(self.json_data, indent=2, sort_keys=True))
            return self._access_token, self._access_token_secret
        else:
            return access_response.text

    def config(self):
        '''Set CONSUEMR_KEY and CONSUMER_SECRET_KEY newly'''

        self.json_data = {
            'CONSUMER_KEY': input('CONSUMER KEY:'),
            'CONSUMER_SECRET': input('CONSUMER SECRET KEY')
        }
        try:
            with open(self.config_file, 'w') as f:
                f.write(json.dumps(self.json_data, indent=2, sort_keys=True))
        except Exception as e:
            print(e)
        else:
            return self.json_data['CONSUMER_KEY'], self.json_data['CONSUMER_SECRET']
