#!/usr/bin/python3
import asyncio, discord
import dataset, json


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

db = dataset.connect('sqlite:///events.db')
event_table = db['events']

bot = discord.Client()

async def check_schedule():
    while True:
        await asyncio.sleep(60) # Wait every minute to check for an event.
        print('Test!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.is_private:
        pass # TODO: Add subscription
    else:
        if message.content.startswith('eb!'):
            await process_command(message.content[3:].split(' '), message)

async def process_command(args, message):
    if 'info' in args[0]:
        await bot.send_message(message.channel, embed=info_embed)
        await bot.send_message(message.author,  'Commands:\n{}'.format(commands_message))
        await bot.send_message(message.channel, 'The commands have been DMed to you!')
    elif 'events' in args[0]:
        pass
    elif 'event' in args[0]:
        pass

@bot.event
async def on_ready():
    print('EventBot is now online!')

def main():
    loop = asyncio.get_event_loop()
    asyncio.async(check_schedule())

    with open('config.json', 'r') as config_file:
        config = json.loads(config_file.read())
        bot.run(config['token'])

if __name__ == '__main__':
    main()
