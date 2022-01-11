#Discord.py Bot Template, by Zennara#8377
#This template is a compilation of code to make it easier to design your own Discord.py Bot
#I made this for my own use, but don't care who uses it, but please credit me if someone asks :)

#imports
import discord #api
import os #for virtual environment secrets on replit
import keep_alive #this keeps our bot alive from the keep_alive.py file
import asyncio #not needed unless creating loop tasks etc (you'll run into it)
import json #to write db to a json file
import requests #to check discord api for limits/bans
from replit import db #database storage
import random

#api limit checker
#rate limits occur when you access the api too much. You can view Discord.py's api below. There it will tell you whether an action will access the api.
#https://discordpy.readthedocs.io/en/stable/api.html
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"You are being Rate Limited : {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

#declare client
intents = discord.Intents.all() #declare what Intents you use, these will be checked in the Discord dev portal
client = discord.Client(intents=intents)


#declare file lists
adjectives = []
items = []
encounters = []

@client.event
async def on_ready():
  print("\nRPG Central Ready.\n")
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="intense d&d"))
  #adjectives
  with open("adjectives.txt") as file:
    adj = file.readlines()
    global adjectives
    adjectives = [line.rstrip() for line in adj]
  #items
  with open("items.txt") as file:
    itm = file.readlines()
    global items
    items = [line.rstrip() for line in itm]
  #encounters
  with open("encounters.txt") as file:
    encounter = file.readlines()
    global encounters
    encounters = [line.rstrip() for line in encounter]

async def error(message, code):
  embed = discord.Embed(color=0xff0000, description=code)
  #if random.randint(1,3) == 1:
  #  embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
  await message.channel.send(embed=embed)

def checkPerms(message):
  if message.author.guild_permissions.manage_guild:
    return True
  else:
    asyncio.create_task(error(message, "You do not have the valid permission: `MANAGE_GUILD`."))

def getItem(player, id):
  count = 0
  count2 = 0
  for guild in db["players"][str(player)]:
    count2 = 0
    for item in db["players"][str(player)][guild]:
      count += 1
      count2 += 1
      if id == count:
        return guild, count2
  return False, False

#chances, from common to legendary, left to right
#must be in order from least to most rare
chances = [50,25,12,6,3]
rarities = ["Common","Uncommon","Rare","Epic","Legendary"]
colors = [0x808080,0x00FF00,0x0000FF,0x7851A9,0xFFD700]
additives = ["-2","-1","+0","+1","+2"]
additiveChances = [5,15,50,15,5]
emojis = ['⚪','🟢','🔵','🟣','🟡']

