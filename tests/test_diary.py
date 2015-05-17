# -*- coding: utf-8 -*-
import unittest
import os
import sys


SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(os.path.abspath(SRC_PATH))


class DiaryTest(unittest.TestCase):
    def _getTargetClass(self):
        from hatena import Diary
        return Diary

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)


if __name__ == '__main__':
    unittest.main()
