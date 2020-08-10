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
        return await utils.parse_admin_msgs(messages, True)

    def is_admin(self, user_id, channel_id, guild_id):
        guild = self.bot.get_guild(guild_id)
        user = guild.get_member(user_id)
        channel = self.bot.get_channel(channel_id)
        permissions = user.permissions_in(channel)
        return permissions.administrator

    async def check_reaction(self, payload):
        if (payload.channel_id != int(Config.ROLES_CHANNEL)
            and self.is_admin(payload.user_id, payload.channel_id,
                              payload.guild_id)):
            emote_values = await self.get_list_of_prizes()
            if str(payload.emoji) in emote_values.keys():
                if payload.event_type == "REACTION_ADD":
                    await self.grant_prize(payload,
                                           emote_values[str(payload.emoji)])
                elif payload.event_type == "REACTION_REMOVE":
                    emote = emote_values[str(payload.emoji)]
                    emote["value"] *= -1
                    await self.grant_prize(payload, emote)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.check_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.check_reaction(payload)


def setup(bot):
    bot.add_cog(Rewards(bot))
