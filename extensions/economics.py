import discord
import utils
from config.config import Config
from discord.ext import commands


class Economics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='peníze', pass_context=True)
    async def penize(self, ctx):
        user_id = str(ctx.message.author)
        data = utils.read_db()
        if user_id in data['users'].keys():
            value = data['users'][user_id]
        else:
            value = data['start-money']
            data['users'][user_id] = value
            utils.save_db(data)

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
            data['users'][user1_id] -= value
            new_value1 = data['users'][user1_id]
            data['users'][user2_id] += value
            new_value2 = data['users'][user2_id]
            utils.save_db(data)
            await ctx.send(f'Hráči {user.mention} bylo posláno {value} peněz, \
hráč {ctx.message.author.mention} má nyní {new_value1} peněz a hráč \
{user.mention} má nyní {new_value2} peněz.')
            await channel.send(f'Úspěšně provedena platba hráčem \
{ctx.message.author.mention} hráči {user.mention}.')

    @commands.command(name='kontrola', pass_context=True)
    @commands.has_permissions(administrator=True)
    async def kontrola(self, ctx, user: discord.User = None):
        user_id = str(user)
        data = utils.read_db()
        if user_id in data['users'].keys():
            value = data['users'][user_id]
        else:
            value = data['start-money']
            data['users'][user_id] = value
            utils.save_db(data)

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
        data = utils.read_db()
        if user_id in data['users'].keys():
            data['users'][user_id] += value
        else:
            data['users'][user_id] = data['start-money'] + value
        new_value = data['users'][user_id]
        utils.save_db(data)
        await ctx.send(f'Hráči {user.mention} bylo připsáno {value} peněz, \
nyní má {new_value} peněz.')

    @commands.command(name="odebrat", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def odebrat(self, ctx, user: discord.User = None, value: int = 0):
        user_id = str(user)
        data = utils.read_db()
        if user_id in data['users'].keys():
            new_value = data['users'][user_id] - value
        else:
            new_value = data['start-money'] - value
        if new_value < 0:
            new_value = 0
        data['users'][user_id] = new_value
        utils.save_db(data)
        await ctx.send(f'Hráči {user.mention} bylo odebráno {value} peněz, \
nyní má {new_value} peněz.')

    @commands.command(name="reset", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        data = utils.read_db()
        reset_value = data['start-money']
        for key in data['users'].keys():
            data['users'][key] = reset_value
        utils.save_db(data)
        await ctx.send(f'Všem hráčům byly resetovány peníze na {reset_value}.')


def setup(bot):
    bot.add_cog(Economics(bot))
