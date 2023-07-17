from typing import Literal, Optional

import discord
from discord import Interaction, app_commands
from discord.app_commands import Choice
from discord.ext import commands


class Info(commands.Cog, description="Info commands about the bot"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Get the bots latency")
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message(
            f"🏓 Pong: {round (self.bot.latency * 1000)} ms"
        )

    @commands.command(
        name="sync",
        description="Sync the slash commands to the current guild(s). Owner only command.",
    )
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.is_owner()
    @commands.guild_only()
    @app_commands.command(name="reload")
    @app_commands.choices(
        extension=[
            Choice(name="trivia", value="cogs.trivia"),
            Choice(name="custom", value="cogs.custom"),
            Choice(name="util", value="cogs.util"),
            Choice(name="chess", value="cogs.chess"),
            Choice(name="cooking", value="cogs.cooking"),
            Choice(name="info", value="cogs.info"),
            Choice(name="reaction", value="cogs.reaction"),
        ]
    )
    async def reload(self, interaction: Interaction, extension: Choice[str]):
        await self.bot.reload_extension(extension.value)
        await interaction.response.send_message(
            f"Reloaded **{extension.value}**", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
