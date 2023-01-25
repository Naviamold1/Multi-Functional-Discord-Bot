import random
import urllib
from typing import Optional
import os
import discord
import requests
from discord import Interaction, app_commands
from discord.ext import commands
from dotenv import load_dotenv

colors = [0xFFE4E1, 0x00FF7F, 0xD8BFD8, 0xDC143C, 0xFF4500, 0xDEB887, 0xADFF2F, 0x800000,
          0x4682B4, 0x006400, 0x808080, 0xA0522D, 0xF08080, 0xC71585, 0xFFB6C1, 0x00CED1]

load_dotenv

class Util(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='weather', description='Get the weather for a specific location')
    @app_commands.describe(location="Enter the name of the location for which you would like to view the weather ")
    async def weather(self, interaction: Interaction, location: str):
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={os.getenv}')
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
            weather_icon_url = f'http://{weather_icon}.png'
            embed = discord.Embed(
                title=f'Weather for {location}', color=random.choice(colors))
            embed.add_field(name='Description',
                            value=weather_description, inline=True)
            embed.add_field(name='Temperature',
                            value=f'{weather_temp}°C', inline=True)
            embed.add_field(name='Min Temperature',
                            value=f'{weather_temp_min}°C', inline=True)
            embed.add_field(name='Max Temperature',
                            value=f'{weather_temp_max}°C', inline=True)
            embed.add_field(name='Humidity',
                            value=f'{weather_humidity}%', inline=True)
            embed.add_field(name='Wind Speed',
                            value=f'{weather_wind}km/h', inline=True)
            embed.add_field(
                name='Sunrise', value=f'{weather_sunrise}', inline=True)
            embed.add_field(
                name='Sunset', value=f'{weather_sunset}', inline=True)
            embed.set_image(url=weather_icon_url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Invalid Location")

    @app_commands.command(name='shorten', description='Shorten a url')
    @app_commands.describe(url="Enter the url you would like to shorten")
    async def shorten(self, interaction: Interaction, url: str, alias: Optional[str]):
        key = os.getenv("CUTTLY_SECRET")
        url = urllib.parse.quote(url)
        site = f'http://cutt.ly/api/api.php?key={key}&short={url}'
        if alias:
            site += f'&name={alias}'
        r = requests.get(site)
        res = r.json()
        status_messages = {
            1: "The shortened link comes from the domain that shortens the link, i.e. the link has already been shortened",
            2: "The entered link is not a link",
            3: "The preferred link name is already taken",
            4: "Invalid API key",
            5: "The link has not passed the validation. Includes invalid characters",
            6: "The link provided is from a blocked domain",
            7: "OK - the link has been shortened",
            8: "You have reached your monthly link limit. You can upgrade your subscription plan to add more links."
        }

        status = res["url"]["status"]

        error = status_messages.get(int(status), "Invalid status")
        if not status_messages[7]:
            embed = discord.Embed(
                title=f'Shortened URL for {res["fullLink"]}', description=f'link: {res["shortLink"]}', color=random.choice(colors), url=res["shortLink"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title=f'Oops an Error Occured', description=f'{error}', color=random.choice(colors))
            embed.set_image(url="https://www.freeiconspng.com/thumbs/error-icon/error-icon-32.png")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='fact', description='Get a random number or a random fact')
    async def fact(self, interaction: Interaction):
        r = requests.get(
            'https://uselessfacts.jsph.pl/random.json?language=en')
        fact = r.json()["text"]
        embed = discord.Embed(
            title='Random fact', description=f'{fact}', color=random.choice(colors))
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))
