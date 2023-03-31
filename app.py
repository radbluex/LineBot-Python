from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,ImageSendMessage

from urllib import parse

import configparser

import requests
import pandas as pd

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['x-line-signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 信息事件
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    
    profile = line_bot_api.get_profile(event.source.user_id)

    name = profile.display_name
    if(event.message.text == "加入"):
        print("加入")
        urlpath = 'https://tokien40.com/image/SaveDataInTXT.php'
        line = {
            'displayName': name,
            'uid': profile.user_id,
            }
        headers = {"charset":"utf-8"}
        test_res = requests.post(urlpath,headers=headers,data=line)

        if test_res.ok:
            print(test_res.text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "感謝您的加入,請先完成檢測再做查詢")
            )
        
    elif(event.message.text == "查詢"):
        imageURL = "https://tokien40.com/image/upload/"+parse.quote(name.encode('utf-8'))+".png"
        print(name+"查詢")

        r = requests.head(imageURL)

        if(r.status_code == requests.codes.ok):
            message = [
                ImageSendMessage(
                    original_content_url = imageURL,
                    preview_image_url = imageURL
                ),
                TextSendMessage(text = "感謝您查詢,這是您的證書")
            ]
        else:
            message = [TextSendMessage(text = "尚無證書,請等待key in完成")]
            
        line_bot_api.reply_message(
            event.reply_token,
            message
        )

if __name__ == "__main__":
    app.run()
