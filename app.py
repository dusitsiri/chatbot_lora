# import os, re, json
# from datetime import datetime, date, timedelta
# from flask import Flask, request, abort
# from googletrans import Translator
# import requests
# from linebot import (
#     LineBotApi, WebhookHandler
# )
# from linebot.exceptions import (
#     InvalidSignatureError
# )
# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage,
# )

# app = Flask(__name__)
# translator = Translator()

# channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
# channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# line_bot_api = LineBotApi(channel_access_token)
# handler = WebhookHandler(channel_secret)

# @app.route('/')
# def homepage():
#     the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

#     return """
#     <h1>Hello Translator-Bot</h1>
#     <p>It is currently {time}.</p>
#     <img src="http://loremflickr.com/600/400">
#     """.format(time=the_time)

# @app.route("/callback", methods=['POST'])
# def callback():
#     # get X-Line-Signature header value
#     signature = request.headers['X-Line-Signature']

#     # get request body as text
#     body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)

#     # handle webhook body
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         abort(400)

#     return 'OK'

# def translate_text(text):
#     en_text = translator.translate(text, dest='en').text
#     return en_text

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     text = event.message.text
#     translated = translate_text(text)
#     line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=translated))
    

# if __name__ == "__main__":
#     app.run(debug=True, use_reloader=True)


import json
import os

from flask import Flask
from flask import request
from flask import make_response

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("lorabot-firebase-adminsdk-rkp0u-5a6cea0466.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():

    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    # Parsing the POST request body into a dictionary for easy access.
    req_dict = json.loads(request.data)
    print(req_dict)
    # Accessing the fields on the POST request boduy of API.ai invocation of the webhook
    intent = req_dict["queryResult"]["intent"]["displayName"]

    if intent == 'ความหมายของ LoRa':
        doc_ref = db.collection(u'ความหมายของ LoRa').document(u'0zNx5yghCTkkTKvLUV7e')
        doc = doc_ref.get().to_dict()

        lora_meaning = doc['lora_meaning']
        picture = doc['picture']
        speech = f'{lora_meaning} \n{picture}'

    elif intent == 'ไม่เกี่ยวกับ LoRa' :
        doc_ref = db.collection(u'ไม่เกี่ยวกับ LoRa').document(u'T4EiYrOKRxqATjfJyyhK')
        doc = doc_ref.get().to_dict()
        
        asking = doc['asking']
        speech = f'{asking}'
    
    else: 
        speech = "กรุณาลองใหม่อีกครั้ง"

    res = makeWebhookResult(speech)

    return res


def makeWebhookResult(speech):

    return {
  "fulfillmentText": speech
    }


if __name__ == '__main__':
    app.run()