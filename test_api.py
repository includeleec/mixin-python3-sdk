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

mixin_api = MIXIN_API(mixin_config)




transfer2user_id = 'd33f7efd-4b0b-41ff-baa3-b22ea40eb44f'  # my user id

# cuiniubi token asset id
CNB_ASSET_ID = "965e5c6e-434c-3fa9-b780-c50f43cd955c"

# test robot transfer to user_id
# for i in range(1, 5):
#     r = mixin_api.transferTo(transfer2user_id, CNB_ASSET_ID, i, "转账次数:" + str(i))
#     time.sleep(1)

mixin_api.getTransfer('bc52ff5a-f610-11e8-8e2a-28c63ffad907')

# mixin_api.getTransfer('13f4c4de-f572-11e8-94cc-00e04c6aa167')
#
#
# mixin_api_robot.getAsset(CNB_ASSET_ID)
#
#
# mixin_api.topAssets()
#
# print('snapshot')
# mixin_api.snapshot('3565a804-9932-4c3c-8280-b0222166eec7')

# 289d6876-79ff-4699-9901-7a670953eef8
mixin_api.snapshot('289d6876-79ff-4699-9901-7a670953eef8')

