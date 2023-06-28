import asyncio
import os

import asyncpg
import discord
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

load_dotenv()


async def run():
    db = await asyncpg.create_pool(os.getenv("DB_SECRET"))
    if db:
        print("Connected to DB")
    await db.execute(
        "CREATE TABLE IF NOT EXISTS Channel(id BIGINT PRIMARY KEY UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY, channel BIGINT UNIQUE NOT NULL)"
    )
    await db.execute(
        "CREATE TABLE IF NOT EXISTS Reaction(id BIGINT PRIMARY KEY UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY, reaction TEXT, channel_id BIGINT NOT NULL, FOREIGN KEY (channel_id) REFERENCES Channel(channel), CONSTRAINT reactions_unique_channel_reaction UNIQUE (channel_id, reaction))"
    )
    bot = MainBot(db=db)
    try:
        await bot.start(os.getenv("BOT_TOKEN"))
    except KeyboardInterrupt:
        await db.close()
        await bot.logout()


class MainBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or("r!"),
            description="Multi Bot Made By Naviamold",
            help_command=PrettyHelp(),
            intents=discord.Intents.all(),
        )
        self.db = kwargs.pop("db")

    async def setup_hook(self) -> None:
        cogs = [
            "cogs.info",
            "cogs.cooking",
            "cogs.util",
            "cogs.trivia",
            "cogs.chess",
            "cogs.reaction",
        ]
        for ext in cogs:
            await self.load_extension(ext)
        if os.path.exists(r"cogs\custom.py"):
            await self.load_extension("cogs.custom")

        sync = await self.tree.sync()
        print(f"Synced {len(sync)} command(s):")
        for command in sync:
            print(command.name)

    async def on_ready(self):
        print(f"We have logged in as {self.user}")
        await self.change_presence(
            activity=discord.Activity(
                name="Naviamold!", type=discord.ActivityType.watching
            )
        )
        print(f"\nBot is in {len(self.guilds)} server(s):")
        for server in self.guilds:
            print(server.name)

    async def on_command_error(self, interaction: Interaction, error: AppCommandError):
        try:
            await interaction.response.send_message(error, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send(error, ephemeral=True)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
