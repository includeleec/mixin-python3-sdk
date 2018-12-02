# -*- coding: utf-8 -*-
"""
Mixin API for Python 3.x
This SDK base on 'https://github.com/myrual/mixin_client_demo/blob/master/mixin_api.py'
some method note '?', because can't run right result, may be it will be resolved later.

env: python 3.x
code by lee.c
update at 2018.12.2
"""

from Crypto.PublicKey import RSA
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
import Crypto
import time
from Crypto import Random
from Crypto.Cipher import AES
import hashlib
import datetime
import jwt
import uuid
import json
import requests
from urllib.parse import urlencode


class MIXIN_API:
    def __init__(self, mixin_config):

        # robot's config
        self.client_id = mixin_config.client_id
        self.client_secret = mixin_config.client_secret
        self.pay_session_id = mixin_config.pay_session_id
        self.pay_pin = mixin_config.pay_pin
        self.pin_token = mixin_config.pin_token
        self.private_key = mixin_config.private_key


        self.keyForAES = ""
        # mixin api base url
        self.api_base_url = 'https://api.mixin.one'

    """
    BASE METHON
    """

    def generateSig(self, method, uri, body):
        hashresult = hashlib.sha256((method + uri+body).encode('utf-8')).hexdigest()
        return hashresult

    def genGETPOSTSig(self, methodstring, uristring, bodystring):
        jwtSig = self.generateSig(methodstring, uristring, bodystring)

        return jwtSig


    def genGETSig(self, uristring, bodystring):
        return self.genGETPOSTSig("GET", uristring, bodystring)

    def genPOSTSig(self, uristring, bodystring):
        return self.genGETPOSTSig("POST", uristring, bodystring)

    def genGETJwtToken(self, uristring, bodystring, jti):
        jwtSig = self.genGETSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')

        return encoded

    def genGETListenSignedToken(self, uristring, bodystring, jti):
        jwtSig = self.genGETSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        privKeyObj = RSA.importKey(self.private_key)
        signer = PKCS1_v1_5.new(privKeyObj)
        signature = signer.sign(encoded)
        return signature


    def genPOSTJwtToken(self, uristring, bodystring, jti):
        jwtSig = self.genPOSTSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        return encoded

    def genEncrypedPin(self):
        if self.keyForAES == "":
            privKeyObj = RSA.importKey(self.private_key)

            decoded_result = base64.b64decode(self.pin_token)

            cipher = PKCS1_OAEP.new(key=privKeyObj, hashAlgo=Crypto.Hash.SHA256, label=self.pay_session_id.encode("utf-8"))

            decrypted_msg = cipher.decrypt(decoded_result)

            self.keyForAES = decrypted_msg

        ts = int(time.time())
        tszero = ts % 0x100
        tsone = (ts % 0x10000) >> 8
        tstwo = (ts % 0x1000000) >> 16
        tsthree = (ts % 0x100000000) >> 24


        tszero = chr(tszero).encode('latin1').decode('latin1')
        tsone = chr(tsone)
        tstwo = chr(tstwo)
        tsthree = chr(tsthree)

        tsstring = tszero + tsone + tstwo + tsthree + '\0\0\0\0'

        toEncryptContent = self.pay_pin + tsstring + tsstring

        lenOfToEncryptContent = len(toEncryptContent)
        toPadCount = 16 - lenOfToEncryptContent % 16
        if toPadCount > 0:
            paddedContent = toEncryptContent + chr(toPadCount) * toPadCount
        else:
            paddedContent = toEncryptContent

        iv = Random.new().read(AES.block_size)


        cipher = AES.new(self.keyForAES, AES.MODE_CBC,iv)
        encrypted_result = cipher.encrypt(paddedContent.encode('latin1'))

        msg = iv + encrypted_result
        encrypted_pin = base64.b64encode(msg)

        return encrypted_pin

    """
    COMMON METHON
    """

    """
    generate API url
    """
    def __genUrl(self, path):
        return self.api_base_url + path

    """
    generate GET http request
    """
    def __genGetRequest(self, path, auth_token=""):

        url = self.__genUrl(path)

        if auth_token == "":
            r = requests.get(url)
        else:
            r = requests.get(url, headers={"Authorization": "Bearer " + auth_token})

        result_obj = r.json()
        print(result_obj)
        return result_obj['data']

    """
    generate POST http request
    """
    def __genPostRequest(self, path, body, auth_token=""):

        # generate url
        url = self.__genUrl(path)

        # transfer obj => json string
        body_in_json = json.dumps(body)

        if auth_token == "":
            r = requests.post(url, json=body_in_json)
        else:
            r = requests.post(url, json=body_in_json, headers={"Authorization": "Bearer " + auth_token})

        result_obj = r.json()
        print(result_obj)
        return result_obj

    """
    generate Mixin Network GET http request
    """
    def __genNetworkGetRequest(self, path, body=None, auth_token=""):

        url = self.__genUrl(path)

        if body is not None:
            body = urlencode(body)
        else:
            body = ""

        if auth_token == "":
            token = self.genGETJwtToken(path, body, str(uuid.uuid4()))
            auth_token = token.decode('utf8')

        r = requests.get(url, headers={"Authorization": "Bearer " + auth_token})
        result_obj = r.json()
        print(result_obj)
        return result_obj


    """
    generate Mixin Network POST http request
    """
    def __genNetworkPostRequest(self, path, body, auth_token=""):

        # transfer obj => json string
        body_in_json = json.dumps(body)

        # generate robot's auth token
        if auth_token == "":
            token = self.genPOSTJwtToken(path, body_in_json, str(uuid.uuid4()))
            auth_token = token.decode('utf8')

        # generate url
        url = self.__genUrl(path)

        r = requests.post(url, json=body, headers={"Authorization": "Bearer " + auth_token})
        result_obj = r.json()
        print(result_obj)
        return result_obj

    """
    ============
    MESSENGER PRIVATE APIs
    ============
    auth token need request 'https://api.mixin.one/me' to get.
    """


    """
    Read user's all assets.
    """
    def getMyAssets(self, auth_token):

        return self.__genGetRequest('/assets', auth_token)

    """
    Read self profile.
    """
    def getMyProfile(self, auth_token):
        return self.__genGetRequest('/me', auth_token)

    """
    ?
    Update my preferences.
    """
    def updateMyPerference(self,receive_message_source="EVERYBODY",accept_conversation_source="EVERYBODY"):

        body = {
            "receive_message_source": receive_message_source,
            "accept_conversation_source": accept_conversation_source
        }

        return self.__genPostRequest('/me/preferences', body)


    """
    ?
    Update my profile.
    """
    def updateMyProfile(self, full_name, auth_token, avatar_base64=""):

        body = {
            "full_name": full_name,
            "avatar_base64": avatar_base64
        }

        return self.__genPostRequest('/me', body, auth_token)

    """
    Get users information by IDs.
    """
    def getUsersInfo(self, user_ids, auth_token):
        return self.__genPostRequest('/users/fetch', user_ids, auth_token)

    """
    Get user's information by ID.
    """
    def getUserInfo(self, user_id, auth_token):
        return self.__genGetRequest('/users/' + user_id, auth_token)

    """
    Search user by Mixin ID or Phone Number.
    """
    def SearchUser(self, q, auth_token):
        return self.__genGetRequest('/search/' + q, auth_token)

    """
    Rotate user’s code_id.
    """
    def rotateUserQR(self, auth_token):
        return self.__genGetRequest('/me/code', auth_token)

    """
    Get my friends.
    """
    def getMyFriends(self, auth_token):
        return self.__genGetRequest('/friends', auth_token)

    """
    Create a GROUP or CONTACT conversation.
    """
    def createConv(self, category, conversation_id, participants, action, role, user_id, auth_token):

        body = {
            "category": category,
            "conversation_id": conversation_id,
            "participants": participants,
            "action": action,
            "role": role,
            "user_id": user_id
        }

        return self.__genPostRequest('/conversations', body, auth_token)

    """
    Read conversation by conversation_id.
    """
    def getConv(self, conversation_id, auth_token):
        return self.__genGetRequest('/conversations/' + conversation_id, auth_token)


    """
    ============
    NETWORK PRIVATE APIs
    ============
    auth token need robot related param to generate.
    """

    """
    PIN is used to manage user’s addresses, assets and etc. There’s no default PIN for a Mixin Network user (except APP).
    if auth_token is empty, it create robot' pin.
    if auth_token is set, it create messenger user pin.
    """
    def createPin(self, new_pin, old_pin="", auth_token=""):
        body = {
            "old_pin": old_pin,
            "new_pin": new_pin
        }

        return self.__genNetworkPostRequest('/pin/update', body, auth_token)


    """
    Verify PIN if is valid or not. For example, you can verify PIN before updating it.
    if auth_token is empty, it verify robot' pin.
    if auth_token is set, it verify messenger user pin.
    """
    def verifyPin(self, pin, auth_token=""):

        body = {
            "pin": pin
        }

        return self.__genNetworkPostRequest('/pin/verify', body, auth_token)

    """
    Grant an asset's deposit address, usually it is public_key, but account_name and account_tag is used for EOS.
    """
    def deposit(self, asset_id):
        return self.__genNetworkGetRequest(' /assets/' + asset_id)


    """
    withdrawals robot asset to address_id
    Tips:Get assets out of Mixin Network, neet to create an address for withdrawal.
    """
    def withdrawals(self, address_id, amount, memo, trace_id=""):
        encrypted_pin = self.genEncrypedPin()

        if trace_id == "":
            trace_id = str(uuid.uuid1())

        body = {
            "address_id": address_id,
            "pin": encrypted_pin,
            "amount": amount,
            "trace_id": trace_id,
            "memo": memo

        }

        return self.__genNetworkPostRequest('/withdrawals/', body)


    """
    Create an address for withdrawal, you can only withdraw through an existent address.
    """
    def createAddress(self, asset_id, public_key="", label="", account_name="", account_tag=""):

        encrypted_pin = self.genEncrypedPin()
        body = {
            "asset_id": asset_id,
            "pin": encrypted_pin,
            "public_key": public_key,
            "label": label,
            "account_name": account_name,
            "account_tag": account_tag
        }

        return self.__genNetworkPostRequest('/addresses/', body)


    """
    Delete an address by ID.
    """
    def delAddress(self, address_id):

        encrypted_pin = self.genEncrypedPin()

        body = {"pin": encrypted_pin}

        return self.__genNetworkPostRequest('/addresses/' + address_id + '/delete', body)


    """
    Read an address by ID.
    """
    def getAddress(self, address_id):
        return self.__genNetworkGetRequest('/addresses' + address_id)

    """
    Transfer of assets between Mixin Network users.
    """
    def transferTo(self, to_user_id, to_asset_id, to_asset_amount, memo, trace_uuid=""):

        # generate encrypted pin
        encrypted_pin = self.genEncrypedPin()

        body = {'asset_id': to_asset_id, 'counter_user_id': to_user_id, 'amount': str(to_asset_amount),
                'pin': encrypted_pin.decode('utf8'), 'trace_id': trace_uuid, 'memo': memo}
        if trace_uuid == "":
            body['trace_id'] = str(uuid.uuid1())

        return self.__genNetworkPostRequest('/transfers', body)

    """
    Read transfer by trace ID.
    """
    def getTransfer(self, trace_id):
        return self.__genNetworkGetRequest('/transfers/trace/' + trace_id)

    """
    Verify a transfer, payment status if it is 'paid' or 'pending'.
    """
    def verifyPayment(self, asset_id, opponent_id, amount, trace_id):

        body = {
            "asset_id": asset_id,
            "opponent_id": opponent_id,
            "amount": amount,
            "trace_id": trace_id
        }

        return self.__genNetworkPostRequest('/payments', body)

    """
    Read asset by asset ID.
    """
    def getAsset(self, asset_id):
        return self.__genNetworkGetRequest('/assets/' + asset_id)

    """
    Read external transactions (pending deposits) by public_key and asset_id, use account_tag for EOS.
    """
    def extTrans(self, asset_id, public_key, account_tag, account_name, limit, offset):

        body = {
            "asset": asset_id,
            "public_key": public_key,
            "account_tag": account_tag,
            "account_name": account_name,
            "limit": limit,
            "offset": offset
        }

        return self.__genNetworkGetRequest('/external/transactions', body)


    """
    Create a new Mixin Network user (like a normal Mixin Messenger user). You should keep PrivateKey which is used to sign an AuthenticationToken and encrypted PIN for the user.
    """
    def createUser(self, session_secret, full_name):

        body = {
            "session_secret": session_secret,
            "full_name": full_name
        }

        return self.__genNetworkPostRequest('/users', body)


    """
    ===========
    NETWORK PUBLIC APIs
    ===========
    """

    """
    Read top valuable assets of Mixin Network.
    """
    def topAssets(self):
        return self.__genGetRequest('/network')

    """
    Read public snapshots of Mixin Network.
    """
    def snapshots(self, offset, asset_id, order='DESC',limit=100):
        # TODO: SET offset default(UTC TIME)
        body = {
            "limit":limit,
            "offset":offset,
            "asset":asset_id,
            "order":order
        }

        return self.__genGetRequest('/network/snapshots', body)


    """
    Read public snapshots of Mixin Network by ID.
    """
    def snapshot(self, snapshot_id):
        return self.__genGetRequest('/network/snapshots/' + snapshot_id)