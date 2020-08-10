import discord
import utils
from config.config import Config
from discord.ext import commands


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def toggle_role(self, payload, emoji):
        guild = discord.utils.get(self.bot.guilds, name=Config.GUILD)
        role = discord.utils.get(guild.roles, name=emoji["value"])
        if role is not None:
            member = guild.get_member(payload.user_id)
            if payload.event_type == "REACTION_ADD":
                await member.add_roles(role)
            elif payload.event_type == "REACTION_REMOVE":
                await member.remove_roles(role)

    async def check_reaction(self, payload):
        if int(Config.ROLES_CHANNEL) == payload.channel_id:
            channel = self.bot.get_channel(int(Config.ROLES_CHANNEL))
            messages = channel.history()
            emote_values = await utils.parse_admin_msgs(messages, False)
            if str(payload.emoji) in emote_values.keys():
                await self.toggle_role(payload,
                                       emote_values[str(payload.emoji)])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # channel = self.bot.get_channel(int(Config.ROLES_CHANNEL))
        await self.check_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.check_reaction(payload)


def setup(bot):
    bot.add_cog(Roles(bot))
