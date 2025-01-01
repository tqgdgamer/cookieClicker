import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT user_id, username, score FROM users ORDER BY score DESC LIMIT 10
''')
result = cursor.fetchall()

errorEmbed = discord.Embed(
    title='Error',
    description='<:error:1285808346573836289> You can not click on the button!',
    colour=discord.Colour.red()
    )

pages = [
    discord.Embed(
        title='<:top:1287522473411088476> Cookie Leaderboard (#1-10)',
        description='Use the buttons below to switch pages',
        colour=discord.Colour.from_str("#946fff")
        ),
    discord.Embed(
        title='<:top:1287522473411088476> Cookie Leaderboard (#11-20)',
        description='Use the buttons below to switch pages',
        colour=discord.Colour.from_str("#946fff")
        ),
    discord.Embed(
        title='<:top:1287522473411088476> Cookie Leaderboard (#21-30)',
        description='Use the buttons below to switch pages',
        colour=discord.Colour.from_str("#946fff")
        ),
]

for i, (user_id, username, score) in enumerate(result, start=1):
    if i <= 10:
        pages[0].add_field(name=f'#{i}', value=f'<@{user_id}> | {username} | Cookies: **{score}**', inline=False)
    elif i <= 20 and i > 10:
        pages[1].add_field(name=f'#{i}', value=f'<@{user_id}> | {username} | Cookies: **{score}**', inline=False)
    elif i <= 30 and i > 20:
        pages[2].add_field(name=f'#{i}', value=f'<@{user_id}> | {username} | Cookies: **{score}**', inline=False)

def fetch_leaderboard():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT user_id, username, score FROM users ORDER BY score DESC LIMIT 100
    ''')
    result = cursor.fetchall()

    return result

class leaderboardButton(discord.ui.View):
    def __init__(self, embeds = pages):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.current_page = 0
        
    @discord.ui.button(label="⏪", style=discord.ButtonStyle.blurple, custom_id='persistent_view:FirstPage')
    async def firstpage(self, interaction: discord.Interaction,  button: discord.ui.Button, disabled=True):
        if self.current_page > 0 :
            self.current_page = 0
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.send_message(embed=errorEmbed, ephemeral=True) 
        
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.blurple, custom_id='persistent_view:PreviousPage')
    async def previouspage(self, interaction: discord.Interaction,  button: discord.ui.Button, disabled=True):
        if self.current_page > 0 :
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self) 
        else:
            await interaction.response.send_message(embed=errorEmbed, ephemeral=True)      
        
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.blurple, custom_id='persistent_view:NextPage')
    async def nextpage(self, interaction: discord.Interaction,  button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1 :
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.send_message(embed=errorEmbed, ephemeral=True)       

    @discord.ui.button(label="⏩", style=discord.ButtonStyle.blurple, custom_id='persistent_view:LastPage')
    async def lastpage(self, interaction: discord.Interaction,  button: discord.ui.Button):      
        if self.current_page < len(self.embeds) - 1 :
            self.current_page = len(self.embeds) - 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.send_message(embed=errorEmbed, ephemeral=True)      

class leaderboard(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.leaderboard_data = []
        self.leaderboard_message = None
        self.update_leaderboard.start()

    @tasks.loop(minutes=10)
    async def update_leaderboard(self):
        try:
            self.leaderboard_data = fetch_leaderboard()

            if self.leaderboard_message:
                await self.update_leaderboard_message()
                print("Updated leaderboard.")
                
            else:
                print("Leaderboard message not found.")
        except Exception as e:
            print(f"Error updating leaderboard: {e}")

    async def update_leaderboard_message(self):
        try:
            if self.leaderboard_message is None:
                print("No leaderboard message exists.")
                return
            
            result = fetch_leaderboard()
            
            for embed in pages:
                embed.clear_fields()

            for i, (user_id, username, score) in enumerate(result, start=1):
                if i <= 10:
                    pages[0].add_field(name=f'#{i}', value=f'<@{user_id}> | {username} | Cookies: **{score}**', inline=False)
                elif i <= 20:
                    pages[1].add_field(name=f'#{i}', value=f'<@{user_id}> | {username} | Cookies: **{score}**', inline=False)
                elif i <= 30:
                    pages[2].add_field(name=f'#{i}', value=f'<@{user_id}> | {username} | Cookies: **{score}**', inline=False)

            await self.leaderboard_message.edit(embed=pages[0])

        except Exception as e:
            print(f"Error updating leaderboard message: {e}")

    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        print("Waiting for bot to come online before leaderboard update...")
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print("leaderboard.py is active!")

    @app_commands.command(name = "leaderboard", description="Fetch the leaderboard for the top 100 cookie clickers")
    async def leaderboard(self, interaction: discord.Interaction):
    
        view = leaderboardButton(embeds=pages)
    
        await interaction.response.send_message(embed=pages[0],view=view)
        self.leaderboard_message = await interaction.original_response()
        await self.update_leaderboard_message()

async def setup(client: commands.Bot):
    await client.add_cog(leaderboard(client), guilds=client.guilds)
