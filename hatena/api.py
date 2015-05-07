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
            self.config()
            self._consumer_key = self.json_data.get('CONSUMER_KEY', None)
            self._consumer_secret = self.json_data.get('CONSUMER_SECRET', None)

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
        (request_token, request_token_secret) = self._get_request_token(scope)
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
            self._scope = self.json_data['SCOPE'] = scope
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
        with open(self.config_file, 'w') as f:
            f.write(json.dumps(self.json_data, indent=2, sort_keys=True))


class Hatebu(object):
    '''Hatena bookmark API'''
    def __init__(self, rest_api_version='1'):
        self.rest_endpoint = 'http://api.b.hatena.ne.jp/{version}/my/bookmark'.format(version=rest_api_version)
        self.auth = OAuth1(
            client_key=OAuth().consumer_key,
            client_secret=OAuth().consumer_secret,
            resource_owner_key=OAuth().access_token,
            resource_owner_secret=OAuth().access_token_secret
        )
        self.scope = OAuth().scope

    '''
    REST API
    document: http://developer.hatena.ne.jp/ja/documents/bookmark/apis/rest
    '''
    def get(self, url):
        need = ['read_public', 'read_private']
        if set(need) & set(self.scope):
            response = requests.get(self.rest_endpoint, params={'url': url}, auth=self.auth)
            if response.ok:
                return json.loads(response.text)
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            return 'Need to authorize with {}'.format(' or '.join(need))

    def post(self, url, comment=None, tags=None, post_twitter=0, post_facebook=0,
             post_mixi=0, post_evernote=0, send_mail=0, private=0):
        need = ['write_public', 'write_private']
        if set(need) & set(self.scope):
            params = {
                'url': url,
                'post_twitter': post_twitter,
                'post_facebook': post_facebook,
                'post_mixi': post_mixi,
                'post_evernote': post_evernote,
                'send_mail': send_mail
            }
            if comment is not None:
                params['comment'] = comment
            if tags is not None and isinstance(tags, list):
                params['tags'] = tags

            response = requests.post(self.rest_endpoint, params=params, auth=self.auth)
            if response.ok:
                return json.loads(response.text)
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            return 'Need to authorize with {}'.format(' or '.join(need))

    def delete(self, url):
        need = ['write_public', 'write_private']
        if set(need) & set(self.scope):
            response = requests.delete(selef.rest_endpoint, params={'url': url}, auth=self.auth)
            if response.status_code is 204:
                return 'ok'
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            return 'Need to authorize with {}'.format(' or '.join(need))
