import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import uuid

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER
    )
''')
conn.commit()

conn2 = sqlite3.connect('CCButtonUsers.db')
cursor2 = conn2.cursor()

cursor2.execute('''
    CREATE TABLE IF NOT EXISTS CCButtonUsers (
        user_id INTEGER,
        button_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                   
    )
''')
conn2.commit()

# add/update user data
def add_or_update_user(user_id, username, score):
    cursor.execute('''
        INSERT INTO users (user_id, username, score)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) 
        DO UPDATE SET username = excluded.username, score = excluded.score
    ''', (user_id, username, score))
    conn.commit()

def add_cc_user(user_id, button_id):
    cursor2.execute('''
        INSERT INTO CCButtonUsers (user_id, button_id)
        VALUES (?, ?)

    ''', (user_id, button_id))
    conn2.commit()

# pull user data
def get_user_stats(user_id):
    cursor.execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        score = result[0]
        return score
    return None

def get_cc_user(button_id):
    cursor2.execute('SELECT user_id FROM CCButtonUsers WHERE button_id = ?', (button_id,))
    result = cursor2.fetchone()
    return result[0] if result else None

# button
class CCButton(discord.ui.View):
    def __init__(self, button_id):
        super().__init__(timeout=None)
        self.button_id = button_id
        self.value = None
        
    @discord.ui.button(label="🍪", style=discord.ButtonStyle.blurple, custom_id='persistent_view:CC')
    async def menu1(self, interaction: discord.Interaction,  button: discord.ui.Button):

        owner_id = get_cc_user(self.button_id)

        if interaction.user.id == owner_id:
            user_id = interaction.user.id
            username = str(interaction.user)

            stats = get_user_stats(user_id)
            
            if stats:
                score = stats
            else:
                score = 0
            
            score += 1

            add_or_update_user(user_id, username, score)
            
            embed = discord.Embed(
                title='Cookie Clicker v1',
                description=f'You have clicked **{score}** times!',
                colour=discord.Colour.blue()
            )
            
            await interaction.response.edit_message(embed=embed)

        else:

            embed = discord.Embed(
                title='<:error:1285808346573836289> Sorry! This is someone\'s button!',
                colour=discord.Colour.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

    

# cmd    
class play(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("play.py is active!")

    @app_commands.command(name="play", description="Create a button and start clicking!")
    async def play(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        button_id = str(uuid.uuid4())
        add_cc_user(user_id, button_id)
        
        view = CCButton(button_id)
        embed = discord.Embed(
            title = "Click the 🍪 below to begin playing!",
            colour = discord.Colour.blue()
        )
        await interaction.response.send_message(embed=embed, view=view)

async def setup(client: commands.Bot):
    await client.add_cog(play(client), guilds=client.guilds)
 