# -*- coding: utf-8 -*-
import unittest
import os
import sys


SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(os.path.abspath(SRC_PATH))


class BookmarkRestTest(unittest.TestCase):
    def _getTargetClass(self):
        from hatena import Bookmark
        return Bookmark

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

    def test_rest_post_and_delete(self):
        target_url = 'http://karapaia.livedoor.biz/archives/52191138.html'
        response = self._makeOne().post(target_url, comment='yeah')

        self.assertEqual(response['comment'], 'yeah')

        response = self._makeOne().delete(target_url)

        self.assertEqual(response, 'ok')

    def test_get_entry_success(self):
        target_url = 'http://karapaia.livedoor.biz/archives/52191138.html'
        response = self._makeOne().get_entry(target_url)

        self.assertEqual(response['title'], 'おったまゲーション！動物たちのドラマチックな顔を集めてみた : カラパイア')

    def test_get_entry_failed_by_invalid_url(self):
        target_url = 'hogehoge'
        response = self._makeOne().get_entry(target_url)

        self.assertEqual(response['status_code'], 404)

    def test_get_tags(self):
        target_url = 'http://karapaia.livedoor.biz/archives/52191138.html'
        response = self._makeOne().get_tags(target_url)

        self.assertEqual(response['status'], '200')

    def test_get_my(self):
        response = self._makeOne().get_my()

        self.assertEqual(len(response.keys()), 19)

    def test_get_count_limit_number_of_url(self):
        import random
        import string

        limit_number_of_url = [''.join([random.choice(string.ascii_lowercase) for i in range(10)]) for i in range(50)]
        response = self._makeOne().get_count(limit_number_of_url)

        self.assertEqual(len(response), 50)

    def test_get_count_failed_by_too_many_url(self):
        import random
        import string

        too_many_url = [''.join([random.choice(string.ascii_lowercase) for i in range(10)]) for i in range(51)]
        response = self._makeOne().get_count(too_many_url)

        self.assertEqual(response['status_code'], 414)

    def test_xmlrpc_get_count_with_single_url(self):
        target_url = 'http://d.hatena.ne.jp/'
        response = self._makeOne().xmlrpc_get_count(target_url)
        '''
        Return format:
        <methodResponse>
          <params>
            <param>
              <value>
                <struct>
                  <member>
                    <name>
                    <value>
        '''
        self.assertEqual(len(response[0][0][0][0]), 1) # struct
        self.assertEqual(response[0][0][0][0][0][0].text, target_url) # name

    def test_xmlrpc_get_count_with_multiple_urls(self):
        target_url = ['http://d.hatena.ne.jp/', 'http://b.hatena.ne.jp/', 'http://www.hatena.ne.jp/']
        response = self._makeOne().xmlrpc_get_count(target_url)

        self.assertEqual(len(response[0][0][0][0]), 3) # struct

    def test_xmlrpc_get_total_count_success(self):
        target_url = 'http://d.hatena.ne.jp/'
        response = self._makeOne().xmlrpc_get_total_count(target_url)
        '''
        Return format:
        <methodResponse>
          <params>
            <param>
              <value>
                <int>
        '''

        self.assertTrue(response[0][0][0][0].text)

    def test_xmlrpc_get_toal_count_failed_by_invalid_url(self):
        target_url = 'invalid_url'
        response = self._makeOne().xmlrpc_get_total_count(target_url)

        self.assertEqual(response['status_code'], 404)

    def test_xmlrpc_get_asin_count_with_single_asin(self):
        target_asin = 4774124966
        response = self._makeOne().xmlrpc_get_asin_count(target_asin)
        '''
        Return format:
        <methodResponse>
          <params>
            <param>
              <value>
                <struct>
                  <member>
                    <name>
                    <value>
        '''
        self.assertEqual(len(response[0][0][0][0]), 1) # struct
        self.assertEqual(response[0][0][0][0][0][0].text, str(target_asin)) # name

    def test_xmlrpc_get_asin_count_with_multiple_asins(self):
        target_asin = [4774124966, 4886487319]
        response = self._makeOne().xmlrpc_get_asin_count(target_asin)

        self.assertEqual(len(response[0][0][0][0]), 2) # struct

    def test_get_entry_json(self):
        target_url = 'http://www.hatena.ne.jp/'
        response = self._makeOne().get_entry_json(target_url)

        self.assertEqual(len(response.keys()), 8)

    def test_get_entry_json_lite(self):
        target_url = 'http://www.hatena.ne.jp/'
        response = self._makeOne().get_entry_json(target_url, lite=True)

        self.assertEqual(len(response.keys()), 7)

    def test_search(self):
        target_user_id = 'mtwtk_man'
        response = self._makeOne().search(target_user_id)

        self.assertTrue('bookmarks' in response.keys())


if __name__ == '__main__':
    unittest.main()
