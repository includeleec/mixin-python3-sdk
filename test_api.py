# -*- coding: utf-8 -*-
"""
Mixin API TEST for Python 3.x
env: python 3.x
code by lee.c
update at 2018.12.2
"""
from mixin_api import MIXIN_API
import mixin_config
import time

mixin_api = MIXIN_API()
mixin_api.client_id = mixin_config.client_id
mixin_api.client_secret = mixin_config.client_secret
mixin_api.pay_session_id = mixin_config.pay_session_id
mixin_api.private_key = mixin_config.private_key
mixin_api.asset_pin = mixin_config.pay_pin
mixin_api.pin_token = mixin_config.pin_token


# encrypted_pin = mixin_api_robot.genEncrypedPin()
# print(encrypted_pin)


transfer2user_id = ''

# cuiniubi token asset id
CNB_ASSET_ID = "965e5c6e-434c-3fa9-b780-c50f43cd955c"

# test robot transfer to user_id
for i in range(1, 2):
    r = mixin_api.transferTo(transfer2user_id, CNB_ASSET_ID, 1, "转账次数:" + str(i))
    time.sleep(1)


# mixin_api_robot.getTransfer('13f4c4de-f572-11e8-94cc-00e04c6aa167')
#
#
# mixin_api_robot.getAsset(CNB_ASSET_ID)
#
#
# mixin_api_robot.topAssets()

# mixin_api_robot.snapshot('8f5b244e-cf86-4374-8eaa-c551fd70cd83')

