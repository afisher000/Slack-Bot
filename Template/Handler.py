# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 11:53:55 2022

@author: afish
"""

class Handler():
    def __init__(self, app, SLACK_BOT_TOKEN, SLACK_BOT_USER_TOKEN):
        self.app = app
        self.SLACK_BOT_TOKEN = SLACK_BOT_TOKEN
        self.SLACK_BOT_USER_TOKEN = SLACK_BOT_USER_TOKEN

    def handle_message_events(self, body, logger):
        logger.info(body)
        
    def handle_app_mention_events(self, body, logger):
        logger.info(body)
