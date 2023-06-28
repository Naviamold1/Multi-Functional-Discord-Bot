import discord
from discord import Interaction, app_commands
from discord.ext import commands


class Reaction(commands.GroupCog, name="reaction"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add")
    async def add(
        self, interaction: Interaction, channel: discord.TextChannel, reaction: str
    ):
        try:
            print(channel, reaction)
            await self.bot.db.execute(
                f"INSERT INTO Channel(channel) VALUES({channel.id})"
            )
        except:
            pass
        await self.bot.db.execute(
            f"INSERT INTO Reaction(channel_id, reaction) VALUES({channel.id}, E'{reaction}')"
        )
        await interaction.response.send_message(
            f"Reactions have started for {channel.mention} with emoji {reaction}"
        )

    @app_commands.command(name="remove")
    async def remove(self, interaction: Interaction):
        await interaction.response.send_message("template command")


async def setup(bot: commands.Bot):
    await bot.add_cog(Reaction(bot))