@client.event
async def on_message(message):
  #check for bots
  if message.author.bot:
    return

  #convert the message to all lowercase
  messagecontent = message.content.lower()

  #check if in server
  if str(message.guild.id) not in db:
    db[str(message.guild.id)] = {"prefix": "!"}

  #this will clear the database if something is broken, WARNING: will delete all entries
  if messagecontent == "!clear":
    for key in db.keys():
      del db[key]
    #my database entries are seperates by server id for each key. this works MOST of the time unless you have a large amount of data
    db[str(message.guild.id)] = {"prefix": "!"}
    db["players"] = {}

  #get prefix
  prefix = db[str(message.guild.id)]["prefix"]

  #this is to dump your databse into database.json. Change this to FALSE to stop this.
  DUMP = True
  if DUMP:
    data2 = {}
    count = 0
    for key in db.keys():
      data2[str(key)] = db[str(key)]
      count += 1

    with open("database.json", 'w') as f:
      json.dump(str(data2), f)

  #change prefix
  if messagecontent.startswith(prefix + "prefix"):
    if checkPerms(message):
      if not any(x in messagecontent for x in ["`",">","@","*","~","_"]):
        if len(messagecontent) <= len(prefix) + 10:
          db[str(message.guild.id)]["prefix"] = message.content.lower().split()[1:][0]
          embed = discord.Embed(color=0x00FF00, description ="Prefix is now `" + message.content.split()[1:][0] + "`")
          embed.set_author(name="Prefix Change")
          #if rand:
          #  embed.add_field(name="᲼",value="\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
          await message.channel.send(embed=embed)
        else:
          await error(message, "Prefix must be between `1` and `3` characters.")
      else:
        await error(message, "Prefix can not contain `` ` `` , `_` , `~` , `*` , `>` , `@`")

  #generate item manually
  if messagecontent == prefix+"gen":
    adj = adjectives[random.randint(0,len(adjectives)-1)]
    itm = items[random.randint(0,len(items)-1)]
    item=""
    emoji=""
    for i in itm:
      if i.isalpha() or i == " ":
        item = item+i
      else:
        emoji = emoji + i
    rarity = random.choices(rarities,chances)[0]
    color = colors[rarities.index(rarity)]

    addition = random.choices(additives,additiveChances)[0]
    
    desc = emoji+" **["+ rarity +"]** "+ adj +" "+ item +" "+ addition
    #send message
    embed = discord.Embed(description=desc, color=color)
    await message.channel.send(embed=embed)

  #chest manually
  if messagecontent == prefix+"chest":
    if checkPerms(message):
      encounter = encounters[random.randint(0,len(encounters)-1)]
      embed = discord.Embed(description="React to open!",color=0xFF0000)
      embed.set_author(name=encounter,icon_url="https://cdn.discordapp.com/attachments/929182726203002920/929966082318536764/chestRed.png")
      msg = await message.channel.send(embed=embed)
      await msg.add_reaction("💎")
  
      def check(reaction, user):
        if reaction.message==msg and str(reaction.emoji)=="💎" and not user.bot:
          asyncio.create_task(reaction.message.clear_reactions()) 
          return True
          
      reaction, user = await client.wait_for('reaction_add', check=check)
  
      adj = adjectives[random.randint(0,len(adjectives)-1)]
      itm = items[random.randint(0,len(items)-1)]
      item=""
      emoji=""
      for i in itm:
        if i.isalpha() or i == " ":
          item = item+i
        else:
          emoji = emoji + i
      rarity = random.choices(rarities,chances)[0]
      color = colors[rarities.index(rarity)]
      addition = random.choices(additives,additiveChances)[0]
      desc = emoji+" **["+ rarity +"]** "+ adj +" "+ item +" "+ addition
      embed = discord.Embed(description=desc, color=color) 
      embed.set_author(name=user.name+" Opened:", icon_url=user.avatar_url)
      await msg.edit(embed=embed)
  
      #find user in db
      if str(user.id) not in db["players"]:
        db["players"][str(user.id)] = {}
      if str(message.guild.id) not in db["players"][str(user.id)]:
        db["players"][str(user.id)][str(message.guild.id)] = []
  
      #give item
      fullItem = emoji+"|"+rarity+"|"+adj+"|"+item+"|"+addition
      db["players"][str(user.id)][str(message.guild.id)].append(fullItem)

  #view bag
  texts = ""
  count = 0
  if messagecontent.startswith(prefix+"pocket") or messagecontent.startswith(prefix+"bag"):
    #check if in database
    if str(message.author.id) in db["players"]:
      for guild in db["players"][str(message.author.id)]:
        for item in db["players"][str(message.author.id)][guild]:
          count +=1
          sections = item.split("|")
          if messagecontent.startswith(prefix+"pocket") and int(guild) != message.guild.id:
            continue
          texts = texts + "`"+str(count)+"` "+(emojis[rarities.index(sections[1])]+" "+sections[0]+" **["+sections[1]+"]** "+sections[2]+" "+sections[3]+" "+sections[4]) + "\n"
    if texts.strip() == "":
      texts = "Your "+messagecontent.replace(prefix,"")+" is offly empty."
    #webhook = await getWebhook(message.channel)
    embed = discord.Embed(description=texts, color=0xFFFFFF)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/929182726203002920/930004332835930132/bag-removebg-preview_1.png")
    embed.set_author(name=messagecontent.replace(prefix,"").capitalize(), icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)

  #delete item
  if messagecontent.startswith(prefix+"delete"):
    splits = messagecontent.split()
    if len(splits) == 2:
      if splits[1].isnumeric():
        id = int(splits[1])
        if str(message.author.id) in db["players"]:
          guild1, count1 = getItem(message.author.id, id)
          if guild1 != False:
            deletedItem = db["players"][str(message.author.id)][guild1][count1-1].replace("|"," ")
            embed = discord.Embed(color=0xff0000, description="⚠️ Are you sure you want to delete\n"+deletedItem)
            msg = await message.channel.send(embed=embed)
            done = False
            def checkR(reaction, user):
              if not user.bot and user.id == message.author.id:
                if reaction.message == msg:
                  if str(reaction.emoji) == "✅":
                    asyncio.create_task(reaction.message.clear_reactions())
                    return True
                  elif str(reaction.emoji) == "❌":
                    asyncio.create_task(reaction.message.clear_reactions())
                    return True
            await msg.add_reaction("✅")
            await msg.add_reaction("⚫")
            await msg.add_reaction("❌")
            while True:
              reaction, user = await client.wait_for('reaction_add', check=checkR)
              if str(reaction.emoji) == "✅":
                break
              if str(reaction.emoji) == "❌":
                done = True
                break
            if not done:
              del db["players"][str(message.author.id)][guild1][count1-1]
              embed = discord.Embed(description="🗑️ Item was deleted.\n"+deletedItem,color=0x00FF00)
              await msg.edit(embed=embed)
            else:
              embed = discord.Embed(description="Deletion cancelled.",color=0x00FF00)
              await msg.edit(embed=embed)
          else:
            await error(message, "Item does not exist.")
        else:
          await error(message, "You do not have any items.")
      else:
        await error(message, "ID must be numeric.")
    else:
      await error(message, "Please specify the item ID.")

  #give item
  if messagecontent.startswith(prefix+"give"):
    splits = messagecontent.split()
    if len(splits) == 3:
      if splits[1].isnumeric():
        mbr = splits[2].replace("<","").replace(">","").replace("@","").replace("!","")
        if mbr.isnumeric():
          if message.guild.get_member(int(mbr)):
            mbr = message.guild.get_member(int(mbr))
            guild1, count1 = getItem(message.author.id, int(splits[1]))
            if guild1 != False:
              item = db["players"][str(message.author.id)][guild1][count1-1]
              del db["players"][str(message.author.id)][guild1][count1-1]
              if str(mbr.id) not in db["players"]:
                db["players"][str(mbr.id)] = {}
                db["players"][str(mbr.id)][guild1] = []
              db["players"][str(mbr.id)][guild1].append(item)
              splits = item.split("|")
              item = splits[0] +" **["+ splits[1] +"]** "+ splits[2] +" "+ splits[3]
              embed = discord.Embed(description="\n"+item+"\n", color=colors[rarities.index(splits[1])])
              embed.set_author(name=message.author.name + " sent", icon_url=message.author.avatar_url)
              embed.set_footer(text="to "+mbr.name, icon_url=mbr.avatar_url)
              await message.channel.send(embed=embed)
            else:
              await error(message, "Item does not exist.")
          else:
            await error(message, "Member not in the guild.")
        else:
          await error(message, "Member must be ID or mention.")
      else:
        await error(message, "Item ID must be numeric.")
    else:
      await error(message, "Please specify the item ID and player mention.")

@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "!"} #for database support


keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Add a secret environment variable named TOKEN in replit (lock icon on left sidebar)
client.run(os.environ.get("TOKEN"))