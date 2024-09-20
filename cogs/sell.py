import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER,
        money INTEGER
    )
''')
conn.commit()

# add/update user data
def add_or_update_user(user_id, username, score, money):
    cursor.execute('''
        INSERT INTO users (user_id, username, score, money)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) 
        DO UPDATE SET username = excluded.username, score = excluded.score, money = excluded.money
    ''', (user_id, username, score, money))
    conn.commit()

# pull user data
def get_user_stats(user_id):
    cursor.execute('SELECT score, money FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        score, money = result[0], result[1]
        return score, money
    return None

# cmd   
class sell(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("sell.py is active!")

    @app_commands.command(name="sell", description="Sell your cookies!")
    async def sell(self, interaction: discord.Interaction, amount: int):

        user_id = interaction.user.id
        username = str(interaction.user)

        stats = get_user_stats(user_id)
        
        if stats:
            score, money = stats
        else:
            score, money = 0,0

        if score - amount >= 0:
            score = score - amount
            money = money + amount

            add_or_update_user(user_id, username, score, money)
    
            embed = discord.Embed(
                title = "Sell Alert!",
                description = f"You have sold {amount} cookies! for ${amount}. You now have {score} cookies left!",
                colour = discord.Colour.blue()
            )

            await interaction.response.send_message(embed=embed)

        elif score-amount < 0:

            embed = discord.Embed(
                title = "Error!",
                description = f"You don't have that amount of cookies silly!",
                colour = discord.Colour.red()
            )

            await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(sell(client), guilds=client.guilds)
    