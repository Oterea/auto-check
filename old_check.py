import requests
import json
import time
from datetime import datetime
import logging as logger
import traceback




url = 'http://wechatmeeting.nuist.edu.cn/wechat/book3/book.html?type=eventInfo?eventId=fc5379ac197b421940fffa4c99723e11'


headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/6.8.0(0x16080000) MacWechat/3.8.7(0x13080710) XWEB/1191 Flue',
        'Cookie': 'token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJub3ciOjE3MTY0NjM3NjgsImV4cCI6MTcxNjQ2NzM2OCwidHQiOiJ3ZWNoYXRfcXkiLCJ0IjoiMjAyMzEyNDkwNzkxIn0.OMw494re9nFROPKtsKuMkYrtBu1ZbEcJSrG_4TattVI'
        }


    # 使用get请求访问目标URL，并提供自定义的请求头
response = requests.get(url, headers = headers)

    # 打印响应内容
print(response.text)


