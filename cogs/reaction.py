import discord
from asyncpg import exceptions as pgexec
from discord import Interaction, app_commands
from discord.ext import commands

reaction_cache = {}


async def get_channel_reactions(db, channel_id):
    if channel_id in reaction_cache:
        print("Cache Hit")
        return reaction_cache[channel_id]
    else:
        res = await db.fetch(
            "SELECT reaction, bots FROM Reaction WHERE channel_id = $1",
            channel_id,
        )
        if res:
            reaction = list(dict(res))
            bots = list(dict(res).values())
            reaction_cache[channel_id] = {"reaction": reaction, "bots": bots}
            print("Cache Miss")
            return reaction_cache[channel_id]


def update_cache(channel_id):
    print("Updating Cache")
    reaction_cache.pop(channel_id)
    print("Cache Updated")


class Reaction(commands.GroupCog, name="reaction"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
            update_cache(channel.id)
            await interaction.response.send_message(
                f"Reactions have started for {channel.mention} with emoji {reaction} with bots {bots}"
            )
        except pgexec.UniqueViolationError:
            await interaction.response.send_message(
                f"The channel {channel.mention} already has started reactions with emoji {reaction}",
                ephemeral=True,
            )

    @app_commands.command(name="remove")
    async def remove(
        self, interaction: Interaction, channel: discord.TextChannel, reaction: str
    ):
        res = await self.bot.db.execute(
            "DELETE FROM Reaction WHERE channel_id = $1 AND reaction = $2",
            channel.id,
            reaction,
        )
        if res:
            update_cache(channel.id)

            await interaction.response.send_message(
                f"Reactions have been removed for {channel.mention} with emoji {reaction}"
            )
        else:
            await interaction.response.send_message(
                f"The channel {channel.mention} does not have reactions with emoji {reaction}",
                ephemeral=True,
            )

    @app_commands.command(name="list")
    async def list(self, interaction: Interaction, channel: discord.TextChannel):
        res = await get_channel_reactions(self.bot.db, channel.id)
        if res:
            embed = discord.Embed(
                title="List of Reactions",
                description=f"List of Reactions for Channel {channel.mention}",
                color=0xFF0000,
            )
            for reaction, bots in zip(res["reaction"], res["bots"]):
                embed.add_field(name=reaction, value=f"Bots: {bots}", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"The channel {channel.mention} does not have reactions",
                ephemeral=True,
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        res = await get_channel_reactions(self.bot.db, message.channel.id)
        if res:
            for reaction, bots in zip(res["reaction"], res["bots"]):
                if not bots and message.author.bot:
                    continue
                try:
                    await message.add_reaction(reaction)
                except discord.errors.NotFound:
                    pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Reaction(bot))
