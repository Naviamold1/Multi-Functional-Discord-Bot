import json
from typing import List, Literal

import requests
from discord import Embed, File, Interaction, app_commands
from discord.ext import commands
from staticmap import CircleMarker, Line, StaticMap


class Transport(
    commands.GroupCog,
    name="transport",
    description="Commands related to public transport",
):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def route_autocomplete(
        self, interaction: Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        with open("assets/routes.json", "r", encoding="UTF-8") as file:
            data = json.load(file)

        return [
            app_commands.Choice(
                name=f"{item['RouteNumber']} - {item['LongName']}",
                value=item["RouteNumber"],
            )
            for item in data["Route"]
            if current.lower() in item["RouteNumber"].lower()
        ]

    async def render_map(self, route, direction):
        url = "https://transfer.msplus.ge:1443/otp/routers/ttc/routeStops"

        querystring = {"routeNumber": route, "forward": direction}

        payload = ""
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

        res = requests.get(
            url, data=payload, headers=headers, params=querystring, verify=False
        )

        m = StaticMap(300, 400, url_template="http://a.tile.osm.org/{z}/{x}/{y}.png")
        line_coordinates = []
        for item in res.json()["Stops"]:
            marker = CircleMarker((item["Lon"], item["Lat"]), "#0036FF", 2)
            line_coordinates.append([item["Lon"], item["Lat"]])
            if len(line_coordinates) >= 2:
                line = Line(line_coordinates, "red", 3)
                m.add_line(line)
                line_coordinates = [[item["Lon"], item["Lat"]]]
            m.add_marker(marker)
        return m.render().save("assets/m.png")

    @app_commands.command(name="route", description="Get transit map route")
    @app_commands.autocomplete(route=route_autocomplete)
    @app_commands.describe(
        route="Route number of the transit", direction="Direction of the transit"
    )
    async def route(
        self,
        interaction: Interaction,
        route: str,
        direction: Literal["1", "0"],
    ):
        await self.render_map(route, direction)

        f = File("assets/m.png", filename="m.png")
        embed = Embed(title=route, color=0xFF0000)
        embed.set_image(url="attachment://m.png")
        await interaction.response.send_message(embed=embed, file=f)


async def setup(bot: commands.Bot):
    await bot.add_cog(Transport(bot))
