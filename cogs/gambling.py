import discord
from discord.ext import commands
from discord import app_commands, ui
import sqlite3
import requests
import asyncio
from math import trunc

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

user_locks = set()

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

        if user_id in user_locks:
            errorEmbed = discord.Embed(
                title='Error',
                description='<:error:1285808346573836289> You are already in a game! Please finish your current game before starting a new one.',
                colour=discord.Colour.red()
            )
            await interaction.response.send_message(embed=errorEmbed, ephemeral=True)
            return
        
        user_locks.add(user_id)

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
                user_locks.remove(user_id)

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
                user_locks.remove(user_id)

    # higher or lower

    @app_commands.command(name="hilo", description="Play higher or lower.")
    @app_commands.describe(bet="Amount of cookies to bet. Must be an integer greater than or equal to 10")
    async def hilo(self, interaction: discord.Interaction, bet: int):

        username = interaction.user.name
        user_id = interaction.user.id

        score = get_user_stats(user_id)

        if user_id in user_locks:
            errorEmbed = discord.Embed(
                title='Error',
                description='<:error:1285808346573836289> You are already in a game! Please finish your current game before starting a new one.',
                colour=discord.Colour.red()
            )
            await interaction.response.send_message(embed=errorEmbed, ephemeral=True)
            return
        
        user_locks.add(user_id)

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

        current_number = int(requests.get("https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain").text)
        new_number = int(requests.get("https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain").text)
        roundnum = 0
        winnings = bet

        embed = discord.Embed(
            title="Higher or Lower",
            description=f"Will the next number be higher than {current_number}?\n\n**Current Prize:**\n**{bet}** cookies",
            colour=discord.Colour.from_str("#ffcc32"),
        )

        embed.set_footer(text=f"Round {roundnum} ‧ Requested by {username}", icon_url=interaction.user.display_avatar.url)

        score -= bet
        add_or_update_user(user_id, username, score)



        class buttons(discord.ui.View):
            def __init__(self, button_id):
                super().__init__(timeout=None)
                self.button_id = button_id
                self.value = None
                
            @discord.ui.button(label="Higher", style=discord.ButtonStyle.green, custom_id='h')
            async def higher(self, interaction: discord.Interaction,  button: discord.ui.Button):

                owner_id = self.button_id

                if interaction.user.id == owner_id:
                    nonlocal new_number
                    nonlocal current_number
                    nonlocal roundnum
                    nonlocal bet
                    nonlocal winnings

                    roundnum += 1

                    if new_number > current_number:
                        if roundnum <= 5:
                            winnings = trunc(round(bet * (1.1**roundnum + 0.1*roundnum**2),0))

                        elif roundnum > 5:
                            winnings = trunc(round(bet*(1.1**5 + 0.1*5**2) * (1.05**(roundnum-5)),0))

                        current_number = new_number
                        new_number = int(requests.get("https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain").text)

                        embed = discord.Embed(
                            title="Higher or Lower",
                            description=f"Will the next number be higher than {current_number}?\n\n**Current Prize:**\n**{winnings}** cookies ‧ *Multiplier: {round((1.1**roundnum + 0.1*roundnum**2),2) if roundnum <= 5 else round((1.1**5 + 0.1*5**2) * (1.05**(roundnum-5)),2)}*",
                            colour=discord.Colour.from_str("#32cd32"),
                        )

                        embed.set_footer(text=f"Round {roundnum} ‧ Requested by {username}", icon_url=interaction.user.display_avatar.url)

                        await interaction.response.edit_message(embed=embed, view=self)

                    else:
                        embed = discord.Embed(
                            title="Higher or Lower",
                            description=f"You lost! The number was **{new_number}**.\n\n",
                            colour=discord.Colour.red(),
                        )

                        embed.set_footer(text=f"Round {roundnum} ‧ Requested by {username}", icon_url=interaction.user.display_avatar.url)

                        for item in self.children:
                            item.disabled = True

                        await interaction.response.edit_message(embed=embed, view=self)

                        user_locks.remove(user_id)

                else:
                    errorEmbed = discord.Embed(
                        title='Error',
                        description='<:error:1285808346573836289> You can not click on the button!',
                        colour=discord.Colour.red()
                    )
                    await interaction.response.send_message(embed=errorEmbed, ephemeral=True)
            @discord.ui.button(label="Lower", style=discord.ButtonStyle.red, custom_id='l')
            async def lower(self, interaction: discord.Interaction,  button: discord.ui.Button):

                owner_id = self.button_id

                if interaction.user.id == owner_id:
                    nonlocal new_number
                    nonlocal current_number
                    nonlocal roundnum
                    nonlocal bet
                    nonlocal winnings

                    roundnum += 1

                    if new_number < current_number:
                        if roundnum <= 5:
                            winnings = trunc(round(bet * round((1.1**roundnum + 0.1*roundnum**2), 2),0))

                        elif roundnum > 5:
                            winnings = trunc(round(bet*round((1.1**5 + 0.1*5**2) * (1.05**(roundnum-5)), 2),0))
                        current_number = new_number
                        new_number = int(requests.get("https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain").text)

                        embed = discord.Embed(
                            title="Higher or Lower",
                            description=f"Will the next number be higher than {current_number}?\n\n**Current Prize:**\n**{winnings}** cookies ‧ *Multiplier: {round((1.1**roundnum + 0.1*roundnum**2),2) if roundnum <= 5 else round((1.1**5 + 0.1*5**2) * (1.05**(roundnum-5)),2)}*",
                            colour=discord.Colour.from_str("#32cd32"),
                        )

                        embed.set_footer(text=f"Round {roundnum} ‧ Requested by {username}", icon_url=interaction.user.display_avatar.url)

                        await interaction.response.edit_message(embed=embed, view=self)

                    else:
                        embed = discord.Embed(
                            title="Higher or Lower",
                            description=f"You lost! The number was **{new_number}**.\n\n",
                            colour=discord.Colour.red(),
                        )

                        embed.set_footer(text=f"Round {roundnum} ‧ Requested by {username}", icon_url=interaction.user.display_avatar.url)

                        for item in self.children:
                            item.disabled = True

                        await interaction.response.edit_message(embed=embed, view=self)

                        user_locks.remove(user_id)

                else:
                    errorEmbed = discord.Embed(
                        title='Error',
                        description='<:error:1285808346573836289> You can not click on the button!',
                        colour=discord.Colour.red()
                    )
                    await interaction.response.send_message(embed=errorEmbed, ephemeral=True)
            @discord.ui.button(label="Redeem", style=discord.ButtonStyle.blurple, custom_id=':r')
            async def redeem(self, interaction: discord.Interaction,  button: discord.ui.Button):

                owner_id = self.button_id

                if interaction.user.id == owner_id:
                    nonlocal bet
                    nonlocal username
                    nonlocal roundnum
                    nonlocal winnings

                    embed = discord.Embed(
                        title="Higher or Lower",
                        description=f"<:alert:1287522413935853721> You have redeemed your winnings and leave with **{winnings}** cookies.",
                        colour=discord.Colour.gold(),
                    )

                    embed.set_footer(text=f"Round {roundnum} ‧ Requested by {username}", icon_url=interaction.user.display_avatar.url)

                    add_or_update_user(user_id, username, score + winnings)

                    for item in self.children:
                        item.disabled = True

                    await interaction.response.edit_message(embed=embed, view=self)

                    user_locks.remove(user_id)

                else:
                    errorEmbed = discord.Embed(
                        title='Error',
                        description='<:error:1285808346573836289> You can not click on the button!',
                        colour=discord.Colour.red()
                    )
                    await interaction.response.send_message(embed=errorEmbed, ephemeral=True)

        await interaction.response.send_message(embed=embed, view=buttons(interaction.user.id))



async def setup(client: commands.Bot):
    await client.add_cog(Gambling(client), guilds=client.guilds)