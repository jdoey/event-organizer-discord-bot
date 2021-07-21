import discord
import asyncio
import string
import random
import datetime
import json
import pymongo
from pymongo import MongoClient
from json.decoder import JSONDecodeError
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)
bot_token = ''

cluster = MongoClient("")
db = cluster["event_message"]
collection = db["event_message"]


@bot.event
async def on_ready():
    global events_channel_id
    events_channel_id = None

    print('Bot is online.')

    with open("eventschannelid.json", "r") as fp:
        try:
            events_channel_id = json.load(fp)
        except JSONDecodeError:
            pass

    if (events_channel_id != None):
        bot.add_cog(start(bot))


@bot.command(name="setembedchannel", description="sets the channel where the embedded messages will be sent\n "
                                                 ";setembedchannel channel_id")
async def setembedchannel(ctx):
    global events_channel_id

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        await ctx.send('Enter channel id of channel that you want the embedded messages to be sent', delete_after=15)
        events_channel_id = await bot.wait_for("message", check=check, timeout=15)
        events_channel_id = events_channel_id.content
        events_channel_id = int(events_channel_id)

        with open("eventschannelid.json", "w") as fp:
            json.dump(events_channel_id, fp)
        with open("eventschannelid.json", "r") as fp:
            events_channel_id = json.load(fp)

        await ctx.send("Success, the bot is now operational", delete_after=3)
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply within 15 seconds!", delete_after=4)
    bot.add_cog(start(bot))


@bot.command(name="addevent", description="creates an event message and sends it to the events channel")
async def addevent(ctx):
    # checks if the user has set the event channel
    try:
        print(events_channel_id)
    except NameError:
        await ctx.send("event channel is not set, use command ;setembedchannel to set the channel you want the "
                       "embedded messages to be sent")
        return

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    # prompts the user who called the command
    try:
        await ctx.send('Enter name of event:', delete_after=30)
        eventName = await bot.wait_for("message", check=check, timeout=15)
        eventName = eventName.content
        await ctx.send('Enter date of event in format MM/DD/YYYY:', delete_after=30)
        eventDate = await bot.wait_for("message", check=check, timeout=15)
        eventDate = eventDate.content
        datetime.datetime.strptime(eventDate, "%m/%d/%Y")
        await ctx.send("Enter time of event in format XX:XX AM/PM:", delete_after=30)
        eventTime = await bot.wait_for("message", check=check, timeout=15)
        eventTime = eventTime.content
        datetime.datetime.strptime(eventTime, "%I:%M %p")
        await ctx.send("Enter the point of contact for the event: ", delete_after=30)
        point_of_contact = await bot.wait_for("message", check=check, timeout=15)
        point_of_contact = point_of_contact.content

    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply within 15 seconds!", delete_after=10)
        return
    except ValueError as err:
        await ctx.send("Incorrect format, redo the command", delete_after=10)
        return

    # creates the embed
    embed = discord.Embed(
        description=eventName,
        color=0x5CDBF0
    )
    embed.add_field(name='Date: ', value=eventDate, inline=True)
    embed.add_field(name='Time: ', value=eventTime, inline=True)
    embed.add_field(name='Point of Contact: ', value=point_of_contact, inline=False)
    embed.set_footer(text="✅ if going || ❔ if unsure || ❌ if not going")

    # sends the embedded message in specified text channel
    channel = bot.get_channel(events_channel_id)
    msg = await channel.send(''.join(random.choices(string.ascii_uppercase + string.digits, k=5)), embed=embed)

    guild = ctx.message.guild

    # creates the role and permissions
    permissions = discord.Permissions(permissions=0x40)
    role = await guild.create_role(name=eventName, permissions=permissions, mentionable=True)


    # creates the planning text channel and permissions
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        role: discord.PermissionOverwrite(read_messages=True)
    }
    txtchannel = await guild.create_text_channel(eventName + " planning", overwrites=overwrites)



    # stores the message ID and role ID to a database
    data_entry = {"_id": msg.id, "roleID": role.id, "txtchannelID": txtchannel.id}
    collection.insert_one(data_entry)
    print("data_entry accepted!")

    # adds reactions to the embedded message
    await msg.add_reaction(emoji="✅")
    await msg.add_reaction(emoji="❔")
    await msg.add_reaction(emoji="❌")


@bot.command(name="deleteevent", description="deletes the specified event \n command is called by passing the name of "
                                             "the event and the unique 5-character code located in the specified "
                                             "embedded message \n\n ex: ;deleteevent \"event_name\" 5_char_code")
async def deleteevent(ctx, eventToDelete: str, ID: str):
    channel = bot.get_channel(events_channel_id)
    allmessages = await channel.history(limit=200).flatten()
    # locates the message and deletes it
    for msg in allmessages:
        if msg.content == ID and msg.author == bot.user:
            query = {"_id": msg.id}
            collection.delete_one(query)
            await msg.delete()

    # deletes the text channel of the event
    eventToDelete_channel = eventToDelete.replace(" ", "-")
    lowercase_channel = eventToDelete_channel.lower()
    existing_channel = discord.utils.get(ctx.guild.channels, name=lowercase_channel + "-planning")
    if existing_channel is not None:
        await existing_channel.delete()
    # deletes the role of the event
    existing_role = discord.utils.get(ctx.guild.roles, name=eventToDelete)
    if existing_role is not None:
        await existing_role.delete()
    await ctx.send('Event has been successfully deleted')


