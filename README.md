#Install
`python setup.py develop`

example needs `bottle`.

`python setup.py example`

#Usage
##Authorization
```
import hatena import OAuth
oauth = OAuth()
oauth.get_request_token()
oauth.get_verifier()
oauth.get_access_token()
```
Then, `config.json` is created under hatena directory.
