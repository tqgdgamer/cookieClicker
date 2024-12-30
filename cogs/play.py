import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import uuid
import random

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

conn2 = sqlite3.connect('CCButtonUsers.db')
cursor2 = conn2.cursor()

# add/update user data
def add_or_update_user(user_id, username, score):
    try:
        cursor.execute('''
            INSERT INTO users (user_id, username, score)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) 
            DO UPDATE SET username = excluded.username, score = excluded.score
        ''', (user_id, username, score))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def add_cc_user(user_id, button_id):
    try:
        cursor2.execute('''
            INSERT INTO CCButtonUsers (user_id, button_id)
            VALUES (?, ?)
        ''', (user_id, button_id))
        conn2.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# pull user data
def get_user_stats(user_id):
    try:
        cursor.execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            score = result[0]
            return score
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def get_cc_user(button_id):
    try:
        cursor2.execute('SELECT user_id FROM CCButtonUsers WHERE button_id = ?', (button_id,))
        result = cursor2.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

# button
class CCButton(discord.ui.View):
    def __init__(self, button_id):
        super().__init__(timeout=None)
        self.button_id = button_id
        self.value = None
        
    @discord.ui.button(label="🍪", style=discord.ButtonStyle.blurple, custom_id='persistent_view:CC')
    async def menu1(self, interaction: discord.Interaction,  button: discord.ui.Button):

        owner_id = get_cc_user(self.button_id)

        bonus = random.randint(1, 1000000)

        if interaction.user.id == owner_id:
            user_id = interaction.user.id
            username = str(interaction.user)

            stats = get_user_stats(user_id)
            
            if stats:
                score = stats
            else:
                score = 0
            
            cursor.execute('SELECT item_id FROM user_items WHERE user_id = ? AND purchased = 1', (user_id,))
            items = cursor.fetchall()

            multiplier = 1
            value = 1
            for item in items:
                item_id = item[0]
                if item_id == 3:
                    multiplier = 4
                elif item_id == 2:
                    multiplier = 3
                elif item_id == 1:
                    multiplier = 2

                if item_id == 6:
                    value = 10
                elif item_id == 5:
                    value = 5
                elif item_id == 4:
                    value = 2

            score += value * multiplier

            add_or_update_user(user_id, username, score)
            
            embed = discord.Embed(
                title='Cookie Clicker v1.3',
                description=f'You have accumulated **{score}** cookies!',
                colour=discord.Colour.blue()
            )
            
            await interaction.response.edit_message(embed=embed)

            if bonus <= 1000:
                bonus_score = random.randint(101, 1000)
                score += bonus_score

                add_or_update_user(user_id, username, score)

                bonus_embed = discord.Embed(
                    title="Bonus!",
                    description=f"\n\n<:alert:1287522413935853721> Rarity: **Rare** | 0.1% Chance\n\nYou earned an additional **{bonus_score}** cookies!",
                    colour=discord.Colour.yellow()
                )

                await interaction.followup.send(embed=bonus_embed, ephemeral=True)

            elif bonus <= 10000:
                bonus_score = random.randint(11, 100)
                score += bonus_score

                add_or_update_user(user_id, username, score)

                bonus_embed = discord.Embed(
                    title="Bonus!",
                    description=f"\n\n<:alert:1287522413935853721> Rarity: **Uncommon** | 1% Chance\n\nYou earned an additional **{bonus_score}** cookies!",
                    colour=discord.Colour.yellow()
                )

                await interaction.followup.send(embed=bonus_embed, ephemeral=True)

            elif bonus <= 100000:
                bonus_score = random.randint(2, 10)
                score += bonus_score

                add_or_update_user(user_id, username, score)

                bonus_embed = discord.Embed(
                    title="Bonus!",
                    description=f"\n\n<:alert:1287522413935853721> Rarity: **Common** | 10% Chance\n\nYou earned an additional **{bonus_score}** cookies!",
                    colour=discord.Colour.yellow()
                )

                await interaction.followup.send(embed=bonus_embed, ephemeral=True)

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
 