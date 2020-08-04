import os
import json
import pymongo
import discord
import traceback
import re
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME')
LOG_CHANNEL = os.getenv('LOG_CHANNEL')
WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL')
ROLES_CHANNEL = os.getenv('ROLES_CHANNEL') # TODO
REWARDS_CHANNEL = os.getenv('REWARDS_CHANNEL')
bot = commands.Bot(command_prefix='!')


def open_json():
    with open('money.json') as json_file:
        data = json.load(json_file)
    return data


def save_json(data):
    with open('money.json', 'w') as outfile:
        json.dump(data, outfile)


def open_db():
    client = pymongo.MongoClient(MONGODB_URI)
    db = client.get_default_database()
    money = db[DB_NAME]
    return client, money


def read_db():
    client, money = open_db()
    data = money.find_one()
    client.close()
    return data


def save_db(data):
    client, money = open_db()
    money.replace_one({'_id': data['_id']}, data, upsert=True)
    client.close()


# user_id should be string
def change_users_money(user_id, value):
    data = read_db()
    if user_id in data['users'].keys():
        data['users'][user_id] += value
    else:
        start_value = data['start-money']
        data['users'][user_id] = start_value + value
    new_value = data['users'][user_id]
    save_db(data)
    return new_value


# user_id should be string
def get_user_money(user_id):
    data = read_db()
    if user_id in data['users'].keys():
        value = data['users'][user_id]
    else:
        start_value = data['start-money']
        data['users'][user_id] = start_value
        save_db(data)
    return value


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    channel = bot.get_channel(int(LOG_CHANNEL))
    await channel.send(f'Bot připojen na server!')


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(WELCOME_CHANNEL))
    await channel.send(f'Ahoj {member.mention}, vítej na Equine Army serveru!')


@bot.command(name="příkazy", pass_context=True)
async def prikazy(ctx):
    embed = discord.Embed(
        title='Uživatelské příkazy',
        description='',
        color=0x1AFB32
    )
    embed.set_footer(
        icon_url=ctx.author.avatar_url,
        text=str(ctx.author)
    )
    embed.add_field(
        name='!příkazy',
        value='vypíše seznam příkazů',
        inline=True
    )
    embed.add_field(
        name='!peníze',
        value='vypíše aktuální stav konta hráče',
        inline=False
    )
    embed.add_field(
        name='!platba @hráč hodnota',
        value='pošle hráči peníze z vlastního konta',
        inline=False
    )
    await ctx.send(embed=embed)
    embed_admin = discord.Embed(
        title='Admin příkazy',
        description='',
        color=0x1AFB32
    )
    embed_admin.set_footer(icon_url=ctx.author.avatar_url, text=str(ctx.author))
    embed_admin.add_field(
        name='!kontrola @hráč', value='vypíše peníze \konkrétního hráče',
        inline=False
    )
    embed_admin.add_field(
        name='!připsat-start hodnota',
        value='změní hodnotu startovních peněz',
        inline=False
    )
    embed_admin.add_field(
        name='!připsat @hráč hodnota',
        value='připíše hráčovi peníze',
        inline=False
    )
    embed_admin.add_field(
        name='!odebrat @hráč hodnota',
        value='odepíše hráčovi peníze',
        inline=False
    )
    await ctx.send(embed=embed_admin)


@bot.command(name='peníze', pass_context=True)
async def penize(ctx):
    user_id = str(ctx.message.author)
    data = read_db()
    if user_id in data['users'].keys():
        value = data['users'][user_id]
    else:
        value = data['start-money']
        data['users'][user_id] = value
        save_db(data)

    await ctx.send(f'Hráč {ctx.message.author.mention} má {value} peněz.')


@bot.command(name="platba", pass_context=True)
async def platba(ctx, user: discord.User = None, value: int = 0):
    user1_id = str(ctx.message.author)
    user2_id = str(user)
    data = read_db()
    channel = bot.get_channel(int(LOG_CHANNEL))
    if value < 0:
        await ctx.send(f'Hráč {ctx.message.author.mention} se pokusil okrást \
hráče {user.mention}!')
        await channel.send(f'{ctx.message.author.mention} se pokusil při platbě\
 zadat zápornou částku.')
    elif value > data['users'][user1_id]:
        await ctx.send(f'Hráč {ctx.message.author.mention} nemá dostatečný \
počet peněz, aktuálně má {data["users"][user1_id]} peněz.')
        await channel.send(f'{ctx.message.author.mention} se pokusil při platbě\
 zadat vyšší částku, než má.')
    else:
        data['users'][user1_id] -= value
        new_value1 = data['users'][user1_id]
        data['users'][user2_id] += value
        new_value2 = data['users'][user2_id]
        save_db(data)
        await ctx.send(f'Hráči {user.mention} bylo posláno {value} peněz, \
hráč {ctx.message.author.mention} má nyní {new_value1} peněz a hráč \
{user.mention} má nyní {new_value2} peněz.')
        await channel.send(f'Úspěšně provedena platba hráčem \
{ctx.message.author.mention} hráči {user.mention}.')


