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

# button
class CCButton(discord.ui.View):
    def __init__(self, author_id = int):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.value = None
        
    @discord.ui.button(label="🍪", style=discord.ButtonStyle.blurple, custom_id='persistent_view:CC')
    async def menu1(self, interaction: discord.Interaction,  button: discord.ui.Button):
        
        if interaction.user.id != self.author_id:

            embed = discord.Embed(
                title='Sorry! This is someone\'s button!',
                colour=discord.Colour.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        else:
            user_id = interaction.user.id
            username = str(interaction.user)

            stats = get_user_stats(user_id)
            
            if stats:
                score, money = stats
            else:
                score, money = 0,0
            
            score += 1

            add_or_update_user(user_id, username, score, money)
            
            embed = discord.Embed(
                title='Cookie Clicker v1',
                description=f'You have clicked **{score}** times!\n\nYou have accumulated **${money}**.',
                colour=discord.Colour.blue()
            )

            if score >= 100:

                embed = discord.Embed(
                    title='Cookie Clicker v1',
                    description=f'🍪 You have clicked **{score}** times!\n\nYou have accumulated **${money}**.\n\ntest',
                    colour=discord.Colour.blue()
                )
            
            await interaction.response.edit_message(embed=embed)

# cmd    
class play(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("play.py is active!")

    @app_commands.command(name="play", description="Create a button and start clicking!")
    async def play(self, interaction: discord.Interaction):
        view = CCButton(interaction.user.id)
        embed = discord.Embed(
            title = "Click the 🍪 below to begin playing!",
            colour = discord.Colour.blue()
        )
        await interaction.response.send_message(embed=embed, view=view)

async def setup(client: commands.Bot):
    await client.add_cog(play(client), guilds=client.guilds)