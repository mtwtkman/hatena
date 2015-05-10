# -*- coding:utf-8 -*-
import os
import sys
import json
from xmlrpc.client import dumps as xmlrpc_dumps
from xml.etree import ElementTree as ET

import requests
from requests_oauthlib import OAuth1

from .oauth import OAuth


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


class Hatebu(object):
    '''Hatena bookmark API'''
    def __init__(self, rest_api_version='1'):
        oauth = OAuth()
        self.base_url = 'http://api.b.hatena.ne.jp/{version}/my/'.format(version=rest_api_version)
        self.rest_url = self.base_url + 'bookmark'
        self.xmlrpc_url = 'http://b.hatena.ne.jp/xmlrpc'
        self.auth = OAuth1(
            client_key=oauth.consumer_key,
            client_secret=oauth.consumer_secret,
            resource_owner_key=oauth.access_token,
            resource_owner_secret=oauth.access_token_secret
        )
        self.scope = oauth.scope
        self.user_id = oauth.user_id

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
                return json.loads(response.text)
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            'Need to authorize with {}'.format(need)

    def get_tags(self, url):
        need = 'read_private'
        if need in self.scope:
            response = requests.get(self.base_url+'tags', params={'url': url}, auth=self.auth)
            if response.ok:
                return json.loads(response.text)
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            'Need to authorize with {}'.format(need)

    def get_my(self):
        need = 'read_private'
        if need in self.scope:
            response = requests.get(self.base_url[:-1], auth=self.auth)

            if response.ok:
                return json.loads(response.text)
            else:
                return {'status_code': response.status_code, 'reason': response.reason}
        else:
            'Need to authorize with {}'.format(need)

    def get_count(self, url):
        response = requests.get('http://api.b.st-hatena.com/entry.counts', params={'url': url})

        if response.ok:
            return json.loads(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def xmlrpc_get_count(self, url):
        if isinstance(url, str):
            url = (url,)
        data = xmlrpc_dumps(params=tuple(url), methodname='bookmark.getCount')
        response = requests.post(url=self.xmlrpc_url, data=data)

        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def xmlrpc_get_total_count(self, url):
        data = xmlrpc_dumps(params=(url,), methodname='bookmark.getTotalCount')
        response = requests.post(url=self.xmlrpc_url, data=data)

        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def xmlrpc_get_asin_count(self, asin):
        if isinstance(asin, int):
            asin = (str(asin),)
        elif isinstance(asin, (tuple, list)):
            asin = tuple(map(lambda x: str(x), asin))

        data = xmlrpc_dumps(params=tuple(asin), methodname='bookmark.getAsinCount')
        response = requests.post(url=self.xmlrpc_url, data=data)

        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def get_entry_json(self, url, callback=None, lite=False):
        endpoint = 'http://b.hatena.ne.jp/entry/json/' if lite is False else 'http://b.hatena.ne.jp/entry/jsonlite/'
        response = requests.get(url=endpoint, params={'url': url, 'callback': callback})

        if response.ok:
            return json.loads(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def search(self, user_id=None, q=None, of=None, limit=None, sort=None,):
        if user_id is None:
            return 'please specify user_id'

        endpoint = 'http://b.hatena.ne.jp/{}/search/json'.format(user_id)
        params = {
            'q': q,
            'of': of,
            'limit': limit,
            'sort': sort
        }
        response = requests.get(url=endpoint, params=params, auth=self.auth)

        if response.ok:
            return json.loads(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}
