import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from datetime import datetime, timedelta

import sqlite3

import cogs.play as cc
import cogs.leaderboard as lb

load_dotenv()

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

def retrieve_button_ids():
    cursor2.execute('SELECT button_id FROM CCButtonUsers')
    result = cursor2.fetchall()
    return [row[0] for row in result]

def purge_old_buttons():
    two_weeks = (datetime.now() - timedelta(weeks=2)).strftime('%Y-%m-%d %H:%M:%S')

    cursor2.execute('''
        DELETE FROM CCButtonUsers WHERE created_at < ?
    ''', (two_weeks,))

    conn2.commit()

    print(f"Purged buttons older than {two_weeks}")


class cookieClicker(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix = 'cc.',
            intents = discord.Intents.all(),
            application_id = 1285399074056573020)
        
        self.initial_extensions = [
            "cogs.ping",
            "cogs.play",
            "cogs.leaderboard"
        ]     

    async def setup_hook(self):
        self.purge_task.start()

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await client.load_extension(f"cogs.{filename[:-3]}")

                    button_ids = retrieve_button_ids()
                    for button_id in button_ids:                
                        client.add_view(cc.CCButton(button_id))

                    client.add_view(lb.leaderboardButton())

                    print(f"Loaded {filename}")
                except Exception as e:
                    print(f"Unable to load {filename}")
                    print(f"[ERROR] {e}")        


    async def close(self):
        await super().close()
        await self.session.close()

    @tasks.loop(hours=24)
    async def purge_task(self):
        print("Running daily button purge task...")
        purge_old_buttons()

    @purge_task.before_loop
    async def before_purge_task(self):
        print("Waiting for bot to come online before button purge...")
        await self.wait_until_ready()

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
