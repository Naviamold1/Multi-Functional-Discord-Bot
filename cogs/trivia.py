import json
import random
import time as tm
from collections import Counter
from typing import Optional

import discord
from discord import Embed, Interaction, app_commands
from discord.app_commands import Choice, Group
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

users = []


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

    geography = Group(name="geography", description="Geography trivia subgroup")

    async def get_list(self, interaction, continent):
        round_num = 0
        await interaction.response.defer()

        with open("assets/list.json", "r") as file:
            data = json.load(file)
        if continent is not None:
            data = [cont for cont in data if cont["continent"] == continent.value]
        start = tm.time()
        previously_selected = []
        return round_num, data, start, previously_selected

    async def main_logic(
        self,
        interaction,
        rounds,
        time,
        buttons,
        round_num,
        data,
        previously_selected,
        mode,
    ):
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
            description=f"Round ends <t:{int(tm.time())+time}:R>",
            timestamp=discord.utils.utcnow(),
            color=random.choice(colors),
        )
        embed.set_author(
            name="Guess the Flag!" if mode == "flag" else "Guess the Country!"
        )
        embed.set_image(url=country_choice[mode])

        if buttons:
            view = Btn(other_choice, answer=country_choice["country"], timeout=time)
            view.message = await interaction.followup.send(embed=embed, view=view)
            await view.wait()

        elif not buttons:
            await interaction.followup.send(embed=embed)

            def check(m):
                country = (
                    str(country_choice.get("country", ""))
                    .lower()
                    .replace(" ", "")
                    .replace("-", "")
                )
                msg = str(m.content).lower().replace(" ", "").replace("-", "")
                alias = country_choice.get("alias", None)

                if alias:
                    if isinstance(alias, list):
                        for i in alias:
                            i = i.lower().replace(" ", "").replace("-", "")
                            if msg == i:
                                return True
                    else:
                        alias = alias.lower().replace(" ", "").replace("-", "")
                        if msg == alias:
                            return True

                return msg == country

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

    async def final_part(self, interaction, start):
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

    @geography.command(name="guess", description="Play flag trivia")
    @app_commands.describe(
        rounds="Amount of Rounds you want to play",
        time="Time limit of each round in seconds",
        quiz="The type of quiz you want to play",
        continent="Only include a specific Continent",
        buttons="Include buttons for each answer aka easy mode",
    )
    @app_commands.choices(
        quiz=[Choice(name="Flags", value="Flags"), Choice(name="Maps", value="Maps")],
        continent=[
            Choice(name="Europe", value="Europe"),
            Choice(name="Asia", value="Asia"),
            Choice(name="Americas", value="Americas"),
            Choice(name="Africa", value="Africa"),
            Choice(name="Oceania", value="Oceania"),
        ],
    )
    async def country_guess(
        self,
        interaction: Interaction,
        quiz: Choice[str],
        continent: Optional[Choice[str]],
        rounds: int = 5,
        time: int = 60,
        buttons: bool = False,
    ):
        if rounds > 197:
            await interaction.response.send_message(
                "197 is the **max** amount of rounds allowed.", ephemeral=True
            )
            rounds = 197

        if interaction.guild_id in self.trivia_in_progress:
            return await interaction.response.send_message(
                "A game is already in progress, please wait for it to finish.",
                ephemeral=True,
            )
        self.trivia_in_progress.append(interaction.guild_id)

        round_num, data, start, previously_selected = await self.get_list(
            interaction, continent
        )

        for _ in range(rounds):
            round_num += 1
            if interaction.guild_id in self.trivia_end:
                self.trivia_end.remove(interaction.guild_id)
                break
            await self.main_logic(
                interaction,
                rounds,
                time,
                buttons,
                round_num,
                data,
                previously_selected,
                mode="flag" if quiz.value == "Flags" else "map",
            )

        await self.final_part(interaction, start)

    @app_commands.command(name="end", description="Ends ongoing trivia")
    async def end(self, interaction: Interaction):
        if interaction.guild_id in self.trivia_in_progress:
            if interaction.guild_id not in self.trivia_end:
                self.trivia_end.append(interaction.guild_id)
            await interaction.response.send_message("Trivia match ended.")
        else:
            await interaction.response.send_message(
                "No trivia match is currently in progress here.", ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Trivia(bot))
