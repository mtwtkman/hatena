# -*- coding:utf-8 -*-
import os
import sys
import re
import json
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom

import requests
from requests_oauthlib import OAuth1

from .oauth import OAuth


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


class Diary(object):
    '''Hatena diary API'''
    def __init__(self):
        oauth = OAuth()
        self.scope = oauth.scope
        need = ['read_private', 'write_private']
        if set(need) & set(self.scope):
            self.auth = OAuth1(
                client_key=oauth.consumer_key,
                client_secret=oauth.consumer_secret,
                resource_owner_key=oauth.access_token,
                resource_owner_secret=oauth.access_token_secret
            )
            self.user_id = oauth.user_id
            self.base_url = 'http://d.hatena.ne.jp/{}/atom'.format(self.user_id)
            self.collection_url = self.base_url + '/blog'
            self.member_url = self.collection_url + '/{date}/{entry_id}'
            self.draft_collection = self.base_url + '/draft'
            self.draft_member = self.draft_collection + '{entry_id}'
        else:
            raise ValueError('Need to authorize with {}'.format(' or '.join(need)))

    def get(self):
        response = requests.get(url=self.base_url, auth=self.auth)
        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def get_entries(self, title, page=1, draft=False):
        url = self.draft_collection if draft else self.collection_url
        response = requests.get(url=url, params={'page': page}, auth=self.auth)
        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def post_entry(self, title, content, updated=None, draft=False):
        if updated and isinstance(updated, datetime) is False:
            raise TypeError('Updated is must be datetime type. Passed updated is {}'.format(type(updated)))

        entry = Element('entry')
        entry.attrib = {'xmlns': 'http://purl.org/atom/ns#'}
        _title = SubElement(entry, 'title')
        _title.text = title
        _content = SubElement(entry, 'content')
        _content.attrib = {'type': 'text/plain'}
        _content.text = content
        _updated = SubElement(entry, 'updated')
        if updated:
            # default timezone is JST
            utc_offset = re.sub(r'((?:\+|-)\d{2})(\d{2})', r'\1:\2', updated.strftime('%z')) if updated.tzinfo else '+09:00'
            _updated.text = updated.strftime('%Y-%m-%dT%H:%M:%S{utc_offset}'.format(utc_offset=utc_offset))
        else:
            _updated.text = None

        data = minidom.parseString(ET.tostring(entry)).toxml(encoding='utf-8')

        url = self.draft_collection if draft else self.collection_url
        response = requests.post(url=url, data=data, auth=self.auth)

        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def get_entry(self, date, entry_id, draft=False):
        url = self.draft_member.format(entry_id=entry_id) if draft else self.member_url.format(date=date, entry_id=entry_id)
        response = requests.get(url=url, auth=self.auth)
        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def edit_entry(self, date, entry_id, title, content, updated=None, draft=False):
        entry = Element('entry')
        entry.attrib = {'xmlns': 'http://purl.org/atom/ns#'}
        _title = SubElement(entry, 'title')
        _title.text = title
        _content = SubElement(entry, 'content')
        _content.attrib = {'type': 'text/plain'}
        _content.text = content
        _updated = SubElement(entry, 'updated')
        _updated.text = updated

        data = minidom.parseString(ET.tostring(entry)).toxml(encoding='utf-8')

        url = self.draft_member.format(entry_id=entry_id) if draft else self.member_url.format(date=date, entry_id=entry_id)
        response = requests.put(url=url, data=data, auth=self.auth)

        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def delete_entry(self, date, entry_id, draft=False):
        url = self.draft_member.format(entry_id=entry_id) if draft else self.member_url.format(date=date, entry_id=entry_id)
        response = requests.get(url=url, auth=self.auth)
        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def publish(self, entry_id):
        response = requests.put(url=self.draft_member.format(entry_id=entry_id), data='X-HATENA-PUBLISH: 1', auth=self.auth)
        if response.ok:
            return ET.fromstring(response.text)
        else:
            return {'status_code': response.status_code, 'reason': response.reason}

    def gen_prettified_xml(self, src):
        return (i for i in minidom.parseString(ET.tostring(src)).toxml(encoding='utf-8').decode().split('\n'))
