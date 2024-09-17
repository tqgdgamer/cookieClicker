import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import cogs.play as cc

load_dotenv()

class cookieClicker(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix = 'cc.',
            intents = discord.Intents.all(),
            application_id = 1285399074056573020)
        
        self.initial_extensions = [
            "cogs.play",
            "cogs.sell"
        ]
        

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await client.load_extension(f"cogs.{filename[:-3]}")
                    
                    client.add_view(cc.CCButton())

                    print(f"Loaded {filename}")
                except Exception as e:
                    print(f"Unable to load {filename}")
                    print(f"[ERROR] {e}")        


    async def close(self):
        await super().close()
        await self.session.close()
       

    async def on_ready(self):
        await client.change_presence(status=discord.Status.idle, activity=discord.Game('Baking cookies!'))
        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

        print("The bot is available for usage...")

client = cookieClicker()
client.remove_command("help")

TOKEN = os.getenv("DISCORD_TOKEN")

client.run(TOKEN)

