# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 11:09:49 2022

@author: afish
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from Handler import Handler
import os

# os.environ['FOOSBOT_BOT_TOKEN'] = 'xapp-'
# os.environ['FOOSBOT_BOT_USER_TOKEN'] = 'xoxb-'

# Tokens
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_BOT_USER_TOKEN = os.environ['SLACK_BOT_USER_TOKEN']
app = App(token=SLACK_BOT_TOKEN)

# Initialize classes
HANDLER = Handler(app, SLACK_BOT_TOKEN, SLACK_BOT_USER_TOKEN)

# Connect event decorators with functions calling class functions.
@app.event("message")
def handle_message_events(body, logger):
    HANDLER.handle_message_events(body, logger)

@app.event("app_mention")
def handle_app_mention_events(body, logger):
    HANDLER.handle_app_mention_events(body, logger)
    
    
    
if __name__=="__main__":
    SocketModeHandler(app, SLACK_BOT_TOKEN).start()