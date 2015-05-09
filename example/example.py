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
        <a href="/oauth">oauth</a></br>
        <form action="/hatebu/entry" method="get">
            url: <input name="url" type="text" />
            <input value="get_entry" type="submit" />
        </form>
        <p>
        <form action="/hatebu/count" method="get">
            url: <input name="url" type="text" />
            <input value="get_count" type="submit" />
        </form>
    '''


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


@route('/hatebu/entry')
def hatebu_entry():
    return str(hatebu.get_entry(request.query['url']))


@route('/hatebu/count')
def hatebu_count():
    urls = request.query['url'].split(',')
    response = hatebu.get_count(request.query['url'])

    return response


if __name__ == '__main__':
    run(host='localhost', port='5000', debug=True, reloader=True)
