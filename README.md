# EventBot

EventBot is a bot that allows server admins to register events and users to subscribe. EventBot was made as a favor for the Wands Discord server, and is public for anyone to use.

## Using

There are three things you typically work with in EventBot - subscriptions, events, and settings. The latter two are only used by admins, where as all users work with subscriptions. For a full list of commands type "eb!info" into your discord server.

### For users:

Users can see all of the active events on a server by typing in "eb!events" on any channel. To subscribe to an event one should do "eb!subscribe <event id>", and to unsubscribe "eb!unsubscribe <event id>". Subscribing means on top of the message the bot will send in the events channel, it will send you a DM when an event starts.

## For admins:

**NOTE**: As of right now your role must have the "Administrator" permission to manage events. This may change in the future.

To create an event type the following:

    eb!event <event name> <mm/dd/yy> <hh:mm>

It is important to note that the event name should not have any spaces in it.

Examples of <mm/dd/yy>:
    07/04/17
    4/20/18

If you need to host an event after this century: tough luck (no one has fun while I'm dead).

Moreover, the time <hh:mm> should be inputted in military time in the UTC time zone.

## Dependencies:

If you're going to run EventBot, you'll need the following:

  * [discord.py](https://github.com/Rapptz/discord.py)
  * dataset

If you're in the project directory, you can easily install these with pip.

    # pip install -r requirements.txt
