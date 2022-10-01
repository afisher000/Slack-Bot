# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 11:53:55 2022

@author: afish
"""
from Blocks import Blocks
import re

class Handler():
    def __init__(self, app, SLACK_BOT_TOKEN, SLACK_BOT_USER_TOKEN):
        self.app = app
        self.SLACK_BOT_TOKEN = SLACK_BOT_TOKEN
        self.SLACK_BOT_USER_TOKEN = SLACK_BOT_USER_TOKEN
        self.Blocks = Blocks()  
        
    def parse_call(self, text, say):
        regex = re.compile('^([\w\s]*)\(([^\)]*)\)$')
        try:
            groups = regex.search(text).groups()
            keyword, item = [group.strip().lower() for group in groups]
        except:
            keyword = None
            item = None
        
        return keyword, item

    def handle_cancellation(self, ack, body, logger):
        ack()
        ts = body['message']['ts']
        channel_id = body['channel']['id']
        self.app.client.chat_delete(token=self.SLACK_BOT_USER_TOKEN,
                                   channel=channel_id, 
                                   ts=ts,
                                   blocks=None)
        return
        
    def handle_message_events(self, body, logger):
        logger.info(body)
        
    def handle_app_mention_events(self, body, logger):
        logger.info(body)
