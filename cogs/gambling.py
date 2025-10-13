import discord
from discord.ext import commands
from discord import app_commands, ui
import sqlite3
import requests
import asyncio

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()


# sql stuff
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

EMOJI_ROW_ID = 9001
RESULT_TEXT_ID = 9002
FOOTER_ID = 9003

# gambling cog
class Gambling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Gambling.py is active!")


    # slot machine
    @app_commands.command(name="slots", description="Play the slot machine.")
    @app_commands.describe(bet="Amount of cookies to bet. Must be an integer greater than or equal to 10")
    @app_commands.choices(
        difficulty=[
            app_commands.Choice(name="Normal", value="3 slots"),
            app_commands.Choice(name="Hard", value="5 slots"),
        ]
    )
    async def slots(self, interaction: discord.Interaction, bet: int, difficulty: app_commands.Choice[str]):

        user_id = interaction.user.id
        username = interaction.user.name

        score = get_user_stats(user_id)

        if score < bet:
            errorEmbed = discord.Embed(
                title='Error',
                description='<:error:1285808346573836289> You do not have enough cookies to make that bet.',
                colour=discord.Colour.red()
            )
            await interaction.response.send_message(embed=errorEmbed, ephemeral=True)
            return
        
        elif not score:
            pass
        
        else:

            if bet < 10:
                errorEmbed = discord.Embed(
                    title='Error',
                    description='<:error:1285808346573836289> The minimum bet is 10 cookies.',
                    colour=discord.Colour.red()
                )
                await interaction.response.send_message(embed=errorEmbed, ephemeral=True)
                return
            
            if bet > 100000000:
                errorEmbed = discord.Embed(
                    title='Error',
                    description='<:error:1285808346573836289> The maximum bet is 100,000,000 cookies.',
                    colour=discord.Colour.red()
                )
                await interaction.response.send_message(embed=errorEmbed, ephemeral=True)
                return
            
            # --- assets ---
            file = discord.File("images/777.png", filename="777.png")

            emojis = [
                "<:1_:1427051665525309512>",
                "<:2_:1427051676212265083>",
                "<:3_:1427051686840635493>",
                "<:4_:1427051698152542329>",
                "<:5_:1427051707526811709>",
                "<:6_:1427051718150983751>",
                "<:7_:1427051730960515212>",
            ]
            spin1 = "<a:slots_1:1427051856869195837>"
            spin2 = "<a:slots_2:1427054015639978015>"
            spin3 = "<a:slots_3:1427054047831265321>"

            spin4 = "<a:slots_1:1427051856869195837>"
            spin5 = "<a:slots_2:1427054015639978015>"

            c1 = int(requests.get("https://www.random.org/integers/?num=1&min=0&max=6&col=1&base=10&format=plain").text)
            c2 = int(requests.get("https://www.random.org/integers/?num=1&min=0&max=6&col=1&base=10&format=plain").text)
            c3 = int(requests.get("https://www.random.org/integers/?num=1&min=0&max=6&col=1&base=10&format=plain").text)

            c4 = int(requests.get("https://www.random.org/integers/?num=1&min=0&max=6&col=1&base=10&format=plain").text)
            c5 = int(requests.get("https://www.random.org/integers/?num=1&min=0&max=6&col=1&base=10&format=plain").text)
            
            winner = (c1 == c2 == c3)

            hard_winner = (c1 == c2 == c3 == c4 == c5)

            class SlotsLayout(ui.LayoutView):
                def __init__(self):
                    super().__init__(timeout=None)

                    if difficulty.value == "3 slots":
                        self.header = ui.Section(
                            ui.TextDisplay("**Slot Machine (Normal)**"),
                            accessory=ui.Thumbnail("attachment://777.png")
                        )
                        self.emoji_row = ui.TextDisplay(f"# {spin1} {spin2} {spin3}")
                    if difficulty.value == "5 slots":
                        self.header = ui.Section(
                            ui.TextDisplay("**Slot Machine (Hard)**"),
                            accessory=ui.Thumbnail("attachment://777.png")
                        )
                        self.emoji_row = ui.TextDisplay(f"# {spin1} {spin2} {spin3} {spin4} {spin5}")

                    self.result_text = ui.TextDisplay("*Spinning...*\n\u200b")

                    self.container = ui.Container(accent_color=0xFFCC32)
                    self.container.add_item(self.header)
                    self.container.add_item(self.emoji_row)
                    self.container.add_item(ui.Separator())
                    self.container.add_item(self.result_text)

                    self.add_item(self.container)

            layout = SlotsLayout()

            await interaction.response.send_message(view=layout, files=[file])

            if difficulty.value == "3 slots":
                await asyncio.sleep(2)
                layout.emoji_row.content = f"# {emojis[c1]} {spin2} {spin3}"
                await interaction.edit_original_response(view=layout)

                await asyncio.sleep(2)
                layout.emoji_row.content = f"# {emojis[c1]} {emojis[c2]} {spin3}"
                await interaction.edit_original_response(view=layout)

                await asyncio.sleep(2)
                layout.emoji_row.content = f"# {emojis[c1]} {emojis[c2]} {emojis[c3]}"
                layout.result_text.content = (
                    f"**Result:** {'You won! <:alert:1287522413935853721>' if winner else 'You lost! Better luck next time.'}\n"
                    f"**Bet:** {bet}\n"
                    f"**{'Winnings' if winner else 'Lost'}:** {'25x Prize - ' if winner else ''}**{bet * 25 if winner else bet}** cookies"
                )

                if winner:
                    score += bet * 25
                    add_or_update_user(user_id, username, score)

                else:
                    score -= bet
                    add_or_update_user(user_id, username, score)

                await interaction.edit_original_response(view=layout)

            if difficulty.value == "5 slots":
                await asyncio.sleep(1)
                layout.emoji_row.content = f"# {emojis[c1]} {spin2} {spin3} {spin4} {spin5}"
                await interaction.edit_original_response(view=layout)

                await asyncio.sleep(1)
                layout.emoji_row.content = f"# {emojis[c1]} {emojis[c2]} {spin3} {spin4} {spin5}"
                await interaction.edit_original_response(view=layout)

                await asyncio.sleep(1)
                layout.emoji_row.content = f"# {emojis[c1]} {emojis[c2]} {emojis[c3]} {spin4} {spin5}"
                await interaction.edit_original_response(view=layout)

                await asyncio.sleep(1)
                layout.emoji_row.content = f"# {emojis[c1]} {emojis[c2]} {emojis[c3]} {emojis[c4]} {spin5}"
                await interaction.edit_original_response(view=layout)

                await asyncio.sleep(1)
                layout.emoji_row.content = f"# {emojis[c1]} {emojis[c2]} {emojis[c3]} {emojis[c4]} {emojis[c5]}"
                layout.result_text.content = (
                    f"**Result:** {'You won! <:alert:1287522413935853721>' if winner else 'You lost! Better luck next time.'}\n"
                    f"**Bet:** {bet}\n"
                    f"**{'Winnings' if winner else 'Lost'}:** {'250x Prize - ' if winner else ''}**{bet * 250 if winner else bet}** cookies"
                )

                if winner:
                    score += bet * 250
                    add_or_update_user(user_id, username, score)

                else:
                    score -= bet
                    add_or_update_user(user_id, username, score)

                await interaction.edit_original_response(view=layout)

    #


async def setup(client: commands.Bot):
    await client.add_cog(Gambling(client), guilds=client.guilds)