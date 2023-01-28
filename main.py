import os

import discord
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

load_dotenv()


class MainBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="r!", description="Multi Bot Made By Naviamold",
                         help_command=PrettyHelp(), intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        cogs = ["cogs.info", "cogs.cooking", "cogs.util", "cogs.trivia"]
        for ext in cogs:
            await self.load_extension(ext)

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name='Naviamold!', type=discord.ActivityType.watching))
        print(f'We have logged in as {self.user}')
        sync = await self.tree.sync()
        print(f"Synced {len(sync)} commands(s):")
        for command in sync:
            print(command.name)
        print(f'\nBot is in {len(self.guilds)} server(s):')
        for server in self.guilds:
            print(server.name)

    async def on_command_error(self, interaction: Interaction, error: AppCommandError):
        try:
            await interaction.response.send_message(error, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send(error, ephemeral=True)


MainBot().run(os.getenv("BOT_TOKEN"))
