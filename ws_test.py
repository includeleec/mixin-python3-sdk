"""
Test Mixin Messenger Robot Websocket methods
code by Lee.c
update at 2018.12.2
"""

from mixin_ws_api import MIXIN_WS_API
from mixin_api import MIXIN_API
import mixin_config

import json
import time
from io import BytesIO
import base64
import gzip

try:
    import thread
except ImportError:
    import _thread as thread


def on_message(ws, message):

    inbuffer = BytesIO(message)

    f = gzip.GzipFile(mode="rb", fileobj=inbuffer)
    rdata_injson = f.read()
    rdata_obj = json.loads(rdata_injson)
    action = rdata_obj["action"]

    if action not in ["ACKNOWLEDGE_MESSAGE_RECEIPT", "CREATE_MESSAGE", "LIST_PENDING_MESSAGES"]:
        print("unknow action")
        return

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        return


    if action == "CREATE_MESSAGE":

        data = rdata_obj["data"]
        msgid = data["message_id"]
        typeindata = data["type"]
        categoryindata = data["category"]
        userId = data["user_id"]
        conversationId = data["conversation_id"]
        dataindata = data["data"]
        created_at = data["created_at"]
        updated_at = data["updated_at"]

        realData = base64.b64decode(dataindata)

        MIXIN_WS_API.replayMessage(ws, msgid)

        print('userId', userId)
        print("created_at",created_at)


        if 'error' in rdata_obj:
            return

        if categoryindata not in ["SYSTEM_ACCOUNT_SNAPSHOT", "PLAIN_TEXT", "SYSTEM_CONVERSATION", "PLAIN_STICKER", "PLAIN_IMAGE", "PLAIN_CONTACT"]:
            print("unknow category")
            return

        if categoryindata == "PLAIN_TEXT" and typeindata == "message":
            realData = realData.lower().decode('utf-8')


            if 'hi' == realData:
                introductionContent = 'welcome to MyFirstRobot\n[hihi] reply n times text\n[c] send a contact card\n[b] send a link button\n[p] you need to pay\n[t] transfer to you'
                MIXIN_WS_API.sendUserText(ws, conversationId, userId, introductionContent)
                return

            if 'hihi' == realData:
                introductionContent = '你好呀 '
                for i in range(3):
                    MIXIN_WS_API.sendUserText(ws, conversationId, userId, introductionContent + str(i))
                    time.sleep(1)
                return

            if 'c' == realData:
                print('send a contact card')
                MIXIN_WS_API.sendUserContactCard(ws, conversationId, userId, "d33f7efd-4b0b-41ff-baa3-b22ea40eb44f")
                return

            if 'b' == realData:
                print('send a link button')
                MIXIN_WS_API.sendUserAppButton(ws, conversationId, userId, "https://github.com/includeleec/mixin-python3-sdk", "点我了解 Mixin Python3 SDK")
                return

            if 'p' == realData:
                print('you need to pay')
                CNB_ASSET_ID = "965e5c6e-434c-3fa9-b780-c50f43cd955c"
                MIXIN_WS_API.sendUserPayAppButton(ws, conversationId, userId, "给点钱吧", CNB_ASSET_ID,  1, "#ff0033")
                return

            if 't' == realData:
                print('transfer to you')
                CNB_ASSET_ID = "965e5c6e-434c-3fa9-b780-c50f43cd955c"
                mixin_api.transferTo(userId, CNB_ASSET_ID, 2, "滴水之恩")
                return

        elif categoryindata == "PLAIN_TEXT":
            print("PLAIN_TEXT but unkonw:")



if __name__ == "__main__":

    mixin_api = MIXIN_API(mixin_config)

    mixin_ws = MIXIN_WS_API(on_message=on_message)

    mixin_ws.run()

