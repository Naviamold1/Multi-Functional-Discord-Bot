import os

import asyncpg
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

load_dotenv()


class MainBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("r!"),
            description="Multi Bot Made By Naviamold",
            help_command=PrettyHelp(),
            intents=discord.Intents.all(),
        )

    async def setup_hook(self) -> None:
        db_secret = "postgresql://postgres:postgres@postgres:5432/postgres"
        if os.getenv("DB_SECRET") is not None:
            db_secret = os.getenv("DB_SECRET")

        self.db = await asyncpg.create_pool(
            db_secret,
            statement_cache_size=0,
        )

        if self.db:
            print("Connected to DB")
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS Guild(id BIGINT PRIMARY KEY UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY, guild BIGINT UNIQUE NOT NULL)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS Channel(id BIGINT PRIMARY KEY UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY, channel BIGINT UNIQUE NOT NULL, guild_id BIGINT NOT NULL, FOREIGN KEY (guild_id) REFERENCES Guild(guild), CONSTRAINT guild_unique_channel_guild UNIQUE (guild_id, channel))"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS Reaction(id BIGINT PRIMARY KEY UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY, reaction TEXT, bots BOOLEAN NOT NULL , channel_id BIGINT NOT NULL, FOREIGN KEY (channel_id) REFERENCES Channel(channel), CONSTRAINT reactions_unique_channel_reaction UNIQUE (channel_id, reaction))"
        )

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


MainBot().run(os.getenv("BOT_TOKEN"))
