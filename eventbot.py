#!/usr/bin/python3
import asyncio, discord
import dataset, json
import sys, os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

# Obtain config from config.json
if os.path.isfile('config.json'):
    with open('config.json') as config_file:
        config = json.loads(config_file.read())
else:
    print('Could not find config.json!', file=sys.stderr)
    sys.exit()


# command messages
creator_id = '175753699224715264' # my discord user id
github_link = 'https://github.com/desolt/EventBot'
info_embed = discord.Embed(title='EventBot', 
                           type='rich', 
                           description='Helps discord admins manage events!\n\n' \
                                       'Created by <@{}>'.format(creator_id),
                           url=github_link)
info_embed.set_thumbnail(url='http://www.thefamouspeople.com/profiles/images/huey-long-2.jpg')

commands_message = '```\n' \
                   'eb!info - shows this menu.\n' \
                   'eb!event <name> <date> <time> - schedules an event\n' \
                   'eb!events - shows the current scheduled events\n' \
                   'eb!cancel <name> - cancels an event\n' \
                   'eb!subscribe <name> - subscribes to an event\n' \
                   'eb!unsubscribe <name> - unsubscribes from an event\n' \
                   '```'

# Bot stuff
bot = discord.Client()

db = dataset.connect('mysql://{}:{}@{}/eventbot'
        .format(config['sql']['user'], config['sql']['pass'], config['sql']['host']))
event_table = db['events']
subscription_table = db['subscriptions']

# Meat and potatoes
async def check_schedule():
    while True:
        await asyncio.sleep(60) # Wait every minute to check for an event.
        print('Test!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('eb!'):
        await process_command(message.content[3:].split(' '), message)

            

async def process_command(args, message):
    if 'info' in args[0]:
        await bot.send_message(message.channel, embed=info_embed)
        await bot.send_message(message.author,  'Commands:\n{}'.format(commands_message))
        await bot.send_message(message.channel, 'The commands have been DMed to you!')
    elif 'subscribe' in args[0]:
        if len(args) == 2:
            try:
                id = int(args[1])
                event = event_table.find_one(id = id)
                if event is None:
                    await bot.send_message(message.channel, 'That event does not exist!')
                else:
                    subscription_exists = subscription_table.find_one(user_id = message.author.id, 
                                                                      event_id = event['id'])
                    if subscription_exists is None:
                        subscription_table.insert(dict(user_id = message.author.id, 
                                                       event_id = event['id']))
                        await bot.send_message(message.channel, 'You are now subscribed to event {}!'.format(event.id))
                    else:
                        await bot.send_message(message.channel, 'You are already subscribed to that event!')
            except ValueError:
                await bot.send_message(message.channel, 'Invalid ID!')
        else: 
            await bot.send_message(message.channel, 'Invalid arguments!')
    elif not message.channel.is_private:
        if 'event' in args[0]: pass


@bot.event
async def on_ready():
    print('EventBot is now online!')
    await check_schedule()

if __name__ == '__main__':
    bot.run(config['token'])
