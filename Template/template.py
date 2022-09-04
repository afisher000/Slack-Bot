# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 11:09:49 2022

@author: afish
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from Blocks import Blocks
from Handler import Handler

# Tokens (export to environment variable in future)
SLACK_BOT_TOKEN = 'xapp-1-A040KGDRDDM-4046755270081-10812808d8b9e556e321e35d2d99da877d96b6da4822981f6229272ee4e17a62'
SLACK_BOT_USER_TOKEN = 'xoxb-4030047472195-4034024803267-9CirDmEz1JfSA7D67VKJ9YSp'
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