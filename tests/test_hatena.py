# -*- coding: utf-8 -*-
import unittest
import os
import sys
import json


SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(os.path.abspath(SRC_PATH))


class HatenaTests(unittest.TestCase):
    def setUp(self):
        import tempfile
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
        from api.hatena import Hatena
        return Hatena

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_get_access_token(self):
        response = self._makeOne().oauth(scope=['read_public', 'write_private'])
        self.assertTrue(response.ok)


if __name__ == '__main__':
    unittest.main()
