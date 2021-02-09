import discord
from discord.ext import commands
 
import sqlite3
from config import settings
from Cybernator import Paginator as pag
 
client = commands.Bot(command_prefix = settings['PREFIX'], intents = discord.Intents.all())
client.remove_command('help')
 
connection = sqlite3.connect('server.db')
cursor = connection.cursor()
#-----------------------------------------Economy-------------------------------------------------#
@client.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        cash BIGINT,
        rep INT,
        lvl INT,
        server_id INT
    )""")
 
    cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
        role_id INT,
        id INT,
        cost BIGINT
    )""")
 
    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, {guild.id})")
            else:
                pass

    connection.commit()
    print('client connected')
 
@client.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, {member.guild.id})")
        connection.commit()
    else:
        pass
 
@client.command(aliases = ['balance', 'cash'])
async def __balance(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed = discord.Embed(
            description = f"""Soldul utilizatorului **{ctx.author}** este **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} :leaves:**"""
        ))
        
    else:
        await ctx.send(embed = discord.Embed(
            description = f"""Soldul utilizatorului **{member}** este **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]} :leaves:**"""
        ))  
 
@client.command(aliases = ['award'])
async def __award(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, specificați utilizatorul căruia doriți să îi acordați o anumită sumă")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, specificați suma pe care doriți să o creditați în contul utilizatorului")
        elif amount < 1:
            await ctx.send(f"**{ctx.author}**, specificați suma mai mare de 1 :leaves:")
        else:
            cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')
 
@client.command(aliases = ['take'])
async def __take(ctx, member: discord.Member = None, amount = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, specificați utilizatorul de la care doriți să luați suma de bani")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, specificați suma pe care doriți să o retrageți din contul utilizatorului")
        elif amount == 'all':
            cursor.execute("UPDATE users SET cash = {} WHERE id = {}".format(0, member.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')
        elif int(amount) < 1:
            await ctx.send(f"**{ctx.author}**, specificați suma mai mare de 1 :leaves:")
        else:
            cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), member.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')
 
@client.command(aliases = ['add-shop'])
async def __add_shop(ctx, role: discord.Role = None, cost: int = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, specificați rolul pe care doriți să îl adăugați în magazin")
    else:
        if cost is None:
            await ctx.send(f"**{ctx.author}**, indicați costul pentru acest rol")
        elif cost < 0:
            await ctx.send(f"**{ctx.author}**, costul unui rol nu poate fi atât de mic")
        else:
            cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
            connection.commit()
 
            await ctx.message.add_reaction('✅')
 
@client.command(aliases = ['remove-shop'])
async def __remove_shop(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, indicați rolul pe care doriți să îl eliminați din magazin")
    else:
        cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
        connection.commit()
 
        await ctx.message.add_reaction('✅')
 
@client.command(aliases = ['shop'])
async def __shop(ctx):
    embed = discord.Embed(title = 'Magazin de roluri')
 
    for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
        if ctx.guild.get_role(row[0]) != None:
            embed.add_field(
                name = f"Costul **{row[1]} :leaves:**",
                value = f"Veți dobândi rolul {ctx.guild.get_role(row[0]).mention}",
                inline = False
            )
        else:
            pass
 
    await ctx.send(embed = embed)
 
@client.command(aliases = ['buy', 'buy-role'])
async def __buy(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, specificați rolul pe care doriți să-l dobândiți")
    else:
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author}**, ai deja un rol")
        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f"**{ctx.author}**, nu aveți suficiente fonduri pentru a cumpăra acest rol")
        else:
            await ctx.author.add_roles(role)
            cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')
 
@client.command(aliases = ['rep', '+rep'])
async def __rep(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, specificați membrul serverului")
    else:
        if member.id == ctx.author.id:
            await ctx.send(f"**{ctx.author}**, nu te poți indica pe tine însuți")
        else:
            cursor.execute("UPDATE users SET rep = rep + {} WHERE id = {}".format(1, member.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')
 
@client.command(aliases = ['leaderboard', 'lb'])
async def __leaderboard(ctx):
    embed = discord.Embed(title = 'Top 10 pe server')
    counter = 0
 
    for row in cursor.execute("SELECT name, cash FROM users WHERE server_id = {} ORDER BY cash DESC LIMIT 10".format(ctx.guild.id)):
        counter += 1
        embed.add_field(
            name = f'# {counter} | `{row[0]}`',
            value = f'Soldul: {row[1]}',
            inline = False
        )
 
    await ctx.send(embed = embed)

#-----------------------------------------------------------Commanda help---------------------------------------------------#

@client.command()
async def help(ctx):
	embed=discord.Embed(title="Comenizile Disponibile:", color=0x5e66d9)
	embed.add_field(name="Economice:", value="$balance/$award/$take/$rep/$shop/$add-shop/$remove-shop  $buy/$leaderboard", inline=True)
	await ctx.send(embed=embed)


#-----------------------------------------------------------Altele------------------------------------------------------------#





 
client.run(settings['TOKEN'])