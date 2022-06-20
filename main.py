import json
import aiohttp
import nextcord
from nextcord import Intents, Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands
import requests
import random
import traceback
import sys
from discord_webhook import DiscordWebhook
import logging
import time
import randomstuff
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

intents = nextcord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

TESTING_GUILD_ID = 629021525978120212

colors = [0xFFE4E1, 0x00FF7F, 0xD8BFD8, 0xDC143C, 0xFF4500, 0xDEB887, 0xADFF2F, 0x800000, 0x4682B4, 0x006400, 0x808080, 0xA0522D, 0xF08080, 0xC71585, 0xFFB6C1, 0x00CED1]

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Activity(name='Naviamold!', type=nextcord.ActivityType.watching))
    print(f'We have logged in as {bot.user}')

# for fn in os.listdir('cogs'):
#     if fn.endswith('.py'):
#         name = fn[:-3]
#         bot.load_extension(f'cogs.{name}')

# @bot.slash_command(name='load', description='Load a cog.', force_global=True)
# async def load(ctx,extension):
#   bot.load_extension(f'cogs.{extension}')
#   await ctx.send(f'Loaded {extension}')

# @bot.slash_command(name='unload', description='Unload a cog.', force_global=True)
# async def unload(ctx,extension):
#   bot.unload_extension(f'cogs.{extension}')
#   await ctx.send(f'Unloaded {extension}')

# @bot.slash_command(name='reload', description='Reload a cog.', force_global=True)
# async def reload(ctx,extension):
#   bot.reload_extension(f'cogs.{extension}')
#   await ctx.send(f'Reloaded {extension}')
  

@bot.slash_command(name="ping", description="Get the bots latency")
async def pingtest(interaction : Interaction):
    await interaction.response.send_message(f'Pong: {round (bot.latency * 1000)} ms')

@bot.slash_command(name='randomrecipe', description="Get a random recipe")
async def randomrecipe(ctx, type:str=SlashOption(description="Select the type of recipe you want to get", required=False)):
  if type is None:
    r = requests.get('https://api.spoonacular.com/recipes/random?apiKey=b446d0abd80c4135bb514dcdce87a7a1')
    title_name = r.json()["recipes"][0]["title"]
    image_name = r.json()["recipes"][0]["image"]
    recipe_link = r.json()["recipes"][0]["spoonacularSourceUrl"]
    description_name = r.json()["recipes"][0]["summary"]
    scores_result1 = r.json()["recipes"][0]["aggregateLikes"]
    #scores_result2 = r.json()["recipes"][0]["spoonacularScore"]
    scores_result3 = r.json()["recipes"][0]["healthScore"]
    get_id = r.json()["recipes"][0]["id"]
    #total_score = 'Spoonaculat Score: ' + scores_result2 + '    ' + 'Health Score: ' + scores_result3 + '   ' + 'Community Score: ' + scores_result1
    embed = nextcord.Embed(title=title_name, description=f'{scores_result1} People liked 😀', color=random.choice(colors), url=recipe_link)
    for item in r.json()["recipes"][0]["extendedIngredients"]:
      #ingredients_name = item["originalName"]
      embed.add_field(name = item["nameClean"], value = item["original"], inline = True)
    embed.set_image(url = image_name)
    embed.set_footer(text = f'Product ID: {get_id}')
    await ctx.response.send_message(embed=embed)
  elif type is not None:
    r = requests.get(f'https://api.spoonacular.com/recipes/random?apiKey=b446d0abd80c4135bb514dcdce87a7a1&tags={type}')
    title_name = r.json()["recipes"][0]["title"]
    image_name = r.json()["recipes"][0]["image"]
    recipe_link = r.json()["recipes"][0]["spoonacularSourceUrl"]
    description_name = r.json()["recipes"][0]["summary"]
    scores_result1 = r.json()["recipes"][0]["aggregateLikes"]
    #scores_result2 = r.json()["recipes"][0]["spoonacularScore"]
    scores_result3 = r.json()["recipes"][0]["healthScore"]
    get_id = r.json()["recipes"][0]["id"]
    #total_score = 'Spoonaculat Score: ' + scores_result2 + '    ' + 'Health Score: ' + scores_result3 + '   ' + 'Community Score: ' + scores_result1
    embed = nextcord.Embed(title=title_name, description=f'{scores_result1} People liked 😀', color=random.choice(colors), url=recipe_link)
    for item in r.json()["recipes"][0]["extendedIngredients"]:
      #ingredients_name = item["originalName"]
      embed.add_field(name = item["nameClean"], value = item["original"], inline = True)
    embed.set_image(url = image_name)
    embed.set_footer(text = f'Product ID: {get_id}')
    await ctx.response.send_message(embed=embed)


