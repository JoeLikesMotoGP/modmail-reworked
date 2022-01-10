import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

token = 'Your Token Here'
bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

db = sqlite3.connect('modmail.db')
cursor = db.cursor()

# Remove after running once

cursor.execute("""
    CREATE TABLE modmail (
        user_id int,
        channel_id int
     )
""")



def check(key):
    if key is None:
        return False
    else:
        return True

@bot.event
async def on_ready():
    print("Modmail Online")

@bot.event
async def on_message(ctx):
    guild = bot.get_guild(907412013309894706)
    category = bot.get_channel(916765823950012527)
    admin_role = discord.utils.get(guild.roles, name="Staff")

    if ctx.author == bot.user:
        return
    
    if not ctx.guild:
        cursor.execute("SELECT user_id FROM modmail WHERE user_id = (?)", (ctx.author.id, ))
        if check(cursor.fetchone()) is True:
            try:
                print("RETURNING USER")
                cursor.execute("SELECT channel_id FROM modmail WHERE user_id = (?)", (ctx.author.id, ))
                channel_id = cursor.fetchone()
                for id in channel_id:
                    channel_id = id
                    break
                channel = bot.get_channel(channel_id)
                if channel is None:
                    print("CHANNEL NOT FOUND")
                    overwrites = {
                        guild.default_role : discord.PermissionOverwrite(read_messages=False),
                        admin_role : discord.PermissionOverwrite(read_messages=True)
                    }
                    new_channel = await guild.create_text_channel(f"{ctx.author.name}-modmail", overwrites=overwrites, category=category)

                    cursor.execute("UPDATE modmail SET channel_id = (?) WHERE user_id = (?)", (new_channel.id, ctx.author.id, ))
                    db.commit()
                    channel = new_channel
                
                embed = discord.Embed(
                    title="Message From [{}]".format(ctx.author.name),
                    color = discord.colour.Color.purple(),
                    timestamp=datetime.now(),
                    description=ctx.content
                )
                embed.set_footer(
                text=f"Sent by {ctx.author} • {ctx.author.id}",
                icon_url = ctx.author.avatar.url
                )
                embed.set_author(
                name=ctx.author.name,
                icon_url = ctx.author.avatar.url
                )

                await channel.send(embed=embed)
                await ctx.add_reaction(emoji='✅')

            except Exception as e:
                print(e)
                await ctx.add_reaction(emoji='❌')
                
        else:
            try:
                print("NEW USER")
                overwrites = {
                    guild.default_role : discord.PermissionOverwrite(read_messages=False),
                    admin_role : discord.PermissionOverwrite(read_messages=True)
                }

                modmail_channel = await guild.create_text_channel(f"{ctx.author.name}-modmail", overwrites=overwrites, category=category)

                cursor.execute("INSERT INTO modmail VALUES (?, ?)", (ctx.author.id, modmail_channel.id, ))
                db.commit()

                embed = discord.Embed(
                    title="New Modmail Ticket",
                    color = discord.colour.Color.brand_green(),
                    timestamp=datetime.now(),
                    description=ctx.content
                )
                embed.set_footer(icon_url=ctx.author.avatar.url, text='\
                    Sent by {}'.format(ctx.author.name))
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
                await modmail_channel.send(embed=embed)
                await ctx.add_reaction(emoji='✅')
            except Exception as e:
                print(e)
                await ctx.add_reaction(emoji='❌')

    else:
        if ctx.channel.category == category:
            cursor.execute("SELECT channel_id FROM modmail WHERE user_id = (?)", (ctx.author.id, ))
            if check(cursor.fetchone()) is True:
                try:
                    cursor.execute("SELECT user_id FROM modmail WHERE channel_id = (?)", (ctx.channel.id, ))
                    user_id = cursor.fetchone()

                    for id in user_id:
                        user_id = id
                        break
                
                    user = discord.utils.get(guild.members, id=user_id)
                    if user is None:
                        await ctx.reply("I can't find that user ⚠")
                        await ctx.add_reaction(emoji='❌')
                        return
                    else:
                        if ctx.content == '!close':
                            close_embed = discord.Embed(
                                title="Ticket is Closed",
                                timestamp=datetime.now(),
                                color = discord.colour.Color.nitro_pink(),
                                description=f"This ticket **is now closed** {ctx.author.mention}\nThis ticket is now closed and no longer being managed by the staff team, if you need anything else please feel free to shoot us another message and we'll get back to you as soon as we can. Thank you for participating in {ctx.guild.name}!\n\nClosed by **{ctx.author}**"
                            )
                            close_embed.set_footer(text="By replying, you are opening another ticket")
                            await user.send(embed=close_embed)
                            channel = ctx.channel
                            await channel.delete()
                            cursor.execute("DELETE FROM modmail WHERE channel_id = (?)", (channel.id, ))
                            db.commit()
                            return
                        else:
                            embed = discord.Embed(
                                title="Message From {}".format(ctx.guild.name),
                                color = discord.colour.Color.og_blurple(),
                                timestamp=datetime.now(),
                                description=ctx.content
                            )
                            embed.set_footer(
                            text=f"Sent by {ctx.author} • {ctx.author.id}",
                            icon_url = ctx.author.avatar.url
                            )

                            embed.set_author(
                            name=ctx.author.name,
                            icon_url = ctx.author.avatar.url
                            )
                            await user.send(embed=embed)
                        await ctx.add_reaction(emoji='✅')
                except Exception as e:
                    print(e)
                    await ctx.add_reaction(emoji='❌')


bot.run(token)
