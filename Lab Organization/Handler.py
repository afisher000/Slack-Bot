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
    # move(index, room, location)
        # index of of table (returned with find(item))
        # populate menu with submit/cancel button
        
    # add self.update_table function to add row and save
    
    # whenever a new player is added, additional entries need to be added to ratings.
        
class Handler():
    def __init__(self, app, SLACK_BOT_TOKEN, SLACK_BOT_USER_TOKEN):
        self.labmap = pd.read_csv('lab_organization.csv')
        self.app = app
        self.SLACK_BOT_USER_TOKEN = SLACK_BOT_USER_TOKEN
        self.SLACK_BOT_TOKEN = SLACK_BOT_TOKEN
        self.Blocks = Blocks()
        
    def parse_call(self, text, say):
        regex = re.compile('(<[^>]*>)([\w\s]*)\(([^\)]*)\)')
        try:
            groups = regex.search(text).groups()
            mention, keyword, item = [group.strip() for group in groups]
        except:
            say(token=self.SLACK_BOT_USER_TOKEN, 
                text='''Cannot parse input''')
            keyword = 'help'
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
            placeholder_text = 'Select an item'
        else:
            locations = self.labmap[self.labmap.room==room].location.unique()
            placeholder_text = room

        blocks = [self.Blocks.plain_text(item),
                  self.Blocks.static_select('room_id', 'Room:', self.labmap.room.unique(),
                                            action_id='room_selection',
                                            placeholder_text=placeholder_text),
                  self.Blocks.static_select('location_id', 'Location:', locations),
                  self.Blocks.button('button_id','Add to Database','Submit', 
                                     action_id='database_submission')]
        
        return blocks
        

        
    def handle_message_events(self, body, logger):
        logger.info(body)
        
    def handle_app_mention_events(self, body, logger, event, say):
        keyword, item = self.parse_call(event['text'], say)
        
        if keyword=='find':
            self.find_item(item, event['channel'])

        elif keyword=='add':
            self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN, 
                                             channel=event['channel'],
                                             text='Default text',
                                             blocks=self.add_item_blocks(item))
            
        elif keyword=='addlocation':
            args = item.split(',')
            if len(args)==2:
                room, location = [arg.strip().lower() for arg in args]
            else:
                say(token=self.SLACK_BOT_USER_TOKEN, text='Wrong number of arguments\naddloaction(room, location)')
                
            self.labmap.loc[len(self.labmap)] = ['', room, location]
            self.labmap.to_csv('lab_organization.csv', index=False)
            
            say(token = self.SLACK_BOT_USER_TOKEN, text=f'Successfully added \"{location}\" in \"{room}\"')
            
            
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