@bot.command(name='kontrola', pass_context=True)
@commands.has_permissions(administrator=True)
async def kontrola(ctx, user: discord.User = None):
    user_id = str(user)
    data = read_db()
    if user_id in data['users'].keys():
        value = data['users'][user_id]
    else:
        value = data['start-money']
        data['users'][user_id] = value
        save_db(data)

    await ctx.send(f'Hráč {user.mention} má {value} peněz.')


@bot.command(name='připsat-start', pass_context=True)
@commands.has_permissions(administrator=True)
async def pripsatstart(ctx, value: int = 0):
    data = read_db()
    data['start-money'] = value
    save_db(data)
    await ctx.send(f'Hodnota startovních peněz změněna na {value}.')


@bot.command(name="připsat", pass_context=True)
@commands.has_permissions(administrator=True)
async def pripsat(ctx, user: discord.User = None, value: int = 0):
    user_id = str(user)
    data = read_db()
    if user_id in data['users'].keys():
        data['users'][user_id] += value
    else:
        data['users'][user_id] = data['start-money'] + value
    new_value = data['users'][user_id]
    save_db(data)
    await ctx.send(f'Hráči {user.mention} bylo připsáno {value} peněz, \
nyní má {new_value} peněz.')


@bot.command(name="odebrat", pass_context=True)
@commands.has_permissions(administrator=True)
async def odebrat(ctx, user: discord.User = None, value: int = 0):
    user_id = str(user)
    data = read_db()
    if user_id in data['users'].keys():
        new_value = data['users'][user_id] - value
    else:
        new_value = data['start-money'] - value
    if new_value < 0:
        new_value = 0
    data['users'][user_id] = new_value
    save_db(data)
    await ctx.send(f'Hráči {user.mention} bylo odebráno {value} peněz, \
nyní má {new_value} peněz.')


@bot.command(name="reset", pass_context=True)
@commands.has_permissions(administrator=True)
async def reset(ctx):
    data = read_db()
    reset_value = data['start-money']
    for key in data['users'].keys():
        data['users'][key] = reset_value
    save_db(data)
    await ctx.send(f'Všem hráčům byly resetovány peníze na {reset_value}.')


async def grant_prize(payload, emote):
    channel = bot.get_channel(payload.channel_id)
    log_channel = bot.get_channel(int(LOG_CHANNEL))
    try:
        message = await channel.fetch_message(payload.message_id)
    except NotFound:
        return
    user = message.author
    reaction_author = bot.get_user(payload.user_id)
    new_value = change_users_money(str(user), emote["value"])
    if emote["value"] > 0:
        text = f'Uživatel {user.mention} získal odměnu {emote["value"]}\
 od {reaction_author.mention} za: {emote["description"]}.'
        await channel.send(text)
        await log_channel.send(f'{text} ({message.jump_url})')
    else:
        await channel.send(f'Odměna pro uživatele {user.mention} zrušena.')
        await log_channel.send(f'Uživatel {reaction_author.mention} zrušil \
odměnu pro {user.mention} za: {emote["description"]}.')



async def get_list_of_prizes():
    channel = bot.get_channel(int(REWARDS_CHANNEL))
    messages = channel.history()
    emote_values = {}
    line_regex = re.compile(r"^.*(\s\s)(\d*)(\s\s)(.*)$")
    async for message in messages:
        for line in message.content.splitlines():
            if re.search(line_regex, line):
                emote, value, description = line.split("  ", 2)
                emote_values[emote] = {
                                        "value": int(value),
                                        "description": description
                                        }
    return emote_values


def is_admin(user_id, channel_id, guild_id):
    guild = bot.get_guild(guild_id)
    user = guild.get_member(user_id)
    channel = bot.get_channel(channel_id)
    permissions = user.permissions_in(channel)
    return permissions.administrator


@bot.event
async def on_raw_reaction_add(payload):
    if is_admin(payload.user_id, payload.channel_id, payload.guild_id):
        emote_values = await get_list_of_prizes()
        if payload.emoji.name in emote_values.keys():
            await grant_prize(payload, emote_values[payload.emoji.name])


@bot.event
async def on_raw_reaction_remove(payload):
    if is_admin(payload.user_id, payload.channel_id, payload.guild_id):
        emote_values = await get_list_of_prizes()
        if payload.emoji.name in emote_values.keys():
            emote = emote_values[payload.emoji.name]
            emote["value"] *= -1
            await grant_prize(payload, emote)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.BadArgument):
        await ctx.send('Prosím, tagni existujícího hráče.')
    else:
        print(error)


@bot.event
async def on_error(event, *args, **kwargs):
    channel = bot.get_channel(int(LOG_CHANNEL))
    output = traceback.format_exc()
    print(output)
    output = utils.cut_string(output, 1900)
    for message in output:
        await channel.send("```\n{}```".format(message))


@bot.event
async def on_disconnect():
    channel = bot.get_channel(int(LOG_CHANNEL))
    await channel.send("Bot byl odpojen ze serveru.")


bot.run(TOKEN)
