import os
import urllib
from typing import Optional

import discord
import requests
from discord import Interaction, app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Util(commands.Cog, description="Utility commands"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="weather", description="Get the weather for a specific location"
    )
    @app_commands.describe(
        location="Enter the name of the location for which you would like to view the weather "
    )
    async def weather(self, interaction: Interaction, location: str):
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={os.getenv("WEATHER_SECRET")}&units=metric'
        )
        if r.status_code == 200:
            weather_data = r.json()
            weather_description = weather_data["weather"][0]["description"]
            weather_temp = weather_data["main"]["temp"]
            weather_temp_min = weather_data["main"]["temp_min"]
            weather_temp_max = weather_data["main"]["temp_max"]
            weather_humidity = weather_data["main"]["humidity"]
            weather_wind = weather_data["wind"]["speed"]
            weather_sunrise = weather_data["sys"]["sunrise"]
            weather_sunset = weather_data["sys"]["sunset"]
            weather_icon = weather_data["weather"][0]["icon"]
            weather_icon_url = f"http://{weather_icon}.png"
            embed = discord.Embed(
                title=f"Weather for {location}", color=discord.Color.blue()
            )
            embed.add_field(name="Description", value=weather_description, inline=True)
            embed.add_field(name="Temperature", value=f"{weather_temp}°C", inline=True)
            embed.add_field(
                name="Min Temperature", value=f"{weather_temp_min}°C", inline=True
            )
            embed.add_field(
                name="Max Temperature", value=f"{weather_temp_max}°C", inline=True
            )
            embed.add_field(name="Humidity", value=f"{weather_humidity}%", inline=True)
            embed.add_field(name="Wind Speed", value=f"{weather_wind}km/h", inline=True)
            embed.add_field(name="Sunrise", value=f"{weather_sunrise}", inline=True)
            embed.add_field(name="Sunset", value=f"{weather_sunset}", inline=True)
            embed.set_image(url=weather_icon_url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Invalid Location", ephemeral=True)

    @app_commands.command(name="shorten", description="Shorten a url")
    @app_commands.describe(url="Enter the url you would like to shorten")
    async def shorten(self, interaction: Interaction, url: str, alias: Optional[str]):
        key = os.getenv("CUTTLY_SECRET")
        url = urllib.parse.quote(url)
        site = f"http://cutt.ly/api/api.php?key={key}&short={url}"
        if alias:
            site += f"&name={alias}"
        r = requests.get(site)
        res = r.json()["url"]
        status_messages = {
            1: "The shortened link comes from the domain that shortens the link, i.e. the link has already been shortened",
            2: "The entered link is not a link",
            3: "The preferred link name is already taken",
            4: "Invalid API key",
            5: "The link has not passed the validation. Includes invalid characters",
            6: "The link provided is from a blocked domain",
            7: "OK - the link has been shortened",
            8: "You have reached your monthly link limit. You can upgrade your subscription plan to add more links.",
        }

        error = status_messages.get(int(res["status"]), "Invalid status")
        if status_messages[7]:
            embed = discord.Embed(
                title=res["title"], color=discord.Color.green(), url=res["shortLink"]
            )
            embed.add_field(name="Shortened Link", value=res["shortLink"], inline=False)
            embed.add_field(name="Original Link", value=res["fullLink"], inline=False)
            embed.set_footer(text=res["date"])
            await interaction.response.send_message(
                content=res["shortLink"], embed=embed
            )
        else:
            embed = discord.Embed(
                title="Oops an Error occurred",
                description=error,
                color=discord.Color.red(),
            )
            embed.set_image(
                url="https://media.discordapp.net/attachments/654748925672161300/1100876703078813767/error-icon-25266.png"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="fact", description="Get a random fact")
    async def fact(self, interaction: Interaction):
        r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        fact = r.json()["text"]
        embed = discord.Embed(
            title="Random fact", description=fact, color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))
