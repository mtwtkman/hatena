# -*- coding: utf-8 -*-
import unittest
import os
import sys
import json


SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(os.path.abspath(SRC_PATH))


class HatebuTest(unittest.TestCase):
    def _getTargetClass(self):
        from hatena import Hatebu
        return Hatebu

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_rest_get_success(self):
        target_url = 'http://www.slideshare.net/supermomonga/super-cool-presentation-at-vimconf2014'
        response = self._makeOne().get(target_url)

        self.assertEqual(len(response.keys()), 10)

    def test_rest_get_error(self):
        target_url = 'unknown'
        response = self._makeOne().get(target_url)

        self.assertEqual(response['status_code'], 404)

    def test_rest_post(self):
        target_url = 'http://karapaia.livedoor.biz/archives/52191138.html'


if __name__ == '__main__':
    unittest.main()
