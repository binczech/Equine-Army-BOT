import discord
import utils
from config.config import Config
from discord.ext import commands

def readwrite_db(user_id, value: int = 0):
    data = utils.read_db()
    if user_id in data['users'].keys():
        data['users'][user_id] += value
    else:
        data['users'][user_id] = data['start-money'] + value
    new_value = data['users'][user_id]
    utils.save_db(data)
    return new_value

class Economics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='peníze', pass_context=True)
    async def penize(self, ctx):
        user_id = str(ctx.message.author)
        value = readwrite_db(user_id)

        await ctx.send(f'Hráč {ctx.message.author.mention} má {value} peněz.')

    @commands.command(name="platba", pass_context=True)
    async def platba(self, ctx, user: discord.User = None, value: int = 0):
        user1_id = str(ctx.message.author)
        user2_id = str(user)
        data = utils.read_db()
        channel = self.bot.get_channel(int(Config.LOG_CHANNEL))
        if user == ctx.message.author:
            await ctx.send('Nemůžeš poslat peníze sám sobě.')
        elif value < 0:
            await ctx.send(f'Hráč {ctx.message.author.mention} se pokusil \
okrást hráče {user.mention}!')
            await channel.send(f'{ctx.message.author.mention} se pokusil při \
platbě zadat zápornou částku.')
        elif value > data['users'][user1_id]:
            await ctx.send(f'Hráč {ctx.message.author.mention} nemá dostatečný \
počet peněz, aktuálně má {data["users"][user1_id]} peněz.')
            await channel.send(f'{ctx.message.author.mention} se pokusil při \
platbě zadat vyšší částku, než má.')
        else:
            new_value1 = readwrite_db(user1_id, -value)
            new_value2 = readwrite_db(user2_id, value)
            await ctx.send(f'Hráči {user.mention} bylo posláno {value} peněz, \
hráč {ctx.message.author.mention} má nyní {new_value1} peněz a hráč \
{user.mention} má nyní {new_value2} peněz.')
            await channel.send(f'Úspěšně provedena platba hráčem \
{ctx.message.author.mention} hráči {user.mention}.')

    @commands.command(name='kontrola', pass_context=True)
    @commands.has_permissions(administrator=True)
    async def kontrola(self, ctx, user: discord.User = None):
        user_id = str(user)
        value = readwrite_db(user_id)

        await ctx.send(f'Hráč {user.mention} má {value} peněz.')

    @commands.command(name='připsat-start', pass_context=True)
    @commands.has_permissions(administrator=True)
    async def pripsatstart(self, ctx, value: int = 0):
        data = utils.read_db()
        data['start-money'] = value
        utils.save_db(data)
        await ctx.send(f'Hodnota startovních peněz změněna na {value}.')

    @commands.command(name="připsat", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def pripsat(self, ctx, user: discord.User = None, value: int = 0):
        user_id = str(user)
        new_value = readwrite_db(user_id, value)
        await ctx.send(f'Hráči {user.mention} bylo připsáno {value} peněz, \
nyní má {new_value} peněz.')

    @commands.command(name="odebrat", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def odebrat(self, ctx, user: discord.User = None, value: int = 0):
        user_id = str(user)
        new_value = readwrite_db(user_id, -value)
        await ctx.send(f'Hráči {user.mention} bylo odebráno {value} peněz, \
nyní má {new_value} peněz.')

    @commands.command(name="resetovat", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx, user: discord.User = None):
        user_id = str(user)
        data = utils.read_db()
        data['users'][user_id] = data['start-money']
        utils.save_db(data)
        await ctx.send(f"Hráči {user.mention} byly resetovány peníze na \
{data['start-money']}.")

    @commands.command(name="připsat-roli", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def pripsat_roli(self, ctx, role: discord.Role, value: int = 0):
        members = []
        for member in role.members:
            # await ctx.send(str(member))
            readwrite_db(str(member), value)
            members.append(member.name)
        await ctx.send(f"Uživatelům s rolí {', '.join(members)} bylo přisáno \
{value} peněz.")

def setup(bot):
    bot.add_cog(Economics(bot))