@bot.slash_command(name='search', description='Search for a specific dish')
async def searchforrecipe(ctx, name:str=SlashOption(description='Type the dish name: ', required=False), id:int=SlashOption(description='Type the dish ID: ', required=False), type:str=SlashOption(description="Select the type of recipe you want to get", required=False)):
  if name:
    try:
      r2 = requests.get(f'https://api.spoonacular.com/recipes/complexSearch?apiKey=b446d0abd80c4135bb514dcdce87a7a1&query={name}&type={type}')
      #title_name = r2.json()["results"][0]["title"]
      image_name = r2.json()["results"][0]["image"]
      embed = nextcord.Embed(title=f'Search Results for {name}', color=random.choice(colors)) #url=recipe_link)
      for item in r2.json()["results"]:
      #ingredients_name = item["originalName"]
        embed.add_field(name = item["title"], value=f'do: **/search id {item["id"]}** for more info about this dish.', inline = True)
        
      await ctx.send(embed=embed)
    except:
      embed = nextcord.Embed(title=f'Search Results for **{name}**:', description='Sorry no results found :(' , color=random.choice(colors))
      embed.set_image(url = 'https://cdn-icons-png.flaticon.com/512/6134/6134065.png')
      await ctx.send(embed=embed)
  elif id:
    try:
      r3 = requests.get(f'https://api.spoonacular.com/recipes/{id}/information?apiKey=b446d0abd80c4135bb514dcdce87a7a1')
      title_name = r3.json()["title"]
      image_name = r3.json()["image"]
      recipe_link = r3.json()["spoonacularSourceUrl"]
      description_name = r3.json()["summary"]
      scores_result1 = r3.json()["aggregateLikes"]
      #scores_result2 = r.json()["recipes"][0]["spoonacularScore"]
      scores_result3 = r3.json()["healthScore"]
      get_id = r3.json()["id"]
      #total_score = 'Spoonaculat Score: ' + scores_result2 + '    ' + 'Health Score: ' + scores_result3 + '   ' + 'Community Score: ' + scores_result1
      embed = nextcord.Embed(title=title_name, description=f'{scores_result1} People liked 😀', color=random.choice(colors), url=recipe_link)
      for item in r3.json()["extendedIngredients"]:
        #ingredients_name = item["originalName"]
        embed.add_field(name = item["nameClean"], value = item["original"], inline = True)
      embed.set_image(url = image_name)
      embed.set_footer(text = f'Product ID: {get_id}')
      await ctx.send(embed=embed)
    except:
      embed = nextcord.Embed(title=f'Nothing was found with the **{id}** id.', description='Check if you are typing it correctly.' , color=random.choice(colors))
      embed.set_image(url = 'https://cdn-icons-png.flaticon.com/512/6134/6134065.png')
      await ctx.send(embed=embed)



@bot.slash_command(name='message', description='dm a user a message')
async def message(ctx, user:nextcord.Member=SlashOption(description='User who you want to send the text to?'), *, text=SlashOption(description='What text you want to send to that user?', required=False), embed=SlashOption(description='EXAMPLE: {"title":"Title","description":"Description","author":{"name":"Name","icon_url":""}.', required=False)):
  if text:
    text_success = await user.send(text)
    if text_success:
      await ctx.send(f'Succesfully sent the **text** message to the **{user}** \n Text message: {text}')
  if embed:
    json_object = json.loads(embed)
    title = json_object["title"]
    description = json_object["description"]
    name = json_object["author"]["name"]
    icon_url = json_object["author"]["icon_url"]
    color = json_object["color"]
    footer = json_object["footer"]["text"]
    embed2 = nextcord.Embed(title=title, description=description, color=color)
    embed2.set_author(name=name, icon_url=icon_url)
    embed2.set_footer(text=footer)
    embed_success = await user.send(embed=embed2)
    if embed_success:
      await ctx.send(f'Succesfully sent the **embed** message to the **{user}** \n embed id: {embed2}')


@bot.event
async def on_command_error(ctx, error):
 if isinstance(error, commands.MissingRequiredArgument):
   await ctx.send("Please type all the required arguments")

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send("Invalid Command")

#weather api integration
@bot.slash_command(name='weather', description='Get the weather for a specific city')
async def weather(ctx, city:str):
  r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid=09657cab1dccc3a485febaa518d7365f')
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
    embed = nextcord.Embed(title=f'Weather for {city}', color=random.choice(colors))
    embed.add_field(name='Description', value=weather_description, inline=True)
    embed.add_field(name='Temperature', value=f'{weather_temp}°C', inline=True)
    embed.add_field(name='Min Temperature', value=f'{weather_temp_min}°C', inline=True)
    embed.add_field(name='Max Temperature', value=f'{weather_temp_max}°C', inline=True)
    embed.add_field(name='Humidity', value=f'{weather_humidity}%', inline=True)
    embed.add_field(name='Wind Speed', value=f'{weather_wind}km/h', inline=True)
    embed.add_field(name='Sunrise', value=f'{weather_sunrise}', inline=True)
    embed.add_field(name='Sunset', value=f'{weather_sunset}', inline=True)
    embed.set_image(url=weather_icon_url)
    await ctx.send(embed=embed)
  else:
    await ctx.send("Invalid City")

#shorten url
@bot.slash_command(name='shorten', description='Shorten a url')
async def shorten(ctx, url:str=SlashOption(description='Type the url you want to shorten: ', required=True)):
  service = "https://url-shortener-service.p.rapidapi.com/shorten"
  payload = f"url=https://{url}"
  headers = {
	  "content-type": "application/x-www-form-urlencoded",
	  "X-RapidAPI-Host": "url-shortener-service.p.rapidapi.com",
	  "X-RapidAPI-Key": "c4f5003902msh76cac3bf466199fp11bc7djsn71bd4c60df06"
  }
  response = requests.request("POST", service, data=payload, headers=headers)
  if response.status_code == 200:
    link = json.loads(response.text)
    final = link["result_url"]
    embed = nextcord.Embed(title=f'Shortened URL for {url}', description=f'link: {final}' ,color=random.choice(colors), url=final)
    await ctx.send(embed=embed)


#random api
@bot.slash_command(name='fact', description='Get a random number or a random fact')
async def fact(ctx):
  r = requests.get('https://uselessfacts.jsph.pl/random.json?language=en')
  fact = r.json()["text"]
  embed = nextcord.Embed(title='Random fact', description=f'Random fact: {fact}', color=random.choice(colors))
  await ctx.send(embed=embed)




bot.run(os.getenv("BOT_TOKEN"))
