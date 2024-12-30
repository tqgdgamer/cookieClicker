import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

class stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("stats.py is active!")

    @app_commands.command(name = "stats", description="Pull a player's data.")
    async def ping(self, interaction: discord.Interaction, user: discord.User = None):

        if user is None:
            user_name = interaction.user.name
            user_id = interaction.user.id
        else:
            user_name = user.name
            user_id = user.id

        try:
            cursor.execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
            score = cursor.fetchone()

            if score is None:
                embed = discord.Embed(
                    title = "Selection Error",
                    description = f"<:error:1285808346573836289> **No data found for {user_name}.**",
                    colour = discord.Colour.red()
                )

                await interaction.response.send_message(embed=embed)
                return
            
            cursor.execute('SELECT item_id FROM user_items WHERE user_id = ? AND purchased = 1', (user_id,))
            items = cursor.fetchall()

            multiplier = 1
            value = 1
            name_m = "None"
            name_v = "None"

            for item in items:
                item_id = item[0]
                if item_id == 3:
                    multiplier = 4
                    name_m = "Pasture Raised Eggs"
                elif item_id == 2:
                    multiplier = 3
                    name_m = "Better Sugar"
                elif item_id == 1:
                    multiplier = 2
                    name_m = "Better Flour"

                if item_id == 6:
                    value = 10
                    name_v = "Macadamia Nuts"
                elif item_id == 5:
                    value = 5
                    name_v = "Chocolate Chips"
                elif item_id == 4:
                    value = 2
                    name_v = "Organic Butter"

        except sqlite3.Error as e:
            print(f"Database error: {e}")

        embed = discord.Embed(
            description = f"# {user_name}'s Stats\n<:alert:1287522413935853721> **Cookies:** {score[0]}\n## Best Cookie Buffs:\n**{name_m}** | Multiplier: **{multiplier}x**\n**{name_v}** | Cookies Per Click: **{value} cookies**",
            colour = discord.Colour.from_str("#ff6b00")
        )

        await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(stats(client), guilds=client.guilds)