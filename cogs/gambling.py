import discord
from discord.ext import commands
from discord import app_commands, ui
import sqlite3
import requests
import asyncio

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

EMOJI_ROW_ID = 9001
RESULT_TEXT_ID = 9002
FOOTER_ID = 9003

class Gambling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Gambling.py is active!")

    @app_commands.command(name="slots", description="Play the slot machine.")
    @app_commands.describe(bet="Amount of cookies to bet. Must be an integer greater than or equal to 10")
    async def slots(self, interaction: discord.Interaction, bet: int):

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

        c1 = int(requests.get("https://www.random.org/integers/?num=1&min=0&max=6&col=1&base=10&format=plain").text)
        c2 = int(requests.get("https://www.random.org/integers/?num=1&min=0&max=6&col=1&base=10&format=plain").text)
        c3 = int(requests.get("https://www.random.org/integers/?num=1&min=0&max=6&col=1&base=10&format=plain").text)
        winner = (c1 == c2 == c3)

        class SlotsLayout(ui.LayoutView):
            def __init__(self):
                super().__init__(timeout=None)

                self.header = ui.Section(
                    ui.TextDisplay("**Slots**"),
                    accessory=ui.Thumbnail("attachment://777.png")
                )

                self.emoji_row = ui.TextDisplay(f"# {spin1} {spin2} {spin3}")

                self.result_text = ui.TextDisplay("*Spinning...*\n\u200b")

                self.container = ui.Container(accent_color=0xFFCC32)
                self.container.add_item(self.header)
                self.container.add_item(self.emoji_row)
                self.container.add_item(ui.Separator())
                self.container.add_item(self.result_text)

                self.add_item(self.container)

        layout = SlotsLayout()

        await interaction.response.send_message(view=layout, files=[file])

        await asyncio.sleep(2)
        layout.emoji_row.content = f"# {emojis[c1]} {spin2} {spin3}"
        await interaction.edit_original_response(view=layout)

        await asyncio.sleep(2)
        layout.emoji_row.content = f"# {emojis[c1]} {emojis[c2]} {spin3}"
        await interaction.edit_original_response(view=layout)

        await asyncio.sleep(2)
        layout.emoji_row.content = f"# {emojis[c1]} {emojis[c2]} {emojis[c3]}"
        layout.result_text.content = (
            f"**Result:** {'You won! 🎉' if winner else 'You lost! Better luck next time.'}\n"
            f"**Bet:** {bet}\n"
            f"**{'Winnings' if winner else 'Lost'}:** {'25x Prize: ' if winner else ''} {bet * 25 if winner else bet} cookies"
        )
        await interaction.edit_original_response(view=layout)


async def setup(client: commands.Bot):
    await client.add_cog(Gambling(client), guilds=client.guilds)