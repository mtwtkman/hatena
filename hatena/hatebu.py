# -*- coding:utf-8 -*-
import os
import sys
import json

import requests
from requests_oauthlib import OAuth1

from .oauth import OAuth


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


class Hatebu(object):
    '''Hatena bookmark API'''
    def __init__(self, rest_api_version='1'):
        self.base_url = 'http://api.b.hatena.ne.jp/{version}/my/'.format(version=rest_api_version)
        self.rest_url = self.base_url + 'bookmark'
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
            response = requests.get(self.rest_url, params={'url': url}, auth=self.auth)
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

            response = requests.post(self.rest_url, params=params, auth=self.auth)
            if response.ok:
                return json.loads(response.text)
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            return 'Need to authorize with {}'.format(' or '.join(need))

    def delete(self, url):
        need = ['write_public', 'write_private']
        if set(need) & set(self.scope):
            response = requests.delete(self.rest_url, params={'url': url}, auth=self.auth)
            if response.status_code is 204:
                return 'ok'
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            return 'Need to authorize with {}'.format(' or '.join(need))

    def get_entry(self, url):
        need = 'read_private'
        if need in self.scope:
            response = requests.get(self.base_url.replace('my/', 'entry'), params={'url': url}, auth=self.auth)

            if response.ok:
                return response.text
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            'Need to authorize with {}'.format(need)

    def get_tags(self, url):
        need = 'read_private'
        if need in self.scope:
            response = requests.get(self.base_url+'tags', params={'url': url}, auth=self.auth)
            if response.ok:
                return response.text
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            'Need to authorize with {}'.format(need)

    def get_my(self):
        need = 'read_private'
        if need in self.scope:
            response = requests.get(self.base_url[:-1], auth=self.auth)

            if response.ok:
                return response.text
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            'Need to authorize with {}'.format(need)


