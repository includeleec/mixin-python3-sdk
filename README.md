# Mixin Python3 SDK & MicroService
- All methods implement on https://developers.mixin.one/api
- This SDK support Python3.x
- Tutorial Video in https://www.youtube.com/playlist?list=PLMt8rZaHF-0Yj0w6tHeD1vxBA7f7GU-0-

## 1.SDK
### mixin_api.py
- This SDK base on https://github.com/includeleec/mixin-python3-sdk
- You can see Demo in test_api.py

### mixin_ws_api.py
- This SDK base on https://github.com/includeleec/mixin-python3-sdk
- You can see Demo in ws_test.py

## 2.MicroService
Packaging SDK to Restful-API, let Mixin can be called by any Application writing in any Language!
The APIS supply now are as follows:
- Query
    - /assets/<asset_id>
    - /top_assets
    - /transfer/<trace_id>

- Transfer
    - /transfer_to/<to_user_id>
        **params: ** {"asset_id": asset_id, "amount": amount, "memo": memo}
- Create
    -   /create_address/<asset_id>
    **params: ** {"pubkey": pubkey, "label": label}

So, obviously, the repo need u to contribute, Come On,Developer:)!

## TODO

- Packaging functions about websocket to Restful API.
