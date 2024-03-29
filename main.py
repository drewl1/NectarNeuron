# main.py

import discord
import os
import json
import datetime
import asyncio
import re
import pymongo 

from datetime import datetime
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents,case_insensitive=True)
time = datetime.now()
dev = [401758281195978762]


mongourl = os.getenv("MONGO_URL")

try:
    mongoclient = pymongo.MongoClient(mongourl)

except pymongo.errors.ConfigurationError:
    print("An Invalid URI")

db = mongoclient.NectarNeuronData
guildcoll = db["guildData"]


def getTime():
  time = datetime.now(timezone.utc)
  formatted_time = time.strftime("%H:%M:%S")
  formatted_date = time.strftime("%m/%d/%Y")
  formatted_time = ":".join([str(int(x)).zfill(2) for x in formatted_time.split(":")])
  formatted_date = "/".join([str(int(x)).zfill(2) for x in formatted_date.split("/")])
  formatted_datetime = f"{formatted_time} UTC on {formatted_date}"
  return formatted_datetime

@client.event
async def on_ready():
    print("Loading cogs . . .")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"{filename} was loaded.")
            except Exception as e:
                print(e)
    print("Cogs loaded successfully.")
    print("Nectar Neuron is Running!")


@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    msg = '**Still on cooldown**, please try again in {:.2f}s'.format(error.retry_after)
    await ctx.send(msg)
  else:
    print(error)
    with open('logs/botErrorLog.txt', "a") as bel:
      bel.write(f"\n[ERROR]   [{time.hour}:{time.minute}:{time.second} UTC on {time.month}/{time.day}/{time.year}] {error}")

@client.command()
async def botpfp(ctx):
  bot_user = client.user
  avatar_url = bot_user.avatar.url if bot_user.avatar else bot_user.default_avatar.url
  embed = discord.Embed(title="Bot's Profile Picture")
  embed.set_image(url=avatar_url)
  await ctx.send(embed=embed)

@client.command()
async def viewlog(ctx):
    try:
        with open('logs/botErrorLog.txt', 'r') as file:
            lines = file.readlines()
            lines.reverse()
            embeds = []
            for index, log in enumerate(lines):
                match = re.search(r'\[(.*?)\]\s+\[(.*?)\]\s+(.*)', log)
                if match:
                    error_type = match.group(1)
                    timestamp = match.group(2)
                    error_message = match.group(3)
                    embed = discord.Embed(title=f"#{len(lines) - index} | [{error_type}]", description=error_message, color=discord.Color.blue())
                    embed.set_footer(text=f"Occurred at {timestamp}")
                else:
                    embed = discord.Embed(title=f"#{len(lines) - index} | [Unknown]", description=log, color=discord.Color.blue())
                embeds.append(embed)
            current_page = 0
            message = await ctx.send(embed=embeds[current_page])
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

            while True:
                try:
                    reaction, user = await client.wait_for("reaction_add", timeout=30.0, check=check)
                    if str(reaction.emoji) == "➡️" and current_page < len(embeds) - 1:
                        current_page += 1
                        await message.edit(embed=embeds[current_page])
                    elif str(reaction.emoji) == "⬅️" and current_page > 0:
                        current_page -= 1
                        await message.edit(embed=embeds[current_page])
                    await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.delete()
                    break

    except FileNotFoundError:
        await ctx.send("Log file not found.")


@client.command()
async def listservers(ctx):
    if ctx.author.id in dev:
        embed = discord.Embed(title="List of Servers", color=discord.Color.blue())
        for guild in client.guilds:
            embed.add_field(name=guild.name, value=f"ID: {guild.id}\nMembers: {guild.member_count}", inline=False)
        await ctx.send(embed=embed)
    else:
        msg = await ctx.send("Developer use only")
        await asyncio.sleep(10)
        await msg.delete()

# Run the bot
token = os.getenv("NN_BOT_TOKEN")
client.run(token)