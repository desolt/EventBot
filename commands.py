import discord
from eventbot import ErrorMessages, get_event, get_event_channel, set_event_channel

# command messages
creator_id = '175753699224715264' # my discord user id
github_link = 'https://github.com/desolt/EventBot'
info_embed = discord.Embed(title='EventBot', 
                           type='rich', 
                           description='Helps discord admins manage events!\n\n' \
                                       'Created by <@{}>'.format(creator_id),
                           url=github_link)
info_embed.set_thumbnail(url='http://www.thefamouspeople.com/profiles/images/huey-long-2.jpg')

commands_message = '```css\n' \
                   'eb!info - shows this menu.\n' \
                   'eb!eventchannel <channel>\n' \
                   'eb!event <name> <mm/dd/yy> <hh:mm UTC> - schedules an event\n' \
                   'eb!repeat <id> - toggles whether an event should repeat each week.\n' \
                   'eb!events [page #] - shows the current scheduled events\n' \
                   'eb!cancel <id> - cancels an event\n' \
                   'eb!subscribe <id> - subscribes to an event\n' \
                   'eb!unsubscribe <id> - unsubscribes from an event\n' \
                   'eb!subscriptions [page #] - lists subscribed events (DM only)\n' \
                   '```'



async def info(bot, args, message):
    if len(args) == 1:
        await bot.send_message(message.channel, embed = info_embed)
        await bot.send_message(message.author, 'Commands:\n{}'.format(commands_message))
        if not message.channel.is_private: # No point in saying commands have been DMed in the DMs.
            await bot.send_message(message.channel, 'The commands have been DMed to you!')
    else:
        await bot.send_message(message.channel, ErrorMessages.INVALID_ARG)

async def eventchannel(bot, args, message):
    if len(args) == 1:
        channel = await get_event_channel(message.server, bot)
        await bot.send_message(message.channel, 'The event channel is <#{}>.'.format(channel.id))
    elif len(args) == 2:
        try:
            new_channel = message.channel_mentions[0]
            await set_event_channel(message.server, new_channel)
            await bot.send_message(message.channel, '<#{}> is now the event channel!'.format(new_channel.id))
        except KeyError:
            await bot.send_message(message.channel, 'No channel mentioned! ex: eb!eventchannel #general')
    else:
        await bot.send_message(message.channel, ErrorMessages.INVALID_ARG)

commands = {
    'info': info,
    'help': info,
    'eventchannel': eventchannel,
}
