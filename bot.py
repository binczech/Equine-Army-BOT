import discord
import traceback
import utils
from config.config import Config
from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=Config.GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    channel = bot.get_channel(int(Config.LOG_CHANNEL))
    await channel.send('Bot připojen na server!')


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(Config.WELCOME_CHANNEL))
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
    embed_admin.set_footer(icon_url=ctx.author.avatar_url,
                           text=str(ctx.author))
    embed_admin.add_field(
        name='!kontrola @hráč', value='vypíše peníze konkrétního hráče',
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


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.BadArgument):
        await ctx.send('Prosím, tagni existujícího hráče.')
    else:
        print(error)


@bot.event
async def on_error(event, *args, **kwargs):
    channel = bot.get_channel(int(Config.LOG_CHANNEL))
    output = traceback.format_exc()
    print(output)
    output = utils.cut_string(output, 1900)
    for message in output:
        await channel.send("```\n{}```".format(message))


@bot.event
async def on_disconnect():
    channel = bot.get_channel(int(Config.LOG_CHANNEL))
    await channel.send("Bot byl odpojen ze serveru.")


print('Loaded extensions: ', end='')
for extension in Config.extensions:
    bot.load_extension(f'extensions.{extension}')
    print(f'{extension} ', end='')
print('')

bot.run(Config.TOKEN)
