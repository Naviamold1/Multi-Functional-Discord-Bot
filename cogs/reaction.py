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
    try:
        reaction_cache.pop(channel_id)
        return {"status": 200, "message": "success cache update"}
    except KeyError:
        return {
            "status": 403,
            "message": f"channel_id: {channel_id} was not found in cache",
        }


class Reaction(commands.GroupCog, name="reaction", description="Manage auto-reactions"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="add",
        description="Add auto-reaction(s) on message sent in that channel",
    )
    @app_commands.describe(
        channel="The channel to add the auto-reaction(s) to",
        reaction="The reaction that should be auto-reacted",
        bots="If bot should auto-react to messages sent by bots / webhooks",
    )
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
            embed = discord.Embed(
                title="Success",
                description="Auto-reactions have been started",
                color=discord.Color.green(),
            )
            embed.add_field(name="Channel", value=channel.mention)
            embed.add_field(name="Reaction", value=reaction)
            embed.add_field(name="Bots", value=bots)
            await interaction.response.send_message(embed=embed)

        except pgexec.UniqueViolationError:
            embed = discord.Embed(
                title="Error",
                description=f"The channel {channel.mention} already has started reactions with emoji {reaction}",
                color=discord.Color.red(),
            )
            embed.add_field(name="field", value="value", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="configure",
        description="Configure bots presence on auto-reaction(s) on message sent in that channel currently",
    )
    @app_commands.describe(
        channel="The channel to modify the auto-reaction(s) to",
        reaction="The auto-reaction that will undergo modification",
        bots="If bot should auto-react to messages sent by bots / webhooks",
    )
    async def configure(
        self,
        interaction: Interaction,
        channel: discord.TextChannel,
        reaction: str,
        bots: bool,
    ):
        res = await self.bot.db.execute(
            f"UPDATE Reaction SET bots = $1 WHERE channel_id = $2 AND reaction = E'{reaction}'",
            bots,
            channel.id,
        )
        if res:
            update_cache(channel.id)
            await interaction.response.send_message(
                f"Successfully Update {channel.mention} with emoji {reaction} with bots {bots}"
            )

    @app_commands.command(
        name="remove",
        description="Remove auto-reaction(s) on message sent in that channel",
    )
    @app_commands.describe(
        channel="The channel to remove the auto-reaction(s) to",
        reaction="The reaction that should be removed from auto-reacted",
    )
    async def remove(
        self, interaction: Interaction, channel: discord.TextChannel, reaction: str
    ):
        await self.bot.db.execute(
            f"DELETE FROM Reaction WHERE channel_id = $1 AND reaction = E'{reaction}'",
            channel.id,
        )
        uc = update_cache(channel.id)
        if uc["status"] == 200:
            embed = discord.Embed(
                title="Success",
                description=f"Auto-reactions have been removed for {channel.mention} with emoji {reaction}",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)
        elif uc["status"] == 403:
            embed = discord.Embed(
                title="Error",
                description=f"The channel {channel.mention} does not have auto-reaction with emoji {reaction}",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="list", description="List all auto-reactions")
    @app_commands.describe(channel="The channel to list the auto-reactions")
    async def list(self, interaction: Interaction, channel: discord.TextChannel):
        res = await get_channel_reactions(self.bot.db, channel.id)
        if res:
            embed = discord.Embed(
                title="List of Reactions",
                description=f"List of Reactions for Channel {channel.mention}",
                color=discord.Color.yellow(),
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
