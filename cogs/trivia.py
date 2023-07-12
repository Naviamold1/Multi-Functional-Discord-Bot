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

colors = [
    0xFFE4E1,
    0x00FF7F,
    0xD8BFD8,
    0xDC143C,
    0xFF4500,
    0xDEB887,
    0xADFF2F,
    0x800000,
    0x4682B4,
    0x006400,
    0x808080,
    0xA0522D,
    0xF08080,
    0xC71585,
    0xFFB6C1,
    0x00CED1,
]


class CustomButton(discord.ui.Button["Btn"]):
    def __init__(self, answer, **kwargs):
        super().__init__(**kwargs)
        self.answer = answer

    async def callback(self, interaction: Interaction):
        view: Btn = self.view

        for button in view.children:
            button.disabled = True

        if self.label == self.answer:
            self.style = discord.ButtonStyle.green
            users.append(f"{interaction.user.name}#{interaction.user.discriminator}")
        else:
            self.style = discord.ButtonStyle.red
            for item in view.children:
                if item.label == self.answer:
                    item.style = discord.ButtonStyle.blurple

        message_content = (
            f"✅ Correct - {interaction.user.mention}"
            if self.answer == self.label
            else f"❌ Wrong - {interaction.user.mention}"
        )
        await interaction.response.edit_message(content=message_content, view=view)
        view.stop()


