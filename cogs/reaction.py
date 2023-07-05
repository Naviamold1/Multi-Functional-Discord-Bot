import asyncpg
import discord
from asyncpg import exceptions as pgexec
from discord import Interaction, app_commands
from discord.ext import commands


class Reaction(commands.GroupCog, name="reaction"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.db: asyncpg.pool.Pool = self.bot.db

    @app_commands.command(name="add")
    async def add(
        self,
        interaction: Interaction,
        channel: discord.TextChannel,
        reaction: str,
        bots: bool = False,
    ):
        guild_id = interaction.guild_id
        channel_id = channel.id
        await self.bot.db.execute(
            "INSERT INTO Guild(guild) VALUES($1) ON CONFLICT DO NOTHING",
            guild_id,
        )

        await self.bot.db.execute(
            "INSERT INTO Channel(guild_id, channel) VALUES($1, $2) ON CONFLICT DO NOTHING",
            guild_id,
            channel_id,
        )

        try:
            await self.bot.db.execute(
                f"INSERT INTO Reaction(channel_id, reaction, bots) VALUES($1, E'{reaction}', $2)",
                channel_id,
                bots,
            )
            await interaction.response.send_message(
                f"Reactions have started for {channel.mention} with emoji {reaction} with bots {bots}"
            )
        except pgexec.UniqueViolationError:
            await interaction.response.send_message(
                f"The channel {channel.mention} already has started reactions with emoji {reaction}",
                ephemeral=True,
            )

    # @TODO NONE OF THE REMOVE IS FUNCTIONAL RN
    @app_commands.command(name="remove")
    async def remove(self, interaction: Interaction, channel: str, reaction: str):
        await interaction.response.send_message("template command")

    @remove.autocomplete("channel")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        # Do stuff with the "current" parameter, e.g. querying it search results...
        res = await self.bot.db.fetch(
            f"SELECT channel_id,reaction FROM Server INNER JOIN reaction on channel = channel_id WHERE server = 629021525978120212"
        )
        # Then return a list of app_commands.Choice
        data = []
        for channel, reaction in res:
            print(channel)
            data.append(app_commands.Choice(name=channel, value=channel))
        return data
        # name = self.bot.get_channel(interaction.channel_id)
        return [
            app_commands.Choice(name=channel, value=channel)
            for channel, reaction in res
        ]

    # @TODO ADD CACHE
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        res = await self.bot.db.fetch(
            "SELECT reaction, bots FROM Reaction WHERE channel_id = $1",
            message.channel.id,
        )
        if res:
            for reaction, bots in res:
                await message.add_reaction(reaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reaction(bot))
