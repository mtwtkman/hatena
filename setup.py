# -*- coding:utf-8 -*-
from setuptools import setup, find_packages


__VERSION__ = '0.0.1'

requirements = [
    'flake8==2.4.0',
    'mccabe==0.3',
    'oauthlib==0.7.2',
    'pep8==1.5.7',
    'pyflakes==0.8.1',
    'requests==2.7.0',
    'requests-oauthlib==0.5.0',
]

extras_require = {
    'example': [
        'Beaker==1.7.0',
        'bottle==0.12.8',
    ]
}

params = {
    'name': 'hatena',
    'version': __VERSION__,
    'description': 'hatena API',
    'install_requires': requirements,
    'extras_require': extras_require,
    'author': 'mtwtk_man',
    'author_email': '',
    'url': 'http://github.com/mtwtkman/hatena/',
    'packages': find_packages('hatena'),
    'license': 'WTFPL',
    'download_url': 'https://github.com/mtwtk_man/hatena/tarball/master',
}

setup(**params)
