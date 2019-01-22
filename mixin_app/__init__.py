#-*- coding:utf-8 -*-


from flask import Flask

# 初始化flask应用
mixin_app = Flask(__name__)

from mixin_app import views