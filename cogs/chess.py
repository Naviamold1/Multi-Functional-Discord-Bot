from datetime import datetime

import chessdotcom
import discord
import lichess.api
from chessdotcom import Client, get_player_profile, get_random_daily_puzzle
from discord import Interaction, app_commands
from discord.app_commands import Choice
from discord.ext import commands


class Chess(commands.GroupCog, name="chess", description="Command related to chess"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="search", description="Get players stats")
    @app_commands.describe(platform="Platform to search", username="Username to search")
    @app_commands.choices(
        platform=[
            Choice(name="chess.com", value="chess.com"),
            Choice(name="lichess.org", value="lichess.org"),
        ]
    )
    async def chsearch(
        self, interaction: Interaction, platform: Choice[str], username: str
    ) -> None:
        Client.request_config["headers"]["User-Agent"] = "discord.py Application. "
        Client.rate_limit_handler.tries = 2
        Client.rate_limit_handler.tts = 4

        try:
            res = get_player_profile(username)
            res = res.json["player"]

            embed = discord.Embed(
                title=res.get("username"), url=res.get("url"), color=0x00AE86
            )
            embed.set_thumbnail(url=res.get("avatar"))
            fields = [
                ("name", res.get("name"), True),
                ("Title", res.get("title"), True),
                ("Followers", res.get("followers"), True),
                ("Country", res.get("country").split("/")[-1], True),
                ("Last Online", f"<t:{res.get('last_online')}>", True),
                ("Joined", f"<t:{res.get('joined')}>", True),
                ("Status", res.get("status"), True),
                ("Is Streamer", res.get("is_streamer"), True),
                ("Verified", res.get("verified"), True),
                ("League", res.get("league"), True),
            ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        except Exception as e:
            await interaction.response.send_message(e.text)
        embed.set_footer(text=f"ID - {res['player_id']}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="puzzle", description="Get a random daily puzzle")
    async def chpuzzle(self, interaction: Interaction) -> None:
        r = get_random_daily_puzzle()
        embed = discord.Embed(
            title=r.puzzle.title,
            url=r.puzzle.url,
            timestamp=datetime.fromtimestamp(r.puzzle.publish_time),
        )
        embed.set_image(url=r.puzzle.image)
        embed.add_field(name="FEN", value=r.puzzle.fen, inline=False)
        embed.add_field(name="PGN", value=r.puzzle.pgn, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chess(bot))
