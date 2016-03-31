#!/usr/bin/env python
# coding=utf-8

from flask import Flask
from flask import request

import httplib

import hashlib
import json
import urllib

app = Flask(__name__)

# 日志打印辅助函数，多添加一个回车，方便查看与调试日志
def cclog(s):
    print(s + "\n")

RT_ANYSDK_LOGIN_SERVER = "callback-play.cocos.com"

# cocosplay-demo的参数
RT_PRIVATE_KEY = '3B57E68AD0407E819EDF1B3779FD74C9'
RT_ENHANCED_KEY = 'Y2U5N2ExNWNhZWYwNThiMjI4YmI'

@app.route("/coco_login", methods=['GET', 'POST'])
def coco_login():
    cclog("AnySDK服务器登陆验证...")
    cclog("post value:" + str(request.values))

    ret = 'login failed'

    private_key = RT_PRIVATE_KEY

    if request.method == 'POST':
        cclog("It's post request ...")
        post_key = request.values['private_key']

        if post_key == private_key:
            cclog("private_key is correct!")
            post_data = request.values

            cclog("anysdk server: " + RT_ANYSDK_LOGIN_SERVER)
            anysdk_conn = httplib.HTTPConnection(RT_ANYSDK_LOGIN_SERVER)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
#            headers = {}

            post_str = ''
            first = True
            for key, value in post_data.items():
                if not first:
                    post_str += '&'
                first = False
                post_str += key + '=' + urllib.quote(value.encode("utf-8"), "~")

            cclog("post to anysdk: " + post_str)
            anysdk_conn.request("POST", '/api/User/LoginOauth/', post_str, headers)

            response = anysdk_conn.getresponse()

            if response.status == 200:
                content = response.read()
                print "any_sdk login result:", content
                resp_dict = json.loads(content)
                resp_dict['ext'] = {
                    "accountID": resp_dict["common"]["uid"]
                }
                ret = resp_dict
            else:
                cclog("response status: " + response.status)
    else:
        cclog("private_key is wrong!")

    response = json.dumps(ret, ensure_ascii=False)
    return response


@app.route("/coco_pay", methods=['GET', 'POST'])
def coco_pay():
    cclog("AnySDK服务器发货通知...")

    response = "failure"
    if request.method == 'POST':
        cclog("In the POST method ...")
        #private_data may be refererd to as your own tracking number

        post_data = request.values
        cclog("post_data:" + str(post_data))
        private_data = post_data['private_data']
        server_id = post_data['server_id']
        trade_status = post_data['pay_status']
        channel = post_data['channel_number']
        user_id = post_data['user_id']
        total_fee = post_data['amount']


        sign = post_data['enhanced_sign']

        enhanced_key = RT_ENHANCED_KEY

        if trade_status == '1':
            validated_order = False
            temp_list = []

            for key, value in request.values.items():
                if key != "sign" and key != 'enhanced_sign':
                    temp_list.append([key, value])

            temp_list = sorted(temp_list, cmp=lambda x,y: cmp(x[0], y[0]))

            raw_str = ''

            for item in temp_list:
                raw_str = raw_str + item[1]

            cclog("raw_str:" + raw_str)

            md5_raw_str = hashlib.md5(raw_str.encode("utf-8")).hexdigest().lower()
            local_sign = hashlib.md5(md5_raw_str + enhanced_key).hexdigest().lower()


            if local_sign == sign:
                validated_order = True
                cclog("合法的签名")
            else:
                cclog("不合法的签名")

            if validated_order:

                #支付完成，并且合法，更新支付状态信息或者通知游戏服务器更新数据...
                cclog("合法的订单")
                response = 'ok'
            else:
                response = "Wrong signature."

    return response



# 脚本入口
if __name__ == "__main__":
    app.debug=True
    app.run('192.168.31.194', 8888)


