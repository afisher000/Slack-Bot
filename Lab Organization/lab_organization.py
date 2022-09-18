# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 11:09:49 2022

@author: afish
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from Handler import Handler
import os

# Tokens
SLACK_BOT_TOKEN = os.environ['LABBOT_BOT_TOKEN']
SLACK_BOT_USER_TOKEN = os.environ['LABBOT_BOT_USER_TOKEN']
app = App(token=SLACK_BOT_TOKEN)

# Initialize helper classes
HANDLER = Handler(app = app,
                  SLACK_BOT_TOKEN = SLACK_BOT_TOKEN, 
                  SLACK_BOT_USER_TOKEN = SLACK_BOT_USER_TOKEN)

# Connect events
@app.event("message")
def handle_message_events(body, logger, event, say):
    HANDLER.handle_message_events(body, logger, event, say)

    
@app.action("room_selection_adding")
def handle_room_selection_adding(ack, body, logger):
    HANDLER.handle_room_selection_adding(ack, body, logger)
    
@app.action("database_submission")
def handle_database_submission(ack, body, logger):
    HANDLER.handle_database_submission(ack, body, logger)
    logger.info(body)

@app.action("room_selection_moving")
def handle_room_selection_moving(ack, body, logger):
    HANDLER.handle_room_selection_moving(ack, body, logger)

@app.action("moving_submission")
def handle_moving_submission(ack, body, logger):
    HANDLER.handle_moving_submission(ack, body, logger)
    logger.info(body)
    
@app.action("cancel_message")
def handle_cancel_message(ack, body, logger):
    HANDLER.handle_cancel_message(ack, body, logger)
    logger.info(body)
    
# Dummy connections to avoid warnings

    
@app.action('static_select-action')
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)
    
@app.event('app_home_opened')
def handle_app_home_opened_events(body, logger):
    logger.info(body)
    
if __name__=="__main__":
    SocketModeHandler(app, SLACK_BOT_TOKEN).start()