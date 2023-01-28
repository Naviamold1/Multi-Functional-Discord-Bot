import json
import os
import random
import time as tm
from collections import Counter
from typing import Optional

import discord
from discord import Embed, Interaction, app_commands
from discord.app_commands import Choice
from discord.ext import commands

colors = [0xFFE4E1, 0x00FF7F, 0xD8BFD8, 0xDC143C, 0xFF4500, 0xDEB887, 0xADFF2F, 0x800000,
          0x4682B4, 0x006400, 0x808080, 0xA0522D, 0xF08080, 0xC71585, 0xFFB6C1, 0x00CED1]


class Trivia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.trivia_in_progeress = []
        self.trivia_end = []

    @app_commands.command(name='trivia-flags', description='Play flag trivia')
    @app_commands.describe(rounds="Ammount of Rounds you want to play", time="Time limit of each round in seconds", continent="Only include a specific Continent")
    @app_commands.choices(
        continent=[
            Choice(name="Europe", value="Europe"),
            Choice(name="Asia", value="Asia"),
            Choice(name="Americas", value="Asia"),
            Choice(name="Africa", value='Africa'),
            Choice(name="Oceania", value="Oceania")
        ]
    )
    async def triviageo(self, interaction: Interaction, continent: Optional[Choice[str]], rounds: int = 1, time: int = 60):
        for server in self.trivia_in_progeress:
            if server == interaction.guild_id:
                return await interaction.response.send_message("A game is already in progress, please wait for it to finish.", ephemeral=True)
        self.trivia_in_progeress.append(interaction.guild_id)
        round_num = 1
        users = []
        await interaction.response.defer()

        with open('assets/list.json', 'r') as file:
            data = json.load(file)
        if continent is not None:
            data = [cont for cont in data if cont["continent"] == continent.value]

        for _ in range(rounds):
            for end in self.trivia_end:
                if end == interaction.guild_id:
                    return
                    
            a = random.choice(data)
            print(os.path.split(a["image"])[1])
            embed = Embed(title=f'Round {round_num} of {rounds}',
                          description=f'Time limit: <t:{int(tm.time())+time}:R>', timestamp=discord.utils.utcnow(), color=random.choice(colors))
            embed.set_author(name="Guess the Flag!")
            filee = discord.File(
                rf"{a['image']}", filename=rf"{os.path.split(a['image'])[1]}")
            embed.set_image(
                url=rf'attachment://{os.path.split(a["image"])[1]}')
            await interaction.followup.send(embed=embed, file=filee)

            def check(m):
                js = str(a["country"])
                js = js.lower()
                msg = str(m.content)
                msg = msg.lower()
                js = js.replace(" ", '')
                msg = msg.replace(" ", '')
                return msg == js
            try:
                res = await self.bot.wait_for('message', timeout=time, check=check)
            except TimeoutError:
                await interaction.followup.send(f"No one gave the correct answer. It was **{a['country']}**")
            else:
                users.append(f'{res.author.name}#{res.author.discriminator}')
                await interaction.followup.send('Correct <@{.author.id}> it was **{country}** !'.format(res, country=a["country"]))
            round_num += 1

        score_embed = Embed(title="Final Scores!",
                            color=discord.Color.from_rgb(148, 120, 192))
        lu = Counter(users)
        lu = lu.most_common()
        for item, count in lu:
            score_embed.add_field(name=str(item), value=count, inline=False)
        await interaction.followup.send(embed=score_embed)
        self.trivia_in_progeress.remove(interaction.guild_id)

    @app_commands.command(name="trivia-end", description="Ends Ongoing Trivia")
    async def triviaend(self, interaction: Interaction):
        if interaction.guild_id in self.trivia_in_progeress:
            self.trivia_end.append(interaction.guild_id)
            await interaction.response.send_message("Trivia match ended.")
        else:
            await interaction.response.send_message("No ongoing trivia match to end.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Trivia(bot))
