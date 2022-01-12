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
    if guild != "scrap":
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
emojis = ['⚪','🟢','🔵','🟣','🟡']

additives = ["+0","+1","+2","+3","+4"]
additiveChances = [50,25,12,6,3]

scrapEmoji = "🔩"
scrapAmounts = [10,20,30,40,50]
multipliers = [1 , 1.1 , 1.25 , 1.5 , 2]

def openChest():
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
  fullItem = emoji+"|"+rarity+"|"+adj+"|"+item+"|"+addition
  return desc, color, fullItem

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
      if not any(x in messagecontent for x in ["`",">","@","*","~","_"," "]):
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
        await error(message, "Prefix can not contain `` ` `` , `_` , `~` , `*` , `>` , `@` , ` `")

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
        db["players"][str(user.id)]["scrap"] = 0
      if str(message.guild.id) not in db["players"][str(user.id)]:
        db["players"][str(user.id)][str(message.guild.id)] = []
  
      #give item
      fullItem = emoji+"|"+rarity+"|"+adj+"|"+item+"|"+addition
      db["players"][str(user.id)][str(message.guild.id)].append(fullItem)

  #view bag
  texts = ""
  count = 0
  scrapAmount = "0"
  if messagecontent.startswith(prefix+"pocket") or messagecontent.startswith(prefix+"bag"):
    #check if in database
    if str(message.author.id) in db["players"]:
      scrapAmount = str(db["players"][str(message.author.id)]["scrap"])
      for guild in db["players"][str(message.author.id)]:
        if guild != "scrap":
          for item in db["players"][str(message.author.id)][guild]:
            count +=1
            sections = item.split("|")
            if messagecontent.startswith(prefix+"pocket") and int(guild) != message.guild.id:
              continue
            texts = texts + "`"+str(count)+"` "+(emojis[rarities.index(sections[1])]+" "+sections[0]+" **["+sections[1]+"]** "+sections[2]+" "+sections[3]+" "+sections[4]) + "\n"
    if texts.strip() == "":
      texts = "Your "+messagecontent.replace(prefix,"")+" is offly empty."
    #webhook = await getWebhook(message.channel)
    #add scrap
    texts = scrapEmoji + " **Scrap:** "+ scrapAmount +"\n\n"+ texts
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
            embed = discord.Embed(color=0xff0000, description="⚠️ Are you sure you want to delete this item?\n"+deletedItem)
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
        mbr = splits[1].replace("<","").replace(">","").replace("@","").replace("!","")
        if mbr.isnumeric():
          if message.guild.get_member(int(mbr)):
            mbr = message.guild.get_member(int(mbr))
            if splits[2].isnumeric():
              guild1, count1 = getItem(message.author.id, int(splits[2]))
              if guild1 != False:
                item = db["players"][str(message.author.id)][guild1][count1-1]
                del db["players"][str(message.author.id)][guild1][count1-1]
                if str(mbr.id) not in db["players"]:
                  db["players"][str(mbr.id)] = {}
                  db["players"][str(mbr.id)]["scrap"] = 0
                if guild1 not in db["players"][str(mbr.id)]:
                  db["players"][str(mbr.id)][guild1] = []
                db["players"][str(mbr.id)][guild1].append(item)
                splits = item.split("|")
                item = splits[0] +" **["+ splits[1] +"]** "+ splits[2] +" "+ splits[3] +" "+splits[4]
                embed = discord.Embed(description="\n"+item+"\n", color=colors[rarities.index(splits[1])])
                embed.set_author(name=message.author.name + " sent", icon_url=message.author.avatar_url)
                embed.set_footer(text="to "+mbr.name, icon_url=mbr.avatar_url)
                await message.channel.send(embed=embed)
              else:
                await error(message, "Item does not exist.")
            else:
              await error(message, "Item ID must be numeric.")
          else:
            await error(message, "Member not in the guild.")
        else:
          await error(message, "Member must be ID or mention.")
      else:
        await error(message, "Item ID must be numeric.")
    else:
      await error(message, "Please specify the item ID and player mention.")

  #pay scrap
  if messagecontent.startswith(prefix+"pay"):
    splits = messagecontent.split()
    if len(splits) == 3:
      splits[1] = splits[1].replace("<","").replace(">","").replace("@","").replace("!","")
      if splits[1].isnumeric():
        if message.guild.get_member(int(splits[1])):
          mbr = message.guild.get_member(int(splits[1]))
          if splits[2].isnumeric():
            amount = int(splits[2])
            if amount > 0:
              if str(message.author.id) in db["players"]:
                scrap = db["players"][str(message.author.id)]["scrap"]
                if scrap >= amount:
                  if splits[1] not in db["players"]:
                    db["players"][str(mbr.id)] = {}
                    db["players"][str(mbr.id)]["scrap"] = 0
                  #gave amount to user
                  db["players"][str(mbr.id)]["scrap"] = db["players"][str(mbr.id)]["scrap"] + amount
                  #subtract amount
                  db["players"][str(message.author.id)]["scrap"] = scrap - amount
                  #confirmation message
                  embed = discord.Embed(description="gave **"+str(amount)+"** "+scrapEmoji + " to:")
                  embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                  embed.set_footer(text=mbr.name,icon_url=mbr.avatar_url)
                  await message.channel.send(embed=embed)
                else:
                  await error(message, "You only have "+str(scrap)+scrapEmoji)
              else:
                await error(message, "You do not have any scrap.")
            else:
              await error(message, "Please enter an amount above `0`")
          else:
            await error(message, "Scrap amount should be numeric")
        else:
          await error(message, "Invalid player mention or ID")
      else:
        await error(message, "Player should be mention or their ID")
    else:
      await error(message, "Please input the amount to pay and the member mention.")

  #scrap item
  if messagecontent.startswith(prefix+"scrap"):
    splits = messagecontent.split()
    if len(splits) == 2:
      if splits[1].isnumeric():
        guild1, count1 = getItem(message.author.id, int(splits[1]))
        if guild1 != False:
          splits = db["players"][str(message.author.id)][guild1][count1-1].split("|")
          scrapItem = splits[0]+" **["+splits[1]+"]** "+splits[2]+" "+splits[3]+" "+splits[4]
          scrapAmount = scrapAmounts[rarities.index(splits[1])] * multipliers[int(splits[4].replace("+",""))]
          print(scrapAmounts[rarities.index(splits[1])])
          print(multipliers[int(splits[4].replace("+",""))])
          embed = discord.Embed(color=0xff0000, description="⚠️ Are you sure you want to **scrap** this item for "+ str(scrapAmount) +scrapEmoji +"?\n"+scrapItem)
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
            db["players"][str(message.author.id)]["scrap"] += scrapAmount
            embed = discord.Embed(description="⚙️ Item was scrapped for "+ str(scrapAmount) +scrapEmoji+"\n"+scrapItem,color=0x00FF00)
            await msg.edit(embed=embed)
          else:
            embed = discord.Embed(description="Scrap cancelled.",color=0x00FF00)
            await msg.edit(embed=embed)
        else:
          await error(message, "Item does not exist.")
      else:
        await error(message, "Item ID must be numeric.")
    else:
      await error(message, "Please specify the item ID.")

  #market
  if messagecontent == prefix+"shop":
    scrap = 0
    if str(message.author.id) in db["players"]:
      scrap = db["players"][str(message.author.id)]["scrap"]
    embed2 = discord.Embed(description="```\n▌   Welcome to the shop   ▐\n```")
    embed2.set_author(name="🛒 Marketplace")

    #items
    embed2.add_field(name="1️⃣ - Item Chest | "+"15"+scrapEmoji, value="A common chest containing an item.", inline=False)
    
    embed2.set_footer(text="Scrap: "+str(scrap)+scrapEmoji, icon_url=message.author.avatar_url)
    msg = await message.channel.send(embed=embed2)

    numbers = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    shopAmount = ["1️⃣"]
    def checkR(reaction, user):
      if not user.bot and user.id == message.author.id:
        if reaction.message == msg:
          if str(reaction.emoji) in shopAmount:
            asyncio.create_task(reaction.remove(user))
            return True
          elif str(reaction.emoji) == "❌":
            asyncio.create_task(reaction.message.clear_reactions())
            return True

    boughtItem = ""
    price = ""
    items = []
    prices = []
    await msg.add_reaction("❌")
    for x in range(len(msg.embeds[0].fields)):      
      items.append(" ".join(msg.embeds[0].fields[x].name.split()[1:-2]))
      prices.append(" ".join(msg.embeds[0].fields[x].name.split()[-1:]))
      await msg.add_reaction(numbers[x])  

    while True:
      reaction, user = await client.wait_for('reaction_add', check=checkR)
      if str(reaction.emoji) in shopAmount:
        boughtItem = items[numbers.index(str(reaction.emoji))]
        price = prices[numbers.index(str(reaction.emoji))]
        if scrap >= int(price[:-1]):
          db["players"][str(message.author.id)]["scrap"] = scrap - int(price[:-1])
          
          desc, color, fullItem = openChest()
          #find user in db
          if str(message.author.id) not in db["players"]:
            db["players"][str(message.author.id)] = {}
            db["players"][str(message.author.id)]["scrap"] = 0
          if str(message.guild.id) not in db["players"][str(message.author.id)]:
            db["players"][str(message.author.id)][str(message.guild.id)] = []
      
          #give item
          db["players"][str(message.author.id)][str(message.guild.id)].append(fullItem)
          scrap = db["players"][str(message.author.id)]["scrap"]
          
          embed = discord.Embed(description="You bought a **" +boughtItem+ "** for " +price+"\n"+desc,color=color)
          await message.channel.send(embed=embed)
          embed2.set_footer(text="Scrap: "+str(scrap)+scrapEmoji, icon_url=message.author.avatar_url)
          await msg.edit(embed=embed2)
        else:
          await error(message, "You only have "+str(scrap)+scrapEmoji)
      if str(reaction.emoji) == "❌":
        embed = discord.Embed(description="You left the shop.",color=0xFF0000)
        await msg.edit(embed=embed)
        break

  #additem
  if messagecontent.startswith(prefix+"additem"):
    pass
  #addscrap
  if messagecontent.startswith(prefix+"addscrap"):
    pass
  #trade command
  if messagecontent.startswith(prefix+"trade"):
    splits = messagecontent.split()
    if len(splits) == 2:
      splits[1] = splits[1].replace("<","").replace(">","").replace("@","").replace("!","")
      if splits[1].isnumeric():
        if message.guild.get_member(int(splits[1])):
          tradee = message.guild.get_member(int(splits[1]))
          if tradee.id != message.author.id:
            embed = discord.Embed(description="▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃")
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            embed.set_footer(text=tradee.name, icon_url=tradee.avatar_url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/929182726203002920/930381037589135390/trading.png")
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("⚫")
            await msg.add_reaction("❌")
            done = False
            traderAgree = False
            tradeeAgree = False
            def checkR(reaction, user):
              if not user.bot:
                if reaction.message == msg:
                  if str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌":
                    if user.id == message.author.id or user.id == tradee.id:
                      asyncio.create_task(reaction.remove(user))
                      return True
  
            user2 = ""
            while True:
              reaction, user = await client.wait_for('reaction_add', check=checkR)
              
              if str(reaction.emoji) == "✅":
                if user.id == message.author.id:
                  if not traderAgree:
                    traderAgree = True
                elif user.id == tradee.id:
                  if not tradeeAgree:
                    tradeeAgree = True
              elif str(reaction.emoji) == "❌":
                if user.id == message.author.id:
                  if traderAgree == False:
                    done = False
                    user2 = user
                    break
                  traderAgree = False
                elif user.id == tradee.id:
                  if tradeeAgree == False:
                    done = False
                    user2 = user
                    break
                  tradeeAgree = False
  
              embed = discord.Embed(description=traderTrades+"/n-----------------------------------/n"+tradeeTrades)
              embed.set_author(name=message.author.name+(" -- [✅ Agreed]" if traderAgree else ""), icon_url=message.author.avatar_url)
              embed.set_footer(text=tradee.name+(" -- [✅ Agreed]" if tradeeAgree else ""), icon_url=tradee.avatar_url)
              embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/929182726203002920/930381037589135390/trading.png")
              await msg.edit(embed=embed)
                
              if traderAgree and tradeeAgree:
                done = True
                break
           
            if done:
              await msg.clear_reactions()
              embed = discord.Embed(description=traderTrades+"/n-----------------------------------/n"+tradeeTrades)
              embed.set_author(name=message.author.name+(" -- [✅ Confirmed]" if traderAgree else ""), icon_url=message.author.avatar_url)
              embed.set_footer(text=tradee.name+(" -- [✅ Confirmed]" if tradeeAgree else ""), icon_url=tradee.avatar_url)
              embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/929182726203002920/930380635300823060/temp-removebg-preview.png")
              await msg.edit(embed=embed)
              print("confirmed")
            else:
              await msg.clear_reactions()
              embed = discord.Embed(description=traderTrades+"/n-----------------------------------/n"+tradeeTrades)
              embed.set_author(name=message.author.name+(" -- [🚫 Cancelled]" if user2.id==message.author.id else ""), icon_url=message.author.avatar_url)
              embed.set_footer(text=tradee.name+(" -- [🚫 Cancelled]" if user2.id==tradee.id else ""), icon_url=tradee.avatar_url)
              embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/929182726203002920/930394152309510184/images-removebg-preview.png")
              await msg.edit(embed=embed)
          else:
            await error(message, "You can not trade with yourself.")
        else:
          await error(message, "Member does not exist.")
      else:
        await error(message, "Member must be mention or ID.")
    else:
      await error(message, "Please specify the member mention or ID.")

@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "!"} #for database support
  db["players"] = {}


keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Add a secret environment variable named TOKEN in replit (lock icon on left sidebar)
client.run(os.environ.get("TOKEN"))