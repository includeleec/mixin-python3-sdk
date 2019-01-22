# -*- coding:utf-8 -*-


from flask import (
    request,make_response)
import json
from mixin_app import mixin_app as app
from functools import wraps
from mixin_api import MIXIN_API
import mixin_config

# == cross_domain ===
'''It's the code that let cross_domain_possible'''

def allow_cross_domain(fun):

    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst

    return wrapper_fun

# === mixin api ===
mixin_api = MIXIN_API(mixin_config)

# === create_address ===

@app.route('/create_address/<asset_id>', methods=['POST'])
@allow_cross_domain
def create_address(asset_id):
    payload = json.loads(request.get_data())
    print(payload)

    result = mixin_api.createAddress(asset_id,
                                     payload["pubkey"],
                                     payload["label"])
    print(result)
    return json.dumps(result)


@app.route('/create_eos_address/<asset_id>', methods=['POST'])
@allow_cross_domain
def create_eos_address(asset_id):
    payload = json.loads(request.get_data())

    result = mixin_api.createAddress(asset_id,
                                     payload["pubkey"],
                                     payload["label"],
                                     payload["account_name"],
                                     payload["account_tag"],
                                     )
    print(result)
    return json.dumps(result)

# === query ===
@app.route('/assets/<asset_id>', methods=['GET'])
@allow_cross_domain
def read_asset(asset_id):
    return json.dumps(mixin_api.getAsset())

@app.route('/top_assets', methods=['GET'])
@allow_cross_domain
def read_top_asset():
    return json.dumps(mixin_api.topAssets())

@app.route('/transfer/<trace_id>', methods=['GET'])
@allow_cross_domain
def query_transfer(trace_id):
    return json.dumps(mixin_api.getTransfer())

# === transfer ===
@app.route('/transfer_to/<to_user_id>', methods=['POST'])
@allow_cross_domain
def tranfer_to(to_user_id):
    payload = json.loads(request.get_data())

    result = mixin_api.transferTo(to_user_id,
                                     payload["asset_id"],
                                     payload["amount"],
                                     payload["memo"],
                                     )
    print(result)
    return json.dumps(result)


