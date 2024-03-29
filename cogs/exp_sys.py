import discord
from discord.ext import commands
import pymongo
from bson import ObjectId
import datetime
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
mongourl = os.getenv("MONGO_URL")

class MongoDBCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Connect to MongoDB
        self.client = pymongo.MongoClient(mongourl)

        self.db = self.client.NectarNeuronData
        self.collection = self.db["userdata"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.TextChannel):
            if len(message.content) > 15:
                user_id = str(message.author.id)
                user_data = self.collection.find_one({"user_id": user_id})
                if user_data:
                    exp = user_data.get("exp", 0)
                    needed_exp = user_data.get("neededExp", 100)
                    level = user_data.get("level", 1)
                    new_exp = exp + 10
                    if new_exp >= needed_exp:
                        level += 1
                        new_needed_exp = 100 * (level ** 2) if level != 1 else 200

                        embed = discord.Embed(title="🎉 LEVEL UP", url="https://example.com",description=f'{message.author.mention} has reached level {level}!\nThats {new_exp} exp!',colour=0xfbff00, timestamp=datetime.now())
                        embed.set_footer(text="Nectar Neuron")
                        await message.channel.send(embed=embed)

                        self.collection.update_one(
                            {"user_id": user_id},
                            {"$set": {"exp": new_exp, "level": level, "neededExp": new_needed_exp}}
                        )
                    else:
                        self.collection.update_one(
                            {"user_id": user_id},
                            {"$set": {"exp": new_exp}}
                        )
                else:
                    new_user_data = {
                        "user_id": user_id,
                        "username": str(message.author),
                        "level": 1,
                        "exp": 10,
                        "neededExp": 100
                    }
                    self.collection.insert_one(new_user_data)


    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        leaderboard_data = self.collection.find().sort("exp", pymongo.DESCENDING).limit(10)
        embed = discord.Embed(title="Leaderboard", color=0xffd700, timestamp=datetime.now())
        for idx, user in enumerate(leaderboard_data, start=1):
            user_id = user["user_id"]
            exp = user.get("exp", 0)
            level = user.get("level", 1)
            username = user.get("username", "Unknown User")
            embed.add_field(name=f"{idx}. {username} - lvl{level}", value=f"{exp} EXP", inline=False)
        embed.set_footer(text="Nectar Neuron")
        await ctx.send(embed=embed)



    @commands.command()
    async def level(self, ctx, *, username: str = None):
        if username is None:
            user_id = str(ctx.author.id)
            user_data = self.collection.find_one({"user_id": user_id})
            username = ctx.author.display_name
        else:
            user_data = self.collection.find_one({"username": username})

        if user_data:
            exp = user_data.get("exp", 0)
            level = user_data.get("level", 1)
            needed_exp = user_data.get("neededExp", 100)
            messages_needed = max(0, needed_exp - exp) / 10
            member = ctx.guild.get_member(int(user_data["user_id"]))
            thumbnail_url = member.avatar.url if member and member.avatar else None
            embed = discord.Embed(title=username, description=f"**Level:** {level}\n**Experience:** {exp}\n**Messages to Level Up:** {str(messages_needed)[:-2].strip()}", color=0x98c379, timestamp=datetime.now())
            if thumbnail_url:
                embed.set_thumbnail(url=thumbnail_url)
            embed.set_footer(text="Nectar Neuron")
            await ctx.send(embed=embed)
        else:
            await ctx.send("User not found in the database.")




        
async def setup(bot):
    await bot.add_cog(MongoDBCog(bot))