class Btn(discord.ui.View):
    def __init__(self, *choices, answer: str = None, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.choices = choices
        self.answer = answer
        self.message = None

        buttons = []
        for item in self.choices:
            for i in item:
                buttons.append(CustomButton(label=i, answer=self.answer))
        random.shuffle(buttons)
        answer_index = random.randint(0, len(buttons))
        buttons.insert(
            answer_index, CustomButton(label=self.answer, answer=self.answer)
        )
        for button in buttons:
            self.add_item(button)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            if item.label == self.answer:
                item.style = discord.ButtonStyle.blurple

        await self.message.edit(view=self)


class Trivia(
    commands.GroupCog,
    discord.ui.View,
    name="trivia",
    description="Trivia related commands",
):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.trivia_in_progress = []
        self.trivia_end = []

    @app_commands.command(name="flags", description="Play flag trivia")
    @app_commands.describe(
        rounds="Amount of Rounds you want to play",
        time="Time limit of each round in seconds",
        continent="Only include a specific Continent",
        buttons="Include buttons for each answer aka easy mode",
    )
    @app_commands.choices(
        continent=[
            Choice(name="Europe", value="Europe"),
            Choice(name="Asia", value="Asia"),
            Choice(name="Americas", value="Americas"),
            Choice(name="Africa", value="Africa"),
            Choice(name="Oceania", value="Oceania"),
        ]
    )
    async def flags(
        self,
        interaction: Interaction,
        continent: Optional[Choice[str]],
        rounds: int = 5,
        time: int = 60,
        buttons: bool = False,
    ):
        for server in self.trivia_in_progress:
            if server == interaction.guild_id:
                return await interaction.response.send_message(
                    "A game is already in progress, please wait for it to finish.",
                    ephemeral=True,
                )
        self.trivia_in_progress.append(interaction.guild_id)
        round_num = 1
        global users
        users = []
        await interaction.response.defer()

        with open("assets/list.json", "r") as file:
            data = json.load(file)
        if continent is not None:
            data = [cont for cont in data if cont["continent"] == continent.value]
        start = tm.time()
        previously_selected = []
        for _ in range(rounds):
            if len(previously_selected) == len(data):
                previously_selected = []
            country_choice = random.choice(data)
            other_choice = random.sample(
                [x["country"] for x in data if x != country_choice], 3
            )
            while country_choice["country"] in previously_selected:
                country_choice = random.choice(data)
            previously_selected.append(country_choice["country"])
            embed = Embed(
                title=f"Round {round_num} of {rounds}",
                description=f"Time limit: <t:{int(tm.time())+time}:R>",
                timestamp=discord.utils.utcnow(),
                color=random.choice(colors),
            )
            embed.set_author(name="Guess the Flag!")
            embed.set_image(url=country_choice["flag"])

            if buttons:
                view = Btn(other_choice, answer=country_choice["country"], timeout=time)
                view.message = await interaction.followup.send(embed=embed, view=view)
                await view.wait()

            elif not buttons:
                await interaction.followup.send(embed=embed)

                def check(m):
                    js = str(country_choice["country"])
                    js = js.lower()
                    msg = str(m.content)
                    msg = msg.lower()
                    js = js.replace(" ", "")
                    msg = msg.replace(" ", "")
                    js = js.replace("-", "")
                    msg = msg.replace("-", "")
                    ali = country_choice.get("alias", None)
                    if ali:
                        if type(ali) == list:
                            for i in ali:
                                i = i.lower()
                                i = i.replace(" ", "")
                                i = i.replace("-", "")
                                if msg == i:
                                    return True
                        else:
                            ali = ali.lower()
                            ali = ali.replace(" ", "")
                            ali = ali.replace("-", "")
                            if msg == ali:
                                return True
                    return msg == js

                try:
                    res = await self.bot.wait_for("message", timeout=time, check=check)
                except TimeoutError:
                    await interaction.followup.send(
                        f":x: No one gave the correct answer. It was **{country_choice['country']}**"
                    )
                else:
                    users.append(f"{res.author.name}#{res.author.discriminator}")
                    message = await res.channel.fetch_message(res.id)
                    await message.add_reaction("✅")
            if interaction.guild_id in self.trivia_end:
                self.trivia_end.remove(interaction.guild_id)
                return
            round_num += 1
        end = tm.time()
        score_embed = Embed(
            title="Final Scores!", color=discord.Color.from_rgb(148, 120, 192)
        )
        lu = Counter(users)
        lu = lu.most_common()
        for i, (item, count) in enumerate(lu):
            if i == 0:
                item = f":first_place: {item}"
            elif i == 1:
                item = f":second_place: {item}"
            elif i == 2:
                item = f":third_place: {item}"
            else:
                item = item

            score_embed.add_field(name=str(item), value=count, inline=False)
        score_embed.set_footer(
            text=f"Time taken: {round(end - start, 2)}s / {round((end - start)/60, 2)}min"
        )
        await interaction.followup.send(embed=score_embed)
        self.trivia_in_progress.remove(interaction.guild_id)

    @app_commands.command(name="maps", description="Play map trivia")
    @app_commands.describe(
        rounds="Amount of Rounds you want to play",
        time="Time limit of each round in seconds",
        continent="Only include a specific Continent",
        buttons="Include buttons for each answer aka easy mode",
    )
    @app_commands.choices(
        continent=[
            Choice(name="Europe", value="Europe"),
            Choice(name="Asia", value="Asia"),
            Choice(name="Americas", value="Americas"),
            Choice(name="Africa", value="Africa"),
            Choice(name="Oceania", value="Oceania"),
        ]
    )
    async def maps(
        self,
        interaction: Interaction,
        continent: Optional[Choice[str]],
        rounds: int = 5,
        time: int = 60,
        buttons: bool = False,
    ):
        for server in self.trivia_in_progress:
            if server == interaction.guild_id:
                return await interaction.response.send_message(
                    "A game is already in progress, please wait for it to finish.",
                    ephemeral=True,
                )
        self.trivia_in_progress.append(interaction.guild_id)
        round_num = 1
        global users
        users = []
        await interaction.response.defer()

        with open("assets/list.json", "r") as file:
            data = json.load(file)
        if continent is not None:
            data = [cont for cont in data if cont["continent"] == continent.value]
        start = tm.time()
        previously_selected = []
        for _ in range(rounds):
            if len(previously_selected) == len(data):
                previously_selected = []
            country_choice = random.choice(data)
            other_choice = random.sample(
                [x["country"] for x in data if x != country_choice], 3
            )
            while country_choice["country"] in previously_selected:
                country_choice = random.choice(data)
            previously_selected.append(country_choice["country"])
            embed = Embed(
                title=f"Round {round_num} of {rounds}",
                description=f"Time limit: <t:{int(tm.time())+time}:R>",
                timestamp=discord.utils.utcnow(),
                color=random.choice(colors),
            )
            embed.set_author(name="Guess the Country!")
            embed.set_image(url=country_choice["map"])
            if buttons:
                view = Btn(other_choice, answer=country_choice["country"], timeout=time)
                view.message = await interaction.followup.send(embed=embed, view=view)
                await view.wait()
            elif not buttons:
                await interaction.followup.send(embed=embed)

                def check(m):
                    js = str(country_choice["country"])
                    js = js.lower()
                    msg = str(m.content)
                    msg = msg.lower()
                    js = js.replace(" ", "")
                    msg = msg.replace(" ", "")
                    js = js.replace("-", "")
                    msg = msg.replace("-", "")
                    ali = country_choice.get("alias", None)
                    if ali:
                        if type(ali) == list:
                            for i in ali:
                                i = i.lower()
                                i = i.replace(" ", "")
                                i = i.replace("-", "")
                                if msg == i:
                                    return True
                        else:
                            ali = ali.lower()
                            ali = ali.replace(" ", "")
                            ali = ali.replace("-", "")
                            if msg == ali:
                                return True
                    return msg == js

                try:
                    res = await self.bot.wait_for("message", timeout=time, check=check)
                except TimeoutError:
                    await interaction.followup.send(
                        f":x: No one gave the correct answer. It was **{country_choice['country']}**"
                    )
                else:
                    users.append(f"{res.author.name}#{res.author.discriminator}")
                    message = await res.channel.fetch_message(res.id)
                    await message.add_reaction("✅")
            if interaction.guild_id in self.trivia_end:
                self.trivia_end.remove(interaction.guild_id)
                return
            round_num += 1
        end = tm.time()
        score_embed = Embed(
            title="Final Scores!", color=discord.Color.from_rgb(148, 120, 192)
        )
        lu = Counter(users)
        lu = lu.most_common()
        for i, (item, count) in enumerate(lu):
            if i == 0:
                item = f":first_place: {item}"
            elif i == 1:
                item = f":second_place: {item}"
            elif i == 2:
                item = f":third_place: {item}"
            else:
                item = item

            score_embed.add_field(name=str(item), value=count, inline=False)
        score_embed.set_footer(
            text=f"Time taken: {round(end - start, 2)}s / {round((end - start)/60, 2)}min"
        )
        await interaction.followup.send(embed=score_embed)
        self.trivia_in_progress.remove(interaction.guild_id)

    @app_commands.command(name="end", description="Ends ongoing trivia")
    async def end(self, interaction: Interaction):
        if interaction.guild_id in self.trivia_in_progress:
            if interaction.guild_id not in self.trivia_end:
                self.trivia_end.append(interaction.guild_id)
                self.trivia_in_progress.remove(interaction.guild_id)
            await interaction.response.send_message("Trivia match ended.")
        else:
            await interaction.response.send_message(
                "No trivia match is currently in progress.", ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Trivia(bot))
