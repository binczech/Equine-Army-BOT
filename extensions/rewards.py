import re
import utils
from config.config import Config
from discord.ext import commands


class Rewards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def grant_prize(self, payload, emote):
        channel = self.bot.get_channel(payload.channel_id)
        log_channel = self.bot.get_channel(int(Config.LOG_CHANNEL))
        try:
            message = await channel.fetch_message(payload.message_id)
        except NotFound:
            return
        user = message.author
        reaction_author = self.bot.get_user(payload.user_id)
        utils.change_users_money(str(user), emote["value"])
        if emote["value"] > 0:
            text = f'Uživatel {user.mention} získal odměnu {emote["value"]} \
od {reaction_author.mention} za: {emote["description"]}.'
            await channel.send(text)
            await log_channel.send(f'{text} ({message.jump_url})')
        else:
            await channel.send(f'Odměna pro uživatele {user.mention} zrušena.')
            await log_channel.send(f'Uživatel {reaction_author.mention} zrušil \
odměnu pro {user.mention} za: {emote["description"]}.')

    async def get_list_of_prizes(self):
        channel = self.bot.get_channel(int(Config.REWARDS_CHANNEL))
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

    def is_admin(self, user_id, channel_id, guild_id):
        guild = self.bot.get_guild(guild_id)
        user = guild.get_member(user_id)
        channel = self.bot.get_channel(channel_id)
        permissions = user.permissions_in(channel)
        return permissions.administrator

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.is_admin(payload.user_id, payload.channel_id,
                         payload.guild_id):
            emote_values = await self.get_list_of_prizes()
            if str(payload.emoji) in emote_values.keys():
                await self.grant_prize(payload,
                                       emote_values[str(payload.emoji)])

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if self.is_admin(payload.user_id, payload.channel_id,
                         payload.guild_id):
            emote_values = await self.get_list_of_prizes()
            if str(payload.emoji) in emote_values.keys():
                emote = emote_values[str(payload.emoji)]
                emote["value"] *= -1
                await self.grant_prize(payload, emote)


def setup(bot):
    bot.add_cog(Rewards(bot))
