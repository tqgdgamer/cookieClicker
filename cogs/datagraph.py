import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

from dotenv import load_dotenv

import os
import asyncio

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.font_manager as fm
import mplcyberpunk

load_dotenv()

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

def graph():

    cookie_values = "SELECT score FROM users ORDER BY score DESC LIMIT 30"
    df = pd.read_sql_query(cookie_values, conn)

    y = df['score']
    x = range(1, len(y)+1)

    font_path = f'{os.getenv("FONT_PATH")}'

    custom_font = fm.FontProperties(fname=font_path)

    plt.style.use("cyberpunk")

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o', color='#08F7FE')  

    plt.title(f'TOP COOKIE CLICKERS', fontproperties=custom_font, fontsize=20)
    plt.xlabel('RANK', fontproperties=custom_font)
    plt.ylabel('COOKIES', fontproperties=custom_font)
    plt.tick_params(colors='#AAAAAA')

    ax = plt.gca()
    ax.grid(color='#2A3459')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_yscale('log')

    for label in ax.get_xticklabels():
        label.set_fontproperties(custom_font)
    for label in ax.get_yticklabels():
        label.set_fontproperties(custom_font)

    mplcyberpunk.add_glow_effects()

    image_path = 'cookie_graph.png'
    return y, image_path

class datagraph(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("datagraph.py is active!")

    @app_commands.command(name = "datagraph", description="User graph of the top players")
    async def datagraph(self, interaction: discord.Interaction):

        y, image_path = graph()

        plt.savefig(image_path, dpi=300)

        file = discord.File(image_path, filename="cookie_graph.png")

        embed = discord.Embed(
            title = "Cookie Wizard",
            description = f"<:info:1287522521448448061> Here is a graph of the **top {len(y)}** cookie clickers!",
            colour = discord.Colour.from_str("#08F7FE"),
        )
        embed.set_image(url="attachment://cookie_graph.png")

        await interaction.response.send_message(file=file, embed=embed)

        file.close()

        await asyncio.sleep(1)
        if os.path.exists(image_path):
            os.remove(image_path)

async def setup(client: commands.Bot):
    await client.add_cog(datagraph(client), guilds=client.guilds)