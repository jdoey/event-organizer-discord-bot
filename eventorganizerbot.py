import discord
import asyncio
import string
import random
import datetime
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)
bot_token = ''

# channel to send the embedded messages
events_channel_id = None

messageID = None
watched_messages = {
    messageID: {
        "✅": {},
        "❔": {}
    }
}


@bot.event
async def on_ready():
    print('Bot is online.')


@bot.command(name="setembedchannel", description="sets the channel where the embedded messages will be sent\n ;setembedchannel channel_id")
async def setembedchannel(ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        await ctx.send('Enter channel id of channel that you want the embedded messages to be sent', delete_after=15)
        global events_channel_id
        events_channel_id = await bot.wait_for("message", check=check, timeout=15)
        events_channel_id = events_channel_id.content
        events_channel_id = int(events_channel_id)
        print(events_channel_id)
        await ctx.send("Success", delete_after=3)
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply within 15 seconds!", delete_after=4)
    bot.add_cog(start(bot))


@bot.command(name="addevent", description="creates an event message and sends it to the events channel")
async def addevent(ctx):
    # checks if the user has set the event channel
    try:
        print(events_channel_id)
    except NameError:
        await ctx.send("event channel is not set, use command ;setembedchannel to set the channel you want the embedded messages to be sent")
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
    embed.add_field(name='Date: ', value=eventDate)
    embed.add_field(name='Time: ', value=eventTime)
    embed.set_footer(text="✅ if going || ❓ if unsure || ❌ if not going")

    # sends the embedded message in specified text channel
    channel = bot.get_channel(events_channel_id)
    msg = await channel.send(''.join(random.choices(string.ascii_uppercase + string.digits, k=5)), embed=embed)

    guild = ctx.message.guild

    # creates the role and permissions
    permissions = discord.Permissions(permissions=0x40)
    role = await guild.create_role(name=eventName, permissions=permissions, mentionable=True)
    global roleID
    roleID = role.id

    # adds reactions to the embedded message
    await msg.add_reaction(emoji="✅")
    await msg.add_reaction(emoji="❔")
    await msg.add_reaction(emoji="❌")

    # creates the planning text channel and permissions
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        role: discord.PermissionOverwrite(read_messages=True)
    }
    txtchannel = await guild.create_text_channel(eventName + " planning", overwrites=overwrites)


@bot.command(name="deleteevent", description="deletes the specified event \n command is called by passing the name of the event and the unique 5-character code located in the specified embedded message \n\n ex: ;deleteevent \"event_name\" 5_char_code")
async def deleteevent(ctx, eventToDelete: str, ID: str):
    channel = bot.get_channel(events_channel_id)
    allmessages = await channel.history(limit=200).flatten()
    # locates the message to delete
    for msg in allmessages:
        if msg.content == ID and msg.author == bot.user:
            await msg.delete()

    # deletes the text channel of the event
    eventToDelete_channel = eventToDelete.replace(" ", "-")
    existing_channel = discord.utils.get(ctx.guild.channels, name=eventToDelete_channel + "-planning")
    if existing_channel is not None:
        await existing_channel.delete()
    # deletes the role of the event
    existing_role = discord.utils.get(ctx.guild.roles, name=eventToDelete)
    if existing_role is not None:
        await existing_role.delete()


@bot.command(name="changeevent", description="changes the details of the specified event \n command is called by passing the event name, event date, event time, and the unique 5-character code located in the specified embedded message \n\n ex: ;changeevent \"event_name\" event_date event_time 5_char_code")
async def changeevent(ctx, eventName: str, eventDate: str, eventTime: str, ID: str):
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
            edit_embed.add_field(name='Date: ', value=eventDate)
            edit_embed.add_field(name='Time: ', value=eventTime)
            edit_embed.set_footer(text="✅ if going || ❔ if unsure || ❌ if not going")
            await msg.edit(embed=edit_embed)

    # renames the role to correspond with the new event name
    existing_role = discord.utils.get(ctx.guild.roles, id=watched_messages[msgID]["✅"])
    role_name = existing_role.name
    await existing_role.edit(name=eventName)
    # renames the text channel to correspond with the new event name
    role_name = role_name.replace(" ", "-")
    existing_channel = discord.utils.get(ctx.guild.channels, name=role_name + "-planning")
    await existing_channel.edit(name=eventName)


@bot.event
async def on_reaction_add(reaction, user):
    # allows only specific reactions, unauthorized reactions will be deleted
    allowed_emojis = ["✅", "❌", "❔"]
    if reaction.message.channel.id == events_channel_id:
        if user.id != bot.user.id and reaction.emoji not in allowed_emojis:
            await reaction.remove(user)
        msg = reaction.message
        # iterates through each reaction in message
        for reacts in msg.reactions:
            # checks if user is a bot and if the user reacted to two different emojis
            if user in await reacts.users().flatten() and user.id != bot.user.id and str(reacts) != str(reaction.emoji):
                await msg.remove_reaction(reacts.emoji, user)

        msgID = reaction.message.id
        # checks if the message has already been added to the dictionary
        if not msgID in watched_messages:
            watched_messages[msgID] = {"✅": roleID,
                                       "❔": roleID}
        # checks if the user reacted with the desired emoji to be assigned the role
        if not reaction.emoji in watched_messages[msgID]:
            return
        # gets the user that reacted with a check mark or question mark on the message
        member = discord.utils.get(reaction.message.guild.members, id=user.id)
        # gets the role assigned to the message
        role = discord.utils.get(reaction.message.guild.roles, id=watched_messages[msgID]["✅"])
        # gives the user the corresponding role
        await member.add_roles(role)


@bot.event
async def on_reaction_remove(reaction, user):
    msgID = reaction.message.id
    if not msgID in watched_messages:
        watched_messages[msgID] = {"✅": roleID}

    if not reaction.emoji in watched_messages[msgID]:
        return

    # gets the user that reacted with a check mark on the message
    member = discord.utils.get(reaction.message.guild.members, id=user.id)
    # gets the role assigned to the message
    role = discord.utils.get(reaction.message.guild.roles, id=watched_messages[msgID]["✅"])
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