@bot.command(name="changeevent", description="changes the details of the specified event \n command is called by "
                                             "passing the event name, event date, event time, and the unique "
                                             "5-character code located in the specified embedded message \n\n ex: "
                                             ";changeevent \"event_name\" event_date event_time 5_char_code")
async def changeevent(ctx, eventName: str, eventDate: str, eventTime: str, point_of_contact: str, ID: str):
    channel = bot.get_channel(events_channel_id)
    allmessages = await channel.history(limit=200).flatten()
    msgID = None
    # looks through the messages in the specified channel and looks for the message that has the
    # desired ID
    for msg in allmessages:
        if msg.content == ID and msg.author == bot.user:
            msgID = msg.id
            # edits the contents of the embedded message
            edit_embed = discord.Embed(
                description=eventName,
                color=0x5CDBF0
            )
            edit_embed.add_field(name='Date: ', value=eventDate, inline=True)
            edit_embed.add_field(name='Time: ', value=eventTime, inline=True)
            edit_embed.add_field(name='Point of Contact: ', value=point_of_contact, inline=False)
            edit_embed.set_footer(text="✅ if going || ❔ if unsure || ❌ if not going")
            await msg.edit(embed=edit_embed)

    # locates the data entry with the given msgID and finds the role_id that corresponds with the msg
    query = {"_id": msgID}
    msg_data = collection.find(query)
    for data in msg_data:
        role_id = data["roleID"]
    # renames the role to correspond with the new event name
    existing_role = discord.utils.get(ctx.guild.roles, id=role_id)
    role_name = existing_role.name
    await existing_role.edit(name=eventName)
    # renames the text channel to correspond with the new event name
    role_name = role_name.replace(" ", "-")
    existing_channel = discord.utils.get(ctx.guild.channels, name=role_name + "-planning")
    await existing_channel.edit(name=eventName + "-planning")
    await existing_channel.send(existing_role.mention + '\nEvent details have been changed! Refer to the #events channel for '
                                               'updated information!')


@bot.event
async def on_raw_reaction_add(payload):
    # allows only specific reactions in the events channel, unauthorized reactions will be deleted
    message = await bot.get_channel(events_channel_id).fetch_message(payload.message_id)
    msgID = message.id
    user = payload.member
    emoji = payload.emoji

    reaction_string = payload.emoji.name
    allowed_emojis = ["✅", "❌", "❔"]
    give_role_emojis = ["✅", "❔"]

    if message.channel.id == events_channel_id:
        if user.id != bot.user.id and reaction_string not in allowed_emojis:
            await message.remove_reaction(emoji, user)

        # iterates through each reaction in message
        for reacts in message.reactions:
            # checks if user is a bot and if the user reacted to two different emojis
            if user in await reacts.users().flatten() and user.id != bot.user.id and str(reacts) != str(payload.emoji):
                await message.remove_reaction(reacts.emoji, user)

        # checks if the user reacted with the desired emoji to be assigned the role
        if reaction_string not in give_role_emojis:
            return

        # locates the data entry with the given msgID and finds the role_id that corresponds with the msg
        query = {"_id": msgID}
        msg_data = collection.find(query)
        for data in msg_data:
            role_id = data["roleID"]

        # gets the user that reacted with a check mark or question mark on the message
        member = discord.utils.get(message.guild.members, id=user.id)
        # gets the role assigned to the message
        role = discord.utils.get(message.guild.roles, id=role_id)
        # gives the user the corresponding role
        await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    message = await bot.get_channel(events_channel_id).fetch_message(payload.message_id)
    msgID = message.id
    guild = await bot.fetch_guild(payload.guild_id)
    user = await guild.fetch_member(payload.user_id)
    reaction_string = payload.emoji.name

    give_role_emojis = ["✅", "❔"]

    if reaction_string not in give_role_emojis:
        return

    # locates the data entry with the given msgID and finds the role_id that corresponds with the msg
    query = {"_id": msgID}
    msg_data = collection.find(query)
    for data in msg_data:
        role_id = data["roleID"]
    # gets the user that reacted with a check mark on the message
    member = discord.utils.get(message.guild.members, id=user.id)
    # gets the role assigned to the message
    role = discord.utils.get(message.guild.roles, id=role_id)
    # removes the role from the user
    await member.remove_roles(role)


class start(commands.Cog):

    @commands.Cog.listener('on_message')
    async def anti_spam(self, message):
        # checks if the message sent is in the events channel
        if message.channel.id == events_channel_id:
            userID = message.author.id
            # checks if the author of the message sent is the bot, if not the the message is deleted
            if userID is not bot.user.id:
                await message.delete()


bot.run(bot_token)
