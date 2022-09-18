# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 11:53:55 2022

@author: afish
"""
import pandas as pd
import numpy as np
import re
from Blocks import Blocks
import pickle

# TO IMPLEMENT:
    # addlocation(room, location)
        # Add empty string item with new room and location to table
        # Include yes/no confirmation
    
    # move(index, room, location)
        # index of table, room and location are optional
        # Present menu with submit/cancel button
        
class Handler():
    def __init__(self, app, SLACK_BOT_TOKEN, SLACK_BOT_USER_TOKEN):
        self.labmap = pd.read_csv('lab_organization.csv')
        self.app = app
        self.SLACK_BOT_USER_TOKEN = SLACK_BOT_USER_TOKEN
        self.SLACK_BOT_TOKEN = SLACK_BOT_TOKEN
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
        
    def find_item(self, item, channel):
        matches = self.labmap[self.labmap.item.str.contains(item)]
        if len(matches)>0:
            self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN, 
                                             channel=channel,
                                             text='Database Results:',
                                             blocks = [self.Blocks.markdown(matches.to_markdown())])
        else:
            self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN, 
                                             channel=channel,
                                             text='No matches...')
        return
    
    def add_item_blocks(self, item, room=None):
        if room is None:
            locations = self.labmap.location.unique()
        else:
            locations = self.labmap[self.labmap.room==room].location.unique()

        blocks = [self.Blocks.plain_text(item),
                  self.Blocks.static_select('room_id', 'Room:', self.labmap.room.unique(),
                                            action_id='room_selection'),
                  self.Blocks.static_select('location_id', 'Location:', locations),
                  self.Blocks.actions(self.Blocks.button('cancel_id','','Cancel', action_id='cancel_message')['accessory'],
                                      self.Blocks.button('submit_id','','Add to Database', action_id='database_submission')['accessory'])]
        
        return blocks
        
        
    def handle_cancellation(self, ack, body, logger):
        ack()
        ts = body['message']['ts']
        channel_id = body['channel']['id']
        self.app.client.chat_delete(token=self.SLACK_BOT_USER_TOKEN,
                                   channel=channel_id, 
                                   ts=ts,
                                   blocks=None)
        return
    def handle_message_events(self, body, logger, event, say):
        print(f'{event["channel"]}')
        if event['channel'][0]!='D':
            print('Not a direct message to bot')
            return
        
        keyword, item = self.parse_call(event['text'], say)
        print(f'{keyword},{item}')
        if keyword=='find':
            self.find_item(item, event['channel'])

        elif keyword=='add':
            self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN, 
                                             channel=event['channel'],
                                             text='Default text',
                                             blocks=self.add_item_blocks(item))
            
        elif keyword=='help':
            say(token=self.SLACK_BOT_USER_TOKEN,
                text='''Function calls:
                    @LabBot find(item)
                    @LabBot add(item)''')

        logger.info(body)
        
    def handle_room_selection(self, ack, body, logger):
        ack()
        room = body['state']['values']['room_id']['room_selection']['selected_option']['value']
        item = body['message']['blocks'][0]['elements'][0]['text']

        ts = body['message']['ts']
        channel_id = body['channel']['id']
        self.app.client.chat_update(token=self.SLACK_BOT_USER_TOKEN,
                                channel=channel_id, 
                                ts=ts,
                                text='nan',
                                as_user=True,
                                blocks=self.add_item_blocks(item, room=room))
        logger.info(body)
        
    def handle_database_submission(self, ack, body, logger):
        ack()
        room = body['state']['values']['room_id']['room_selection']['selected_option']['value']
        location = body['state']['values']['location_id']['static_select-action']['selected_option']['value']
        item = body['message']['blocks'][0]['elements'][0]['text']

        # Add to database and save
        self.labmap.loc[len(self.labmap)] = [item, location, room]
        self.labmap.to_csv('lab_organization.csv', index=False)
        
        # Update message
        ts = body['message']['ts']
        channel_id = body['channel']['id']
        updated_message = f'Added row: {item}, {location}, {room}'
        self.app.client.chat_delete(token=self.SLACK_BOT_USER_TOKEN,
                               channel=channel_id, 
                               ts=ts,
                               blocks=None)
        self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN, 
                                    channel=channel_id,
                                    text=updated_message)
        logger.info(body)