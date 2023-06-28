from discord import Interaction, app_commands
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Get the bots latency")
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message(
            f"🏓 Pong: {round (self.bot.latency * 1000)} ms"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
