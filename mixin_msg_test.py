from flask import Flask, redirect, request
import requests
import json

import mixin_config
from mixin_api import MIXIN_API

mixin_api = MIXIN_API(mixin_config)


# 启动 Flask
app = Flask(__name__)


@app.route('/')
def index():
    # 1. 获得用户的授权 Request Authorization Code

    scope = 'PROFILE:READ+PHONE:READ+CONTACTS:READ+ASSETS:READ'

    get_auth_code_url = 'https://mixin.one/oauth/authorize?client_id='+ mixin_config.client_id+'&scope='+ scope +'&response_type=code'
    return redirect(get_auth_code_url)


@app.route('/user')
def user():

    # 2. 取得 Authorization Token
    auth_token = get_auth_token()


    data = mixin_api.getMyProfile(auth_token)

    data_friends = mixin_api.getMyFriends(auth_token)

    data_asset = mixin_api.getMyAssets(auth_token)


    return '<h1>mixin api</h1> user id:'+data['user_id'] + '  asset  friend'

# 取得 Authorization Token
def get_auth_token():
    get_auth_token_url = 'https://api.mixin.one/oauth/token'

    # 从 url 中取到 code
    auth_code = request.args.get('code')

    post_data = {
        "client_id": mixin_config.client_id,
        "code": auth_code,
        "client_secret": mixin_config.client_secret,
    }

    r = requests.post(get_auth_token_url, json=post_data)
    r_json = r.json()
    print(r_json)

    auth_token = r_json['data']['access_token']

    return auth_token

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)