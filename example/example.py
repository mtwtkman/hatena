# -*- coding:utf-8 -*-
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


from bottle import redirect, run, route, request
from hatena import OAuth, Bookmark


oauth = OAuth()
bookmark = Bookmark()


@route('/')
def index():
    return '''
        <a href="/oauth">oauth</a></br>
        <form action="/bookmark/entry" method="get">
            url: <input name="url" type="text" />
            <input value="get_entry" type="submit" />
        </form>
        <p>
        <form action="/bookmark/count" method="get">
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


@route('/bookmark/entry')
def bookmark_entry():
    return str(bookmark.get_entry(request.query['url']))


@route('/bookmark/count')
def bookmark_count():
    urls = request.query['url'].split(',')
    response = bookmark.get_count(request.query['url'])

    return response


if __name__ == '__main__':
    run(host='localhost', port='5000', debug=True, reloader=True)
