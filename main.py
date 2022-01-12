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

def giveOP(owner):
  adj = "Unobtainable Zenn's"
  itm = "💎Gem"
  item=""
  emoji=""
  for i in itm:
    if i.isalpha() or i == " ":
      item = item+i
    else:
      emoji = emoji + i
  rarity = "Epic"
  color = colors[rarities.index(rarity)]
  addition = "+5"
  op = emoji+"|"+rarity+"|"+adj+"|"+item+"|"+addition
  db["players"][str(owner)][str(806706495466766366)].append(op)

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

chestprice = 50
rerollPrice = 25

pageSize = 8

def openChest():
  adj = adjectives[random.randint(0,len(adjectives)-1)]
  if random.randint(1,5) == 1:
    adj = adj +" "+ adjectives[random.randint(0,len(adjectives)-1)]
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
    db[str(message.guild.id)] = {"prefix": "!", "name" : message.guild.name, "join" : False}

  #this will clear the database if something is broken, WARNING: will delete all entries
  if messagecontent == "!clear":
    for key in db.keys():
      del db[key]
    #my database entries are seperates by server id for each key. this works MOST of the time unless you have a large amount of data
    db[str(message.guild.id)] = {"prefix": "!", "name" : message.guild.name, "join" : False}
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
    desc, color, fullItem = openChest()
    #send message
    embed = discord.Embed(description=desc, color=color)
    await message.channel.send(embed=embed)

  #chest manually
  if messagecontent == prefix+"chest":
    #if checkPerms(message):
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
  
      desc, color, fullItem = openChest()
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
      db["players"][str(user.id)][str(message.guild.id)].append(fullItem)

  #help
  if messagecontent == prefix+"help":
    text = f"""
    **Member Commands**
    `{prefix}help` - Displays this message
    `{prefix}prefix <new>` - Changes the command prefix
    `{prefix}bag` - Show all of your items
    `{prefix}pocket` - Show all your items from this server
    `{prefix}shop` - View the marketplace
    `{prefix}trade <member>` - Start a trade with another player
    `{prefix}distill <id>` - Change the adjective of your item
    `{prefix}transmute <id>` - Change the object of your item
    `{prefix}scrap <id>` - Scrap the item
    `{prefix}give <member> <id>` - Give the item to another player
    `{prefix}delete <id>` - Delete an item

    **Staff Commands**
    `{prefix}private` - Set your server to private
    `{prefix}public` - Set your server to public
    """
    embed = discord.Embed(description=text, color=0x000000)
    embed.set_footer(text="<> - Required | [] - Optional")
    await message.channel.send(embed=embed)

  #help for each command
  elif messagecontent.startswith(prefix+"help"):
    commands = ["help","prefix","bag","pocket","shop","trade","distill","transmute","scrap","give","delete","private","public"]
    if messagecontent.split()[1] in commands:
      cmd = commands.index(messagecontent.split()[1])
      if cmd==0:
        text=f"""
        This shows a page with all of the available commands. Anything wrapped in `<` and `>` are **required** arguments, while anything wrapped in `[` and `]` are **optional** arguments. An argument is a value you put into the command like information, a member, or an ID. You can find more help in my [discord server](https://discord.gg/y5FJsThMsc).
        """
      elif cmd==1:
        text=f"""
        This command will change the prefix for your server. Every server with this bot can have their own, custom prefix. {message.guild.name}'s prefix is currently `{prefix}`
        """
      elif cmd==2:
        text=f"""
        This will show you all of the contents of your inventory across all servers. You can find your **items** and **scrap** {scrapEmoji} here. Items are seperated by server. If the server you found an item in is a public server, a hyperlink to that server will be it's name.
        """
      elif cmd==3:
        text=f"""
        This will show you your inventory in a more simplified version. Only the items from the current server you used the command in will be shown.
        """
      elif cmd==4:
        text=f"""
        This opens the **shop**. You can buy chests here for new items with your **scrap** {scrapEmoji}. The current price is {chestprice} {scrapEmoji}.
        """
      elif cmd==5:
        text=f"""
        This initiates a trade with another player. If they accept, you can add and remove **items** or **scrap** {scrapEmoji} to trade. To accept a trade, react with ✅. To cancel your acceptance or to cancel the trade, react with ❌. When both player confirm the trade, the agreed upon items will be transferred.
        """
      elif cmd==6:
        text=f"""
        This will give you a chance to get a new **adjective** for your item. Currently this costs {rerollPrice} {scrapEmoji}.
        """
      elif cmd==7:
        text=f"""
        This will give you a chance to get a new **noun** and **emoji** for your item. Currently this costs {rerollPrice} {scrapEmoji}.
        """
      elif cmd==8:
        text=f"""
        This will scrap the item with the `id` you inputted. A confirmation message will appear with the amount it is scrapped for. Scrap prices are determined by the **rarity** and multiplied by the **addition** (+-).
        """
      elif cmd==9:
        text=f"""
        This will give the item matching the `id` to the designated `member`. You can use the members **mention** or **id** for the command.
        """
      elif cmd==10:
        text=f"""
        This will delete the item matching the `id`. Warning: this **can not** be undone.
        """
      elif cmd==11:
        text=f"""
        Set your server to `private`. This **will not allow** users from other guilds to join off items and bags. This will also delete any valid invite links created by {client.user.name}. Only usable by members with the `Manage_Guild` permission.
        """
      elif cmd==12:
        text=f"""
        Set your server to `public`. This **will allow** users from other guilds to join off items and bags. Only usable by members with the `Manage_Guild` permission.
        """

      #send command
      embed = discord.Embed(description=text, color=0x000000, title=commands[commands.index(messagecontent.split()[1])].capitalize())
      await message.channel.send(embed=embed)

  #private
  if messagecontent == prefix+"private":
    if checkPerms(message):
      if db[str(message.guild.id)]["join"] == True:
        embed = discord.Embed(description="🔒 Your server is now private on **"+client.user.name+"**.")
        db[str(message.guild.id)]["join"] = False
        for invite in await message.guild.invites():
          if invite.inviter.id == client.user.id:
            await invite.delete(reason="Server set to private")
            break
      else:
        embed = discord.Embed(description="🔒 Your server is already private on **"+client.user.name+"**.")
      embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url, color=0x000000)
      await message.channel.send(embed=embed)

  #private
  if messagecontent == prefix+"public":
    if checkPerms(message):
      if db[str(message.guild.id)]["join"] == False:
        embed = discord.Embed(description="🔓 Your server is now public on **"+client.user.name+"**.", color=0x000000)
        db[str(message.guild.id)]["join"] = True
      else:
        embed = discord.Embed(description="🔓 Your server is already public on **"+client.user.name+"**.", color=0x000000)
      embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
      await message.channel.send(embed=embed)

  #view bag
  inPage = 1
  if messagecontent == prefix+"pocket" or messagecontent == prefix+"bag":
    async def openBag(msg, page):
      texts = ""
      count = 0
      itemsOnPage = 0
      scrapAmount = "0"
      #check if in database
      if str(message.author.id) in db["players"]:
        scrapAmount = str(db["players"][str(message.author.id)]["scrap"])
        for guild in db["players"][str(message.author.id)]:
          if itemsOnPage >= pageSize:
            break
          if guild != "scrap":
            if db["players"][str(message.author.id)][guild]:
              #get invite link
              link = db[str(guild)]["name"]
              try:
                done = False
                if db[str(message.guild.id)]["join"] == True:
                  g = client.get_guild(int(guild))
                  for invite in await g.invites():
                    if invite.inviter.id == client.user.id:
                      link = "["+g.name+"]("+invite.url+")"
                      done = True
                      break
                  if not done:
                    inv = await g.text_channels[0].create_invite()
                    link = "["+g.name+"]("+inv.url+")"
              except:
                pass
              if messagecontent.startswith(prefix+"pocket") and int(guild) == message.guild.id:
                texts = texts + "**" + link + "**\n"
              elif messagecontent.startswith(prefix+"bag"):
                texts = texts + "**" + link + "**\n"
              for item in db["players"][str(message.author.id)][guild]:
                if itemsOnPage >= pageSize:
                  break
                count +=1
                sections = item.split("|")
                if messagecontent.startswith(prefix+"pocket") and int(guild) != message.guild.id:
                  continue
                if page*pageSize - (pageSize+1) <= count <= page*pageSize:
                  itemsOnPage += 1
                  texts = texts + "`"+str(count)+"` "+(emojis[rarities.index(sections[1])]+" "+sections[0]+" **["+sections[1]+"]** "+sections[2]+" "+sections[3]+" "+sections[4]) + "\n"
              if messagecontent.startswith(prefix+"bag") or (messagecontent.startswith(prefix+"pocket") and int(guild) == message.guild.id):
                texts = texts + "\n"
      if texts.strip() == "":
        texts = "Your "+messagecontent.replace(prefix,"")+" is awfully empty."
      #webhook = await getWebhook(message.channel)
      #add scrap
      texts = scrapEmoji + " **Scrap:** "+ scrapAmount +"\n\n"+ texts
      embed = discord.Embed(description=texts, color=0x000000)
      embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/929182726203002920/930004332835930132/bag-removebg-preview_1.png")
      embed.set_author(name=message.author.name+"'s "+messagecontent.replace(prefix,"").capitalize(), icon_url=message.author.avatar_url)
      await msg.edit(embed=embed)

      if page != 1:
        await msg.add_reaction("⬅️")
      else:
        await msg.add_reaction("⚫")
      if itemsOnPage >= pageSize:
        await msg.add_reaction("➡️")

      def check(reaction, user):
        if not user.bot:
          if reaction.message == msg:
            if user.id == message.author.id:
              if str(reaction.emoji) == "⬅️":
                if page != 1:
                  asyncio.create_task(reaction.message.clear_reactions())
                  return True
              elif str(reaction.emoji) == "➡️":
                asyncio.create_task(reaction.message.clear_reactions())
                return True

      try:
        reaction, user = await client.wait_for('reaction_add', check=check, timeout=30)
      except asyncio.TimeoutError:
        await msg.clear_reactions()
      else:
        if str(reaction.emoji) == "⬅️":
          if page != 1:
            await openBag(msg,page-1)
        elif str(reaction.emoji) == "➡️":
          await openBag(msg,page+1)
          

    embed = discord.Embed(color=0x000000,description="🎒 **Opening "+message.author.name+"'s "+("Bag" if messagecontent==prefix+"bag" else "Pocket")+". . .**")
    msg = await message.channel.send(embed=embed)
    if messagecontent == prefix+"bag":
      await openBag(msg,inPage)
    else:
      await openBag(msg,inPage)

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
            embed = discord.Embed(color=0x000000, description=deletedItem, title="⚠️ Are you sure you want to delete?")
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
              embed = discord.Embed(description=deletedItem,color=0x000000, title="🗑️ Item deleted.")
              await msg.edit(embed=embed)
            else:
              embed = discord.Embed(description="✅ Deletion cancelled.",color=0x000000)
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
      if splits[2].isnumeric():
        mbr = splits[1].replace("<","").replace(">","").replace("@","").replace("!","")
        if mbr.isnumeric():
          if message.guild.get_member(int(mbr)):
            mbr = message.guild.get_member(int(mbr))
            guild1, count1 = getItem(message.author.id, int(splits[2]))
            if str(message.author.id) in db["players"]:
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
              await error(message, "You have no items to give.")
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
                  embed = discord.Embed(color=0x000000,description="gave **"+str(amount)+"** "+scrapEmoji + " to:")
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
        if str(message.author.id) in db["players"]:
          guild1, count1 = getItem(message.author.id, int(splits[1]))
          if guild1 != False:
            splits = db["players"][str(message.author.id)][guild1][count1-1].split("|")
            scrapItem = emojis[rarities.index(splits[1])] +" "+ splits[0]+" **["+splits[1]+"]** "+splits[2]+" "+splits[3]+" "+splits[4]
            scrapAmount = scrapAmounts[rarities.index(splits[1])] * multipliers[int(splits[4].replace("+",""))]
            embed = discord.Embed(color=0xff0000, description=scrapItem, title="⚠️ Are you sure you want to **scrap** this item for "+ str(scrapAmount) +scrapEmoji +"?")
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
              embed = discord.Embed(description=scrapItem,color=0x000000,title="⚙️ Item was scrapped for "+ str(scrapAmount) +scrapEmoji)
              await msg.edit(embed=embed)
            else:
              embed = discord.Embed(description="❌ Scrap cancelled.",color=0x000000)
              await msg.edit(embed=embed)
          else:
            await error(message, "You have no items to scrap.")
        else:
          await error(message, "Item does not exist.")
      else:
        await error(message, "Item ID must be numeric.")
    else:
      await error(message, "Please specify the item ID.")

  #reroll
  global items
  if messagecontent.startswith(prefix+"distill") or messagecontent.startswith(prefix+"transmute"):
    splits = messagecontent.split()
    if len(splits) == 2:
      if splits[1].isnumeric():
        guild1, count1 = getItem(message.author.id, int(splits[1]))
        if guild1 != False:
          if splits[0] == prefix+"distill" or splits[0] == prefix+"transmute":
            scrap = db["players"][str(message.author.id)]["scrap"]
            if scrap >= rerollPrice:
              db["players"][str(message.author.id)]["scrap"] = scrap - rerollPrice
              item=""
              emoji=""
              splitItem = db["players"][str(message.author.id)][guild1][count1-1].split("|")
              adj = splitItem[2]
              item = splitItem[3]
              emoji = splitItem[0]
              if splits[0] == prefix+"distill":
                adj = adjectives[random.randint(0,len(adjectives)-1)]
                if random.randint(1,5) == 1:
                  adj = adj +" "+ adjectives[random.randint(0,len(adjectives)-1)]
              elif splits[0] == prefix+"transmute":
                item = ""
                emoji = ""
                itm = items[random.randint(0,len(items)-1)]
                for i in itm:
                  if i.isalpha() or i == " ":
                    item = item+i
                  else:
                    emoji = emoji + i
              rarity = splitItem[1]
              color = colors[rarities.index(rarity)]
              addition = splitItem[4]
              desc = emoji+" **["+ rarity +"]** "+ adj +" "+ item +" "+ addition
              fullItem = emoji+"|"+rarity+"|"+adj+"|"+item+"|"+addition
              db["players"][str(message.author.id)][guild1].insert(count1-1,fullItem)
              db["players"][str(message.author.id)][guild1].pop(count1)
              embed = discord.Embed(description=desc, title="Item "+ ("Distilled" if splits[0]==prefix+"distill" else "Transmuted") +" for "+str(rerollPrice)+" "+scrapEmoji, color=color)
              await message.channel.send(embed=embed)
            else:
              await error(message, "You only have **"+str(scrap)+"** "+scrapEmoji)
          else:
            await error(message, "Reroll type needs to be `adj` or `noun`")
        else:
          await error(message, "Item does not exist")
      else:
        await error(message, "Item ID must be numeric.")
    else:
      await error(message, "Please specify the item ID.")

  #move an item in your bag
  if messagecontent.startswith(prefix+"move"):
    splits = messagecontent.split()
    if len(splits) == 3:
      if splits[1].isnumeric():
        if splits[2].isnumeric():
          if str(message.author.id) in db["players"]:
            guild1, count1 = getItem(message.author.id, int(splits[1]))
            if guild1 != False:
              guild2, count2 = getItem(message.author.id, int(splits[2]))
              if guild2 != False:
                if guild1 == guild2:
                  insertItem = db["players"][str(message.author.id)][guild1][count1-1]
                  db["players"][str(message.author.id)][guild1].pop(count1-1)
                  db["players"][str(message.author.id)][guild1].insert(count2-1, insertItem)           
                  item1 = db["players"][str(message.author.id)][guild1][count2-1].split("|")
                  item1 = emojis[rarities.index(item1[1])] +" "+ item1[0] +" **["+ item1[1] +"]** "+ item1[2] +" "+ item1[3] +" "+ item1[4]
                  embed = discord.Embed(color=colors[rarities.index(item1[1])],title="🚚 **Moved**",description=item1+"\n`"+splits[1]+"` ➡️ `"+splits[2]+"`")
                  await message.channel.send(embed=embed)
                else:
                  await error(message, "Cannot move item to an index of another guild.")
              else:
                await error(message, "Index does not exist.")
            else:
              await error(message, "Item does not exist.")
          else:
            await error(message, "You do not have any items.")
        else:
          await error(message, "Index is not a number.")
      else:
        await error(message, "Item ID needs to be a number.")
    else:
      await error(message, "Input needs to have item ID and index to move to.")

  #swap two items in your bag
  if messagecontent.startswith(prefix+"swap"):
    splits = messagecontent.split()
    if len(splits) == 3:
      if splits[1].isnumeric():
        if splits[2].isnumeric():
          if str(message.author.id) in db["players"]:
            guild1, count1 = getItem(message.author.id, int(splits[1]))
            if guild1 != False:
              guild2, count2 = getItem(message.author.id, int(splits[2]))
              if guild2 != False:
                if guild1 == guild2:
                  item1 = db["players"][str(message.author.id)][guild1][count1-1].split("|")
                  item1 = "`"+splits[1]+"` "+emojis[rarities.index(item1[1])] + item1[0] +" **["+ item1[1] +"]** "+ item1[2] +" "+ item1[3] +" "+ item1[4]
                  item2 = db["players"][str(message.author.id)][guild2][count2-1].split("|")
                  item2 = "`"+splits[2]+"` "+emojis[rarities.index(item2[1])] + item2[0] +" **["+ item2[1] +"]** "+ item2[2] +" "+ item2[3] +" "+ item2[4]
                  db["players"][str(message.author.id)][guild1][count1-1],db["players"][str(message.author.id)][guild2][count2-1] = db["players"][str(message.author.id)][guild2][count2-1],db["players"][str(message.author.id)][guild1][count1-1]
                  embed = discord.Embed(color=0x000000,title="🔀 **Swapped**",description=item1 +"\n**with**\n" + item2)
                  await message.channel.send(embed=embed)
                else:
                  await error(message, "Cannot swap items from two different servers.")
              else:
                await error(message, "Swapped item does not exist")
            else:
              await error(message, "Swapping item does not exist.")
          else:
            await error(message, "You do not have any items to swap.")
        else:
          await error(message, "The item you wish to swap with must be it's ID")
      else:
        await error(message, "The item you wish to swap must be it's ID")
    else:
      await error(message, "Please specify the two items you want to swap")

  #market
  if messagecontent == prefix+"shop":
    scrap = 0
    if str(message.author.id) in db["players"]:
      scrap = db["players"][str(message.author.id)]["scrap"]
    embed2 = discord.Embed(color=0x000000,description="```\n▌   Welcome to the shop   ▐\n```")
    embed2.set_author(name="🛒 Marketplace")

    #items
    embed2.add_field(name="1️⃣ - Item Chest | "+str(chestprice)+scrapEmoji, value="A common chest containing an item.", inline=False)
    
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
    shopItems = []
    prices = []
    await msg.add_reaction("❌")
    for x in range(len(msg.embeds[0].fields)):      
      shopItems.append(" ".join(msg.embeds[0].fields[x].name.split()[1:-2]))
      prices.append(" ".join(msg.embeds[0].fields[x].name.split()[-1:]))
      await msg.add_reaction(numbers[x])  

    while True:
      reaction, user = await client.wait_for('reaction_add', check=checkR)
      if str(reaction.emoji) in shopAmount:
        boughtItem = shopItems[numbers.index(str(reaction.emoji))]
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
  db[str(guild.id)] = {"prefix": "!", "name" : guild.name, "join" : False} #for database support

@client.event
async def on_guild_update(before, after):
  if str(before.id) not in db:
    db[str(before.id)] = {"prefix": "!", "name" : after.name, "join" : False}
  db[str(before.id)] = {"prefix": db[str(before.id)]["prefix"], "name" : after.name, "join" : False}


keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Add a secret environment variable named TOKEN in replit (lock icon on left sidebar)
client.run(os.environ.get("TOKEN"))