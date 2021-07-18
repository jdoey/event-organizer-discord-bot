import discord
import asyncio
import string
import random
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)
bot_token = 'ODY1OTQ0ODc1NTMxMTA4Mzc2.YPLYAg.Hp0vF0FDeghxL4wRJeRJz6lNgDs'

# channel to send the embedded messages
events_channel_id = 865164812438732800

messageID = None
watched_messages = {
    messageID: {
        "✅": {}
    }
}


@bot.event
async def on_ready():
    print('Bot is online.')
    channel = bot.get_channel(events_channel_id)


@bot.command()
async def addevent(ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    # prompts the user who called the command
    try:
        await ctx.send('Enter name of event:')
        eventName = await bot.wait_for("message", check=check, timeout=15)
        eventName = eventName.content
        await ctx.send('Enter date of event in format MM/DD/YYYY:')
        eventDate = await bot.wait_for("message", check=check, timeout=15)
        eventDate = eventDate.content
        await ctx.send("Enter time of event in format XX:XX AM/PM")
        eventTime = await bot.wait_for("message", check=check, timeout=15)
        eventTime = eventTime.content
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply within 15 seconds!")

    # creates the embed
    embed = discord.Embed(
        description=eventName,
        color=0x5CDBF0
    )
    embed.add_field(name='Date: ', value=eventDate)
    embed.add_field(name='Time: ', value=eventTime)
    embed.set_footer(text="✅ if going || ❌ if not going")

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
    await msg.add_reaction(emoji="❌")

    # creates the planning text channel and permissions
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        role: discord.PermissionOverwrite(read_messages=True)
    }
    txtchannel = await guild.create_text_channel(eventName + " planning", overwrites=overwrites)


@bot.command()
async def deleteevent(ctx, ID: str, eventToDelete: str):
    channel = bot.get_channel(events_channel_id)
    allmessages = await channel.history(limit=200).flatten()
    # locates the message to delete
    for msg in allmessages:
        if msg.content == ID and msg.author == bot.user:
            await msg.delete()

    # deletes the text channel of the event
    existing_channel = discord.utils.get(ctx.guild.channels, name=eventToDelete + " planning")
    if existing_channel is not None:
        await existing_channel.delete()
    # deletes the role of the event
    existing_role = discord.utils.get(ctx.guild.roles, name=eventToDelete)
    if existing_role is not None:
        await existing_role.delete()


@bot.command()
async def changeevent(ctx, eventName: str, eventDate: str, eventTime: str, ID: str):
    channel = bot.get_channel(events_channel_id)
    allmessages = await channel.history(limit=200).flatten()

    for msg in allmessages:
        if msg.content == ID and msg.author == bot.user:
            edit_embed = discord.Embed(
                description=eventName,
                color=0x5CDBF0
            )
            edit_embed.add_field(name='Date: ', value=eventDate)
            edit_embed.add_field(name='Time: ', value=eventTime)
            edit_embed.set_footer(text="✅ if going || ❌ if not going")
            await msg.edit(embed=edit_embed)


@bot.event
async def on_reaction_add(reaction, user):
    # allows only specific reactions, unauthorized reactions will be deleted
    allowed_emojis = ["✅", "❌"]
    if user.id != bot.user.id and reaction.emoji not in allowed_emojis:
        await reaction.remove(user)
    msgID = reaction.message.id
    # checks if the message has already been added to the dictionary
    if not msgID in watched_messages:
        watched_messages[msgID] = {"✅": roleID}
    # checks if the user reacted with the desired emoji to be assigned the role
    if not reaction.emoji in watched_messages[msgID]:
        return

    # gets the user that reacted with a check mark on the message
    member = discord.utils.get(reaction.message.guild.members, id=user.id)
    # gets the role assigned to the message
    role = discord.utils.get(reaction.message.guild.roles, id=watched_messages[msgID]["✅"])
    # removes the role from the user
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

@bot.listen('on_message')
async def anti_spam(message):
    # checks if the message sent is in the events channel
    if message.channel.id == events_channel_id:
        userID = message.author.id
        # checks if the author of the message sent is the bot, if not the the message is deleted
        if userID is not bot.user.id:
            await message.delete()

bot.run(bot_token)
