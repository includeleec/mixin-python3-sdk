"""
Mixin Python3 Websocket SDK
base on https://github.com/myrual/mixin_client_demo/blob/master/home_of_cnb_robot.py
code by Lee.c
update at 2018.12.2
"""
import json
import uuid
import gzip
import time
from io import BytesIO
import base64
import websocket
import mixin_config
from mixin_api import MIXIN_API

try:
    import thread
except ImportError:
    import _thread as thread


class MIXIN_WS_API:

    def __init__(self, on_message, on_open=None, on_error=None, on_close=None, on_data=None):

        mixin_api = MIXIN_API(mixin_config)
        encoded = mixin_api.genGETJwtToken('/', "", str(uuid.uuid4()))

        if on_open is None:
            on_open = MIXIN_WS_API.__on_open

        if on_close is None:
            on_close = MIXIN_WS_API.__on_close

        if on_error is None:
            on_error = MIXIN_WS_API.__on_error

        if on_data is None:
            on_data = MIXIN_WS_API.__on_data

        self.ws = websocket.WebSocketApp("wss://blaze.mixin.one/",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    header=["Authorization:Bearer " + encoded.decode()],
                                    subprotocols=["Mixin-Blaze-1"],
                                    on_data=on_data)

        self.ws.on_open = on_open

    """
    run websocket server forever
    """
    def run(self):

        while True:
            self.ws.run_forever()

    """
    ========================
    WEBSOCKET DEFAULT METHOD
    ========================
    """

    """
    on_open default
    """
    @staticmethod
    def __on_open(ws):

        def run(*args):
            print("ws open")
            Message = {"id": str(uuid.uuid1()), "action": "LIST_PENDING_MESSAGES"}
            Message_instring = json.dumps(Message)

            fgz = BytesIO()
            gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
            gzip_obj.write(Message_instring.encode())
            gzip_obj.close()
            ws.send(fgz.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)
            while True:
                time.sleep(1)

        thread.start_new_thread(run, ())

    """
    on_data default
    """
    @staticmethod
    def __on_data(ws, readableString, dataType, continueFlag):
        return

    """
    on_close default
    """

    @staticmethod
    def __on_close(ws):
        return

    """
    on_error default
    """

    @staticmethod
    def __on_error(error):
        print(error)


    """
    =================
    REPLY USER METHOD
    =================
    """

    """
    generate a standard message base on Mixin Messenger format
    """

    @staticmethod
    def writeMessage(websocketInstance, action, params):

        message = {"id": str(uuid.uuid1()), "action": action, "params": params}
        message_instring = json.dumps(message)

        fgz = BytesIO()
        gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
        gzip_obj.write(message_instring.encode())
        gzip_obj.close()
        websocketInstance.send(fgz.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)

    """
    when receive a message, must reply to server
    ACKNOWLEDGE_MESSAGE_RECEIPT ack server received message
    """
    @staticmethod
    def replayMessage(websocketInstance, msgid):
        parameter4IncomingMsg = {"message_id": msgid, "status": "READ"}
        Message = {"id": str(uuid.uuid1()), "action": "ACKNOWLEDGE_MESSAGE_RECEIPT", "params": parameter4IncomingMsg}
        Message_instring = json.dumps(Message)
        fgz = BytesIO()
        gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
        gzip_obj.write(Message_instring.encode())
        gzip_obj.close()
        websocketInstance.send(fgz.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)
        return

    """
    reply a button to user
    """
    @staticmethod
    def sendUserAppButton(websocketInstance, in_conversation_id, to_user_id, realLink, text4Link, colorOfLink="#0084ff"):

        btn = '[{"label":"' + text4Link + '","action":"' + realLink + '","color":"' + colorOfLink + '"}]'

        btn = base64.b64encode(btn.encode('utf-8')).decode(encoding='utf-8')

        params = {"conversation_id": in_conversation_id, "recipient_id": to_user_id, "message_id": str(uuid.uuid4()),
                  "category": "APP_BUTTON_GROUP", "data": btn}
        return MIXIN_WS_API.writeMessage(websocketInstance, "CREATE_MESSAGE", params)

    """
    reply a contact card to user
    """

    @staticmethod
    def sendUserContactCard(websocketInstance, in_conversation_id, to_user_id, to_share_userid):

        btnJson = json.dumps({"user_id": to_share_userid})
        btnJson = base64.b64encode(btnJson.encode('utf-8')).decode('utf-8')
        params = {"conversation_id": in_conversation_id, "recipient_id": to_user_id, "message_id": str(uuid.uuid4()),
                  "category": "PLAIN_CONTACT", "data": btnJson}
        return MIXIN_WS_API.writeMessage(websocketInstance, "CREATE_MESSAGE", params)

    """
    reply a text to user
    """
    @staticmethod
    def sendUserText(websocketInstance, in_conversation_id, to_user_id, textContent):

        textContent = textContent.encode('utf-8')
        textContent = base64.b64encode(textContent).decode(encoding='utf-8')

        params = {"conversation_id": in_conversation_id, "recipient_id": to_user_id, "status": "SENT",
                  "message_id": str(uuid.uuid4()), "category": "PLAIN_TEXT",
                  "data": textContent}
        return MIXIN_WS_API.writeMessage(websocketInstance, "CREATE_MESSAGE", params)

    """
    send user a pay button
    """
    @staticmethod
    def sendUserPayAppButton(webSocketInstance, in_conversation_id, to_user_id, inAssetName, inAssetID, inPayAmount, linkColor="#0CAAF5"):
        payLink = "https://mixin.one/pay?recipient=" + mixin_config.client_id + "&asset=" + inAssetID + "&amount=" + str(
            inPayAmount) + '&trace=' + str(uuid.uuid1()) + '&memo=PRS2CNB'
        btn = '[{"label":"' + inAssetName + '","action":"' + payLink + '","color":"' + linkColor + '"}]'

        btn = base64.b64encode(btn.encode('utf-8')).decode(encoding='utf-8')

        gameEntranceParams = {"conversation_id": in_conversation_id, "recipient_id": to_user_id,
                              "message_id": str(uuid.uuid4()), "category": "APP_BUTTON_GROUP", "data": btn}
        MIXIN_WS_API.writeMessage(webSocketInstance, "CREATE_MESSAGE", gameEntranceParams)




