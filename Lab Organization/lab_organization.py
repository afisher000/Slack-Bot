# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 11:09:49 2022

@author: afish
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from Handler import Handler

# Tokens (can export to environment variable in future)
SLACK_BOT_TOKEN = 'xapp-1-A040W4WP002-4044175780881-119c09e94077fef5269c058d435234009d1ee85836f43f490c419a3319d45c4a'
SLACK_BOT_USER_TOKEN = 'xoxb-4030047472195-4016024311719-OJO1GZn7dUWJCd1mmlRdeZxP'
app = App(token=SLACK_BOT_TOKEN)

# Initialize helper classes
HANDLER = Handler(app = app,
                  SLACK_BOT_TOKEN = SLACK_BOT_TOKEN, 
                  SLACK_BOT_USER_TOKEN = SLACK_BOT_USER_TOKEN)

# Connect events
@app.event("message")
def handle_message_events(body, logger):
    HANDLER.handle_message_events(body, logger)

@app.event("app_mention")
def handle_app_mention_events(body, logger, event, say):
    HANDLER.handle_app_mention_events(body, logger, event, say)
    
@app.action("room_selection")
def handle_room_selection(ack, body, logger):
    HANDLER.handle_room_selection(ack, body, logger)
    
@app.action("database_submission")
def handle_database_submission(ack, body, logger):
    HANDLER.handle_database_submission(ack, body, logger)
    logger.info(body)
    
if __name__=="__main__":
    SocketModeHandler(app, SLACK_BOT_TOKEN).start()