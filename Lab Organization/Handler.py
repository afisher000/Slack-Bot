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

        
class Handler():
    def __init__(self, app, SLACK_BOT_TOKEN, SLACK_BOT_USER_TOKEN):
        self.labmap = pd.read_csv('lab_organization.csv')
        self.app = app
        self.SLACK_BOT_USER_TOKEN = SLACK_BOT_USER_TOKEN
        self.SLACK_BOT_TOKEN = SLACK_BOT_TOKEN
        self.Blocks = Blocks()
        self.possible_commands = '''Function calls:
            find(item)
            add(item)
            move(index)
            addlocation(room, location)'''
        
    def parse_call(self, text, say):
        regex = re.compile('^([\w\s]*)\(([^\)]*)\)$')
        try:
            groups = regex.search(text).groups()
            keyword, item = [group.strip().lower() for group in groups]
        except:
            keyword = None
            item = None
        
        return keyword, item
        
    def add_item(self, item, channel):
        
        blocks = [self.Blocks.plain_text_input('text_input_id', 'Item', 'plain_text_input-action',
                                               initial_value = item),
                  self.Blocks.static_select('room_id', 'Room:', self.labmap.room.unique(),
                                            action_id='room_selection_adding'),
                  self.Blocks.static_select('location_id', 'Location:', self.labmap.location.unique()),
                  self.Blocks.actions(self.Blocks.button('cancel_id','','Cancel', action_id='cancel_message')['accessory'],
                                      self.Blocks.button('submit_id','','Add to Database', action_id='database_submission')['accessory']
                                      )
                  ]
        self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN, 
                                 channel=channel,
                                 text='Default text',
                                 blocks=blocks)
    
    def move_item(self, index, channel):
        index = int(index) #convert str to int
        if index not in self.labmap.index:
            self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN,
                                             channel=channel,
                                             text='Index not in table...')
            return
        
        item, room, location = self.labmap.loc[index]
        locations = self.labmap[self.labmap.room==room].location.unique()
        
        
        blocks = [self.Blocks.plain_text(str(index)),
                  self.Blocks.plain_text_input('text_input_id', 'Item', 'plain_text_input-action',
                                                initial_value = item),
                  self.Blocks.static_select('room_id', 'Room:', self.labmap.room.unique(),
                                            action_id='room_selection_moving',
                                            initial_option=self.Blocks.option_object(room)),
                  self.Blocks.static_select('location_id', 'Location:', locations,
                                            initial_option=self.Blocks.option_object(location)),
                  self.Blocks.actions(self.Blocks.button('cancel_id','','Cancel', action_id='cancel_message')['accessory'],
                                      self.Blocks.button('submit_id','','Change Location in Database', action_id='moving_submission')['accessory']
                                      )
                  ]
        
        self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN, 
                                         channel=channel,
                                         text='Default text',
                                         blocks=blocks)
        
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
        

    def handle_moving_submission(self, ack, body, logger):
        ack()
        
        index = int(body['message']['blocks'][0]['elements'][0]['text'])
        room = body['state']['values']['room_id']['room_selection_moving']['selected_option']['value']
        item = body['state']['values']['text_input_id']['plain_text_input-action']['value']
        location = body['state']['values']['location_id']['static_select-action']['selected_option']['value']
        
        # Update table and save
        self.labmap.loc[index] = [item, room, location]
        self.labmap.to_csv('lab_organization.csv', index=False)
        
        # Update message
        ts = body['message']['ts']
        channel_id = body['channel']['id']
        updated_message = f'Edited entry {index}: {item}, {location}, {room}'
        self.app.client.chat_delete(token=self.SLACK_BOT_USER_TOKEN,
                               channel=channel_id, 
                               ts=ts,
                               blocks=None)
        self.app.client.chat_postMessage(token=self.SLACK_BOT_USER_TOKEN, 
                                    channel=channel_id,
                                    text=updated_message)
        logger.info(body)
        
    def handle_room_selection_moving(self, ack, body, logger):
        ack()
        
        pickle.dump(body, open('body.pkl','wb'))
        ts = body['message']['ts']
        channel_id = body['channel']['id']
        room = body['state']['values']['room_id']['room_selection_moving']['selected_option']['value']
        locations = self.labmap[self.labmap.room==room].location.unique()
        
        blocks = body['message']['blocks']
        blocks[3]['accessory']['options'] = self.Blocks.options_dict(locations)
        if 'initial_option' in blocks[3]['accessory']:
            del blocks[3]['accessory']['initial_option']
            
        blocks[2]['accessory']['initial_option'] = self.Blocks.option_object(room)
        
        self.app.client.chat_update(token=self.SLACK_BOT_USER_TOKEN,
                                channel=channel_id, 
                                ts=ts,
                                text='nan',
                                as_user=True,
                                blocks=blocks)
        
    def handle_room_selection_adding(self, ack, body, logger):
        ack()
        #pickle.dump(body, open('body.pkl', 'wb'))
        room = body['state']['values']['room_id']['room_selection_adding']['selected_option']['value']
        item = body['state']['values']['text_input_id']['plain_text_input-action']['value']
        
        blocks = body['message']['blocks']
        blocks[2]['accessory']['options'] = self.Blocks.options_dict(self.labmap[self.labmap.room==room].location.unique())
        blocks[1]['accessory']['initial_option'] = self.Blocks.option_object(room)

        ts = body['message']['ts']
        channel_id = body['channel']['id']
        self.app.client.chat_update(token=self.SLACK_BOT_USER_TOKEN,
                                channel=channel_id, 
                                ts=ts,
                                text='nan',
                                as_user=True,
                                blocks=blocks)
        logger.info(body)
        
    def handle_cancel_message(self, ack, body, logger):
        ack()
        ts = body['message']['ts']
        channel_id = body['channel']['id']
        self.app.client.chat_delete(token=self.SLACK_BOT_USER_TOKEN,
                                    channel=channel_id, 
                                    ts=ts,
                                    blocks=None)
        return
        
    def handle_database_submission(self, ack, body, logger):
        ack()
        room = body['state']['values']['room_id']['room_selection_adding']['selected_option']['value']
        location = body['state']['values']['location_id']['static_select-action']['selected_option']['value']
        item = body['state']['values']['text_input_id']['plain_text_input-action']['value']

        # Add to database and save
        self.labmap.loc[len(self.labmap)] = [item, room, location]
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
        
    def handle_message_events(self, body, logger, event, say):
        keyword, item = self.parse_call(event['text'], say)
        
        if keyword=='find':
            self.find_item(item, event['channel'])

        elif keyword=='add':
            self.add_item(item, event['channel'])

            
        elif keyword=='addlocation':
            args = item.split(',')
            if len(args)==2:
                room, location = [arg.strip().lower() for arg in args]
            else:
                say(token=self.SLACK_BOT_USER_TOKEN, text='Wrong number of arguments\naddloaction(room, location)')
                
            self.labmap.loc[len(self.labmap)] = ['', room, location]
            self.labmap.to_csv('lab_organization.csv', index=False)
            
            say(token = self.SLACK_BOT_USER_TOKEN, text=f'Successfully added \"{location}\" in \"{room}\"')
            
        elif keyword=='move':
            self.move_item(item, event['channel'])
            
        elif keyword=='help':
            say(token=self.SLACK_BOT_USER_TOKEN,
                text=self.possible_commands)

        logger.info(body)