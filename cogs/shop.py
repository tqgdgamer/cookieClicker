import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

client = commands.Bot(command_prefix="cc.", intents=discord.Intents.all())

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS shop (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')
conn.commit()

# Create user_items table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_items (
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    purchased INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, item_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES shop(id)
)
''')
conn.commit()

# Define the items and their prices
items = [
    {"name": "Better Flour", "description": "Doubles your cookies.", "price": 1000},
    {"name": "Better Sugar", "description": "Triples your cookies.", "price": 5000},
    {"name": "Pasture Raised Eggs", "description": "Quadruple the cookies. Quadruple the addiction.", "price": 25000},
    {"name": "Organic Butter", "description": "Get two cookies per click!", "price": 100},
    {"name": "Chocolate Chips", "description": "Get five cookies per click!", "price": 2500},
    {"name": "Macadamia Nuts", "description": "Get ten cookies per click!", "price": 10000},
    {"name": "Chance Formula", "description": "Unlock Super Bonus!", "price": 100000}
]

# Insert items into the shop table if they don't already exist
for item in items:
    cursor.execute("INSERT OR IGNORE INTO shop (user_id, name, description, price) VALUES (?, ?, ?, ?)",
                   (0, item["name"], item["description"], item["price"]))
conn.commit()

class ShopView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        options = [
            discord.SelectOption(label=f"{item['name']} | {item['price']} Cookies", description=item['description'], value=str(item_id))
            for item_id, item in enumerate(items, start=1)
        ]
        select = discord.ui.Select(
            placeholder="Select an item to buy...",
            min_values=1,
            max_values=1,
            options=options
        )
        select.callback = self.select_callback_handler
        self.add_item(select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                title = "Permission Error",
                description = f"<:error:1285808346573836289> You cannot interact with this menu.",
                colour = discord.Colour.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            return False
        return True

    async def select_callback_handler(self, interaction: discord.Interaction):
        if 'values' in interaction.data and interaction.data['values']:
            item_id = int(interaction.data['values'][0])
        else:
            await interaction.response.send_message("Invalid selection", ephemeral=True)
            return

        cursor.execute("SELECT name, price FROM shop WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if item:
            name, price = item
            # Check if the item is already purchased
            cursor.execute("SELECT purchased FROM user_items WHERE user_id = ? AND item_id = ?", (self.user_id, item_id))
            purchased = cursor.fetchone()
            if purchased and purchased[0] == 1:
                embed = discord.Embed(
                    title = "Purchase Error",
                    description = f"<:error:1285808346573836289> You have already purchased this item.",
                    colour = discord.Colour.red()
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Check if the user has enough cookies
            cursor.execute("SELECT score FROM users WHERE user_id = ?", (self.user_id,))
            cookies = cursor.fetchone()[0]
            if cookies >= price:
                cursor.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (price, self.user_id))
                cursor.execute("INSERT INTO user_items (user_id, item_id, purchased) VALUES (?, ?, ?) ON CONFLICT(user_id, item_id) DO UPDATE SET purchased=1", (self.user_id, item_id, 1))
                conn.commit()

                cursor.execute("SELECT score FROM users WHERE user_id = ?", (self.user_id,))
                score = cursor.fetchone()[0]

                embed = discord.Embed(
                    title = "Purchase Successful",
                    description = f"<:checkmark:1287522486845575261> You have bought **{name}** for **{price}** cookies!\nYou now have **{score}** cookies.",
                    colour = discord.Colour.green()
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title = "Purchase Error",
                    description = f"<:error:1285808346573836289> You can't afford this!",
                    colour = discord.Colour.red()
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title = "Purchase Error",
                description = f"<:error:1285808346573836289> Item not found.",
                colour = discord.Colour.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)            

class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("shop.py is active!")

    @app_commands.command(name = "shop", description="Looking for ways to increase your cookie count? Check out the shop!")
    async def shop(self, interaction: discord.Interaction):

        user_id = interaction.user.id
        view = ShopView(user_id)

        embed = discord.Embed(
            title = "Shop",
            description = f"<:shop:1310461840433872937> Welcome to the shop! The best place for you to up your cookie count.",
            colour = discord.Colour.green()
        )

        await interaction.response.send_message(embed=embed, view=view)

async def setup(client: commands.Bot):
    await client.add_cog(Shop(client), guilds=client.guilds)

