# -*- coding: utf-8 -*-
import unittest
import os
import sys
import json


SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(os.path.abspath(SRC_PATH))


class OAuthTest(unittest.TestCase):
    def setUp(self):
        self.config_file = os.path.join(SRC_PATH, 'api', 'config.json')
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                self.origin_config = json.loads(f.read())
        else:
            self.origin_config = None

    def tearDown(self):
        if self.origin_config:
            with open(self.config_file, 'w') as f:
                f.write(json.dumps(self.origin_config, indent=2, sort_keys=True))

    def _getTargetClass(self):
        from hatena import OAuth
        return OAuth

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_only_invalid_scope_is_failed(self):
        msg = 'invalid scope.'
        response = self._makeOne().get_request_token(scope=['nil_scope'])
        self.assertEqual(response, msg)

    def test_invalid_scope_included_is_failed(self):
        msg = 'invalid scope.'
        response = self._makeOne().get_request_token(scope=['nil_scope', 'read_public'])
        self.assertEqual(response, msg)

    def test_valid_duplicated_scope_allowed(self):
        response = self._makeOne().get_request_token(scope=['read_public', 'read_public', 'write_private'])
        self.assertTrue(isinstance(response, tuple))

    def test_argument_all_replaced_to_allowed_four_scopes(self):
        allowed_scope = ['read_private', 'read_public', 'write_private', 'write_public']
        obj = self._makeOne()
        response = obj.get_request_token(scope=['all'])
        self.assertTrue(isinstance(response, tuple))
        self.assertEqual(obj.scope, allowed_scope)

    def test_get_access_token(self):
        obj = self._makeOne()
        obj.get_request_token(scope=['all'])
        obj.get_verifier()
        response = obj.get_access_token()
        self.assertTrue(isinstance(response, tuple))


if __name__ == '__main__':
    unittest.main()
