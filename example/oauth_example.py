# -*- coding:utf-8 -*-
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


from bottle import redirect, run, route, request
from hatena import OAuth, Hatebu


oauth = OAuth()
hatebu = Hatebu()


@route('/')
def index():
    return '''
        <a href='/oauth'>oauth</a></br>
        <a href="hatebu/entry">hatebu entry</a>'''


@route('/oauth')
def verify():
    oauth.get_request_token(scope=['all'], callback_uri='http://localhost:5000/oauth_callback')
    redirect(oauth.get_verifier())


@route('/oauth_callback')
def oauth_callback():
    verifier = request.query['oauth_verifier']
    oauth.get_access_token(verifier)
    if oauth.access_token and oauth.access_token_secret:
        redirect('/')
    else:
        return 'oops...'

@route('/hatebu/entry/<url>')
def hatebu_entry(url):
    return str(hatebu.get_entry(url))


if __name__ == '__main__':
    run(host='localhost', port='5000', debug=True)
