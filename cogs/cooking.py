import os
import random
from typing import Optional

import discord
import requests
from discord import Interaction, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

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


class Cooking(
    commands.GroupCog,
    name="recipe",
    description="Command related to recipes and cooking",
):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="random", description="Get a random recipe")
    @app_commands.describe(tag="Select the type of recipe you want to get")
    async def random_recipe(self, interaction: Interaction, tag: Optional[str]):
        url = f'https://api.spoonacular.com/recipes/random?apiKey={os.getenv("SPOONACULAR_SECRET")}'
        if tag is not None:
            url += f"&tags={tag}"
        r = requests.get(url)
        if r.status_code != 200:
            return await interaction.response.send_message(
                "Something went wrong, please try again later", ephemeral=True
            )
        result = r.json()["recipes"][0]
        title_name = result["title"]
        image_name = result["image"]
        recipe_link = result["spoonacularSourceUrl"]
        scores_result1 = result["aggregateLikes"]
        get_id = result["id"]
        embed = discord.Embed(
            title=title_name,
            description=f"{scores_result1} Person liked this recipe 😀",
            color=random.choice(colors),
            url=recipe_link,
        )
        for item in result["extendedIngredients"]:
            embed.add_field(name=item["nameClean"], value=item["original"], inline=True)
        embed.set_image(url=image_name)
        embed.set_footer(text=f"Product ID: {get_id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="search", description="Search for a specific dish")
    @app_commands.describe(
        method="Select how you want to search for a dish",
        query="Enter the name or id of the dish you want to search for",
        tag="Select the type of recipe you want to get",
    )
    @app_commands.choices(
        method=[
            Choice(name="name", value="name"),
            Choice(name="id", value="id"),
        ]
    )
    async def search_recipe(
        self,
        interaction: Interaction,
        method: Choice[str],
        query: str,
        tag: Optional[str],
    ):
        url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={os.getenv("SPOONACULAR_SECRET")}&addRecipeInformation=True'
        if method.value == "name":
            url += f"&query={query}&type={tag}"
        elif method.value == "id":
            url = f'https://api.spoonacular.com/recipes/{query}/information?apiKey={os.getenv("SPOONACULAR_SECRET")}'
        try:
            r = requests.get(url)
            result = r.json()["results"][0] if method.value == "name" else r.json()
            title_name = result["title"]
            image_name = result["image"]
            recipe_link = result["spoonacularSourceUrl"]
            scores_result1 = result["aggregateLikes"]
            get_id = result["id"]
            embed = discord.Embed(
                title=f"Search Results for {query}"
                if method.value == "name"
                else title_name,
                description=f"{scores_result1} Person liked this recipe 😀"
                if method.value == "id"
                else "",
                color=discord.Color.green(),
                url=recipe_link,
            )
            if method.value == "name":
                for item in r.json()["results"]:
                    embed.add_field(
                        name=item["title"],
                        value=f'do: **/recipe search method:id query:{item["id"]}** for more info about this dish.',
                        inline=True,
                    )
            else:
                for item in result["extendedIngredients"]:
                    embed.add_field(
                        name=item["nameClean"], value=item["original"], inline=True
                    )
                embed.set_footer(text=f"Product ID: {get_id}")
            embed.set_image(url=image_name)
            await interaction.response.send_message(embed=embed)
        except requests.exceptions.JSONDecodeError:
            embed = discord.Embed(
                title=f"Nothing was found with the id **{query}**"
                if method.value == "id"
                else f"Nothing was found with the name **{query}**",
                description="Check if you are typing it correctly.",
                color=discord.Color.red(),
            )
            embed.set_image(
                url="https://cdn-icons-png.flaticon.com/512/6134/6134065.png"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Cooking(bot))
