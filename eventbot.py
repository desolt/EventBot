#!/usr/bin/python3
import asyncio, discord
import dataset, json
import sys, os
from datetime import datetime
from enum import Enum

# Obtain config from config.json
if os.path.isfile('config.json'):
    with open('config.json') as config_file:
        config = json.loads(config_file.read())
else:
    print('Could not find config.json!', file=sys.stderr)
    sys.exit()



# Bot stuff
bot = discord.Client()

db = dataset.connect('mysql://{}:{}@{}/eventbot'
        .format(config['sql']['user'], config['sql']['pass'], config['sql']['host']))
event_table = db['events']
subscription_table = db['subscriptions']

# Meat and potatoes
async def check_schedule():
    while True:
        for event in event_table.all():
            if datetime.utcnow() < event['startsat']:
                continue

            channel = await get_event_channel(bot.get_server(event['serverid']))

            await bot.send_message(channel, 'Event "{}" (#{}) has started!'.format(event['name'], event['id']))
            for userid in subscription_table.find(eventid = event['id']):
                try:
                    user = await bot.get_user_info(userid['userid'])
                    print('Found user!')
                    await bot.send_message(user, 'Event "{}" has started!'.format(event['name']))
                except discord.NotFound: pass
            if 'repeat' not in event or not event['repeat']:
                subscription_table.delete(eventid = event['id'])

            if 'repeat' in event and event['repeat']: 
                # Delays the event to next week.
                newstartsat = event['startsat'] + datetime.timedelta(days = 7),
                event_table.update(dict(startsat = newstartsat, id = event['id']), ['id'])
            else:
                event_table.delete(id = event['id'])
            print('Event #{} has started!'.format(event['id']))

        await asyncio.sleep(60) # Wait every minute to check for an event.

class ErrorMessages(Enum):
    def __str__(self):
        return str(self.value)

    INVALID_ARG  = 'Invalid arguments!'
    PERMISSION   = 'You do not have permission to use this command!'
    BAD_EVENT    = 'That event does not exist!'
    BAD_ID       = 'Invalid ID!'
    BAD_PAGE_NUM = 'Invalid page number!'

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('eb!'):
        args = message.content[3:].split(' ')
        from commands import commands
        cmd = commands.get(args[0])
        if cmd is not None:
            await cmd(bot, args, message)

async def get_event(id):
    event = event_table.find_one(id = id)
    if event is None:
        raise ValueError('Invalid event ID!')
    return event

async def get_event_channel(server, bot):
    channel = db['server_settings'].find_one(serverid = server.id)
    if channel is None:
        channel = server.default_channel
    else:
        channel = bot.get_channel(channel['eventchannel'])
    return channel

async def set_event_channel(server, channel):
    settings = dict(eventchannel = channel.id, serverid = server.id)
    if db['server_settings'].find_one(serverid = server.id) is None:
        db['server_settings'].insert(settings)
    else:
        db['server_settings'].update(settings, ['serverid'])

@bot.event
async def on_ready():
    await bot.change_presence(game = discord.Game(name='eb!info | https://github.com/desolt/EventBot'))
    print('EventBot is now online!')
    await check_schedule()

if __name__ == '__main__':
    bot.run(config['token'])
