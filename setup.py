# -*- coding:utf-8 -*-
from distutils.core import setup


__VERSION__ = '0.0.1'

params = {
    'name': 'hatena',
    'version': __VERSION__,
    'description': 'hatena API',
    'author': 'mtwtk_man',
    'author_email': '',
    'url': 'http://github.com/mtwtkman/hatena/',
    'packages': ['hatena'],
    'license': 'WTFPL',
    'download_url': 'https://github.com/mtwtk_man/hatena/tarball/master',
}

setup(**params)
