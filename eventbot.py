#!/usr/bin/python3
import asyncio, discord
import dataset, json
import logging, sys, os
from datetime import datetime, timedelta
from enum import Enum

zones = {
    'UTC': timedelta(hours =  0),
    'EST': timedelta(hours = -4),
    'EDT': timedelta(hours = -4),
    'CDT': timedelta(hours = -5),
    'CST': timedelta(hours = -6),
    'MST': timedelta(hours = -7),
    'PST': timedelta(hours = -8),
    # Best timezones end around here :(
    'ECT': timedelta(hours =  1),
    'EET': timedelta(hours =  2),
    'MSK': timedelta(hours =  3),
    'JST': timedelta(hours =  9),
    'KST': timedelta(hours =  9),
    'CST': timedelta(hours =  8),
    'IST': timedelta(hours =  5, minutes = 30),
}

class ErrorMessages(Enum):
    def __str__(self):
        return str(self.value)

    INVALID_ARG  = 'Invalid arguments!'
    PERMISSION   = 'You do not have permission to use this command!'
    BAD_EVENT    = 'That event does not exist!'
    BAD_ID       = 'Invalid ID!'
    BAD_PAGE_NUM = 'Invalid page number!'

class EventBot(discord.Client):
    def __init__(self):
        # Logging
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # MySQL/dataset
        self.db = dataset.connect('mysql://{}:{}@{}/eventbot'
                             .format(config['sql']['user'], config['sql']['pass'], config['sql']['host']))
        self.event_table = self.db['events']
        self.subscription_table = self.db['subscriptions']

        super().__init__()


    async def on_ready(self):
        await self.change_presence(game = discord.Game(name='eb!info | https://github.com/desolt/EventBot'))
        self.logger.info('Servers joined: {}'.format(len(self.servers)))
        self.logger.info('Events pending: {}'.format(self.event_table.count()))
        self.logger.info('EventBot is now online!')
        await self.check_schedule()

    async def on_server_join(self, server):
        self.logger.info('Joined server {} ("{}")'.format(server.id, server.name))

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.author.bot:
            return # Don't respond to bots to prevent potential spam.

        if message.content.startswith('eb!'):
            args = message.content[3:].split(' ')
            from commands import commands
            cmd = commands.get(args[0])
            if cmd is not None:
                await cmd(self, args, message)

    async def on_member_remove(self, member):
        if member is member.server.me: return # Don't notify ourselves.

        events = self.event_table.find(serverid = member.server.id)
        for event in events:
            self.subscription_table.delete(eventid = event['id'], userid = member.id)
        await self.send_message(member, 'Hey! I noticed you left {} so your subscriptions there have automatically been removed'
                .format(member.server.name))

    async def on_server_remove(self, server):
        events = self.event_table.find(serverid = server.id)
        for event in events:
            self.subscription_table.delete(eventid = event['id'])
        self.event_table.delete(serverid = server.id)
        self.db['server_settings'].delete(serverid = server.id)

    async def check_schedule(self):
        while True:
            for event in self.event_table.all():
                if datetime.utcnow() < event['startsat']:
                    continue

                channel = await self.get_event_channel(self.get_server(event['serverid']))

                await self.send_message(channel, 'Event "{}" (#{}) has started!'.format(event['name'], event['id']))
                for userid in self.subscription_table.find(eventid = event['id']):
                    try:
                        user = await self.get_user_info(userid['userid'])
                        await self.send_message(user, 'Event "{}" has started!'.format(event['name']))
                    except discord.NotFound: pass
                if 'repeat' not in event or not event['repeat']:
                    self.subscription_table.delete(eventid = event['id'])

                if 'repeat' in event and event['repeat']: 
                    # Delays the event to next week.
                    startsat = event['startsat']
                    dtobj = startsat + timedelta(days = 7),
                    self.event_table.update(dict(startsat = dtobj[0], id = event['id']), ['id'])
                else:
                    self.subscription_table.delete(eventid = event['id'])
                    self.event_table.delete(id = event['id'])
                self.logger.info('Event #{} has started!'.format(event['id']))

            await asyncio.sleep(60) # Wait every minute to check for an event.

    async def get_event_channel(self, server):
        channel = self.db['server_settings'].find_one(serverid = server.id)
        if channel is None:
            channel = server.default_channel
        else:
            try:
                channel = self.get_channel(channel['eventchannel'])
            except KeyError: channel = None
            if channel is None: return server.default_channel
        return channel

    async def set_event_channel(self, server, channel):
        settings = dict(eventchannel = channel.id, serverid = server.id)
        if self.db['server_settings'].find_one(serverid = server.id) is None:
            self.db['server_settings'].insert(settings)
        else:
            self.db['server_settings'].update(settings, ['serverid'])

    async def get_timezone(self, server):
        settings = self.db['server_settings'].find_one(serverid = server.id)
        if settings is None:
            return 'UTC'

        try:
            return settings['zone']
        except KeyError:
            return 'UTC'

    async def set_timezone(self, server, zone):
        if zones.get(zone) is None:
            raise ValueError('Unsupported timezone!')

        settings = self.db['server_settings'].find_one(serverid = server.id)
        if settings is None:
            self.db['server_settings'].insert(dict(serverid = server.id, zone = zone))
        else:
            self.db['server_settings'].update(dict(serverid = server.id, zone = zone), ['serverid'])

if __name__ == '__main__':
    # Obtain config from config.json
    if os.path.isfile('config.json'):
        with open('config.json') as config_file:
            config = json.loads(config_file.read())
            bot = EventBot()
            bot.run(config['token'])
    else:
        print('Could not find config.json!', file=sys.stderr)
    
