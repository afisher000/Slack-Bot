# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 11:09:49 2022

@author: afish
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from Blocks import Blocks
from Handler import Handler
import os

# Tokens
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_BOT_USER_TOKEN = os.environ['SLACK_BOT_USER_TOKEN']
app = App(token=SLACK_BOT_TOKEN)



# Class can be moved to different file

# Initialize classes
BLOCKS = Blocks()
HANDLER = Handler()

# Connect event decorators with functions calling class functions.
@app.event("message")
def handle_message_events(body, logger):
    HANDLER.handle_message_events(body, logger)

@app.event("app_mention")
def handle_app_mention_events(body, logger):
    HANDLER.handle_app_mention_events(body, logger)
    
    
    
if __name__=="__main__":
    SocketModeHandler(app, SLACK_BOT_TOKEN).start()