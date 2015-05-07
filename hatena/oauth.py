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

    def __init__(self, config_file_name='config.json'):
        self.config_file = os.path.join(os.path.dirname(__file__), config_file_name)
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                self.json_data = json.loads(f.read())
            self._consumer_key = self.json_data.get('CONSUMER_KEY', None)
            self._consumer_secret = self.json_data.get('CONSUMER_SECRET', None)
            self._access_token = self.json_data.get('ACCESS_TOKEN', None)
            self._access_token_secret = self.json_data.get('ACCESS_TOKEN_SECRET', None)
            self._scope = self.json_data.get('SCOPE', None)
        else:
            self._consumer_key, self._consumer_secret = self.config()
            self._access_token = None
            self._access_token_secret = None
            self._scope = None

    def _get_request_token(self, scope):
        url = 'https://www.hatena.com/oauth/initiate'
        scope = {'scope': ','.join(scope)} if scope is not None and isinstance(scope, list) else None
        auth = OAuth1(
            client_key=self._consumer_key,
            client_secret=self._consumer_secret,
            callback_uri='oob'
        )

        response = requests.post(url, params=scope, auth=auth)

        if response.ok:
            content = parse_qs(response.text)
            return content['oauth_token'][0], content['oauth_token_secret'][0]
        else:
            return response.text

    def get_access_token(self, scope=['read_public'], device='pc'):
        allowed_scope = ['read_private', 'read_public', 'write_private', 'write_public']
        if not set(scope).issubset(set(allowed_scope+['all'])):
            return 'invalid scope.'

        self._scope = allowed_scope if 'all' in scope else list(set(scope))

        (request_token, request_token_secret) = self._get_request_token(self._scope)
        urls = {
            'pc': 'https://www.hatena.ne.jp/oauth/authorize',
            'smart': 'https://www.hatena.ne.jp/touch/oauth/authorize',
            'mobile': 'http://www.hatena.ne.jp/mobile/oauth/authorize'
        }

        verify_response = requests.get(urls[device], params={'oauth_token': request_token})

        webbrowser.open(unquote(verify_response.url))
        oauth_verifier = input('input verifier code: ')

        url = 'https://www.hatena.com/oauth/token'
        auth = OAuth1(
            client_key=self._consumer_key,
            client_secret=self._consumer_secret,
            resource_owner_key=request_token,
            resource_owner_secret=request_token_secret,
            verifier=oauth_verifier
        )

        access_response = requests.post(url, auth=auth)

        if access_response.ok:
            content = parse_qs(access_response.text)
            self._access_token = self.json_data['ACCESS_TOKEN'] = content['oauth_token'][0]
            self._access_token_secret = self.json_data['ACCESS_TOKEN_SECRET'] = content['oauth_token_secret'][0]
            self.json_data['SCOPE'] = self._scope
            with open(self.config_file, 'w') as f:
                f.write(json.dumps(self.json_data, indent=2, sort_keys=True))
            return access_response
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
