import discord
import os
import asyncio
import json
import random
from datetime import datetime

intents = discord.Intents.all()
client = discord.Client(intents=intents)

nonGuilds = ["trading", "items", "shows", "scrap"]
chances = [50, 25, 12, 6, 3]
rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
colors = [0x808080, 0x00FF00, 0x0000FF, 0x7851A9, 0xFFD700]
emojis = ['⚪', '🟢', '🔵', '🟣', '🟡']
additives = ["+0", "+1", "+2", "+3", "+4"]
additiveChances = [50, 25, 12, 6, 3]
scrapEmoji = "🔩"
scrapAmounts = [10, 20, 30, 40, 50]
multipliers = [1, 1.1, 1.25, 1.5, 2]
chestprice = 50
brushPrice = 10
rerollPrice = 25
chestChanceMAX = 33
pageSize = 8
adjectives = []
items = []
encounters = []
showoffs = []


def load_file(filename):
    try:
        with open(filename, encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except UnicodeDecodeError:
        print(f"Error: {filename} contains invalid characters.")
        return []


def update_data():
    global data
    with open("data.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2)
    with open('data.json', encoding="utf-8") as f:
        data = json.load(f)


@client.event
async def on_ready():
    global adjectives, items, encounters, showoffs
    print("\nRPG Central Ready.\n")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="intense d&d"))
    adjectives = load_file("adjectives.txt")
    items = load_file("items.txt")
    encounters = load_file("encounters.txt")
    showoffs = load_file("showoffs.txt")
    for member in data["players"]:
        data["players"][str(member)]["trading"] = ""
    update_data()


async def error(message, code):
    embed = discord.Embed(color=0xff0000, description=code)
    await message.channel.send(embed=embed)


def checkPerms(message):
    if message.author.guild_permissions.manage_guild:
        return True
    else:
        asyncio.create_task(error(message, "You do not have the valid permission: `MANAGE_GUILD`."))
        return False


async def checkZen(message):
    if message.author.id == (await client.application_info()).owner.id:
        return True
    else:
        await error(message, "You must be the application owner to use this.")
        return False


def getItem(player, id):
    count = 0
    count2 = 0
    if str(player) in data["players"]:
        for guild in data["players"][str(player)]:
            if guild not in nonGuilds or guild == "items":
                count2 = 0
                for item in data["players"][str(player)][guild]:
                    count += 1
                    count2 += 1
                    if id == count:
                        return guild, count2
    return False, False


def openChest():
    adj = adjectives[random.randint(0, len(adjectives) - 1)]
    if random.randint(1, 5) == 1:
        adj = adj + " " + adjectives[random.randint(0, len(adjectives) - 1)]
    itm = items[random.randint(0, len(items) - 1)]
    item = ""
    emoji = ""
    for i in itm:
        if i.isalpha() or i == " ":
            item = item + i
        else:
            emoji = emoji + i
    rarity = random.choices(rarities, chances)[0]
    color = colors[rarities.index(rarity)]
    addition = random.choices(additives, additiveChances)[0]
    desc = emoji + " **[" + rarity + "]** " + adj + " " + item + " " + addition
    fullItem = emoji + "|" + rarity + "|" + adj + "|" + item + "|" + addition
    return desc, color, fullItem


@client.event
async def on_message(message):
    if message.author.id == client.user.id or message.author.bot:
        return

    print(f"\n[{message.guild.name}]-{message.author.name}: {message.content}")

    if str(message.guild.id) not in data:
        data[str(message.guild.id)] = {"prefix": "!", "name": message.guild.name, "join": False}
        update_data()

    prefix = data[str(message.guild.id)]["prefix"]
    messagecontent = message.content.lower()

    # Add your commands here
    if message.author.id == client.user.id:
        print("BOT MESSAGE")
    else:
        print(f"\n[{message.guild.name}]-{message.author.name}: {message.content}")

        # check for bots
    if message.author.bot:
        return

    # this will clear the database if something is broken, WARNING: will delete all entries
    if messagecontent == prefix + "clear":
        if await checkZen(message):
            for key in data.keys():
                del data[key]
            # my database entries are seperates by server id for each key. this works MOST of the time unless you have a large amount of data
            data[str(message.guild.id)] = {"prefix": "!", "name": message.guild.name, "join": False}
            data["players"] = {}
            embed = discord.Embed(description="🆑 **Database was cleared**")
            await message.channel.send(embed=embed)
            update_data()

    # this is to dump your databse into database.json. Change this to FALSE to stop this.
    DUMP = False
    if DUMP:
        data2 = {}
        count = 0
        for key in data.keys():
            data2[str(key)] = data[str(key)]
            count += 1

        with open("database.json", 'w') as f:
            json.dump(str(data2), f)

    # get trading bool
    def trading():
        if str(message.author.id) in data["players"]:
            return data["players"][str(message.author.id)]["trading"]
        else:
            return ""

    # change prefix
    if messagecontent.startswith(prefix + "prefix"):
        if checkPerms(message):
            print(messagecontent[len(prefix) + 7:])
            if not any(x in messagecontent[len(prefix) + 7:] for x in ["`", ">", "@", "*", "~", "_", " "]):
                if len(messagecontent) <= len(prefix) + 10:
                    if len(messagecontent.split()) > 1:
                        data[str(message.guild.id)]["prefix"] = message.content.lower().split()[1:][0]
                        embed = discord.Embed(color=0x00FF00,
                                              description="Prefix is now `" + message.content.split()[1:][0] + "`")
                        embed.set_author(name="Prefix Change")
                        await message.channel.send(embed=embed)
                        update_data()
                else:
                    await error(message, "Prefix must be between `1` and `3` characters.")
            else:
                await error(message, "Prefix can not contain `` ` `` , `_` , `~` , `*` , `>` , `@` , ` `")

    # showoff commands
    if messagecontent.startswith(prefix + "showoff"):
        splits = messagecontent.split(" ", 1)
        if len(splits) == 2:
            if splits[1].isnumeric():
                guild1, count1 = getItem(message.author.id, int(splits[1]))
                if guild1 != False:
                    print(guild1)
                    print(count1)
                    item = data["players"][str(message.author.id)][guild1][count1 - 1]
                    splits = item.split("|")
                    if len(splits) == 5:
                        item = splits[0] + " **[" + splits[1] + "]** " + splits[2] + " " + splits[3] + " " + splits[4]
                        color = colors[rarities.index(splits[1])]
                    else:
                        type = ""
                        if guild1 == "items":
                            type = "Paintbrush 🖌️"
                        item = f"{splits[0]} {splits[1]} {type}"
                        color = 0x000000
                    brag = showoffs[random.randint(0, len(showoffs) - 1)]
                    embed = discord.Embed(description=item, color=color)
                    embed.set_author(name=f"{message.author.name} {brag}", icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                else:
                    await error(message, "Item does not exist")
            else:
                await error(message, "Item ID must be numeric")
        else:
            await error(message, "Please specify the item ID to showoff")

    # generate item manually
    if messagecontent == prefix + "testgen":
        if await checkZen(message):
            desc, color, fullItem = openChest()
            # send message
            embed = discord.Embed(title="🚧 Item Test Generated", description=desc, color=color)
            await message.channel.send(embed=embed)

    # generate and give an item
    if messagecontent.startswith(prefix + "gen"):
        if await checkZen(message):
            sp = message.content.split(" ", 1)
            if len(sp) == 2:
                splits = sp[1].split("|")
                splits = [s.strip() for s in splits]
                if len(splits) == 5:
                    emoji = splits[0]
                    adj = splits[2]
                    item = splits[3]
                    if splits[1].lower() in [s.lower() for s in rarities]:
                        rarity = rarities[[s.lower() for s in rarities].index(splits[1].lower())]
                        if splits[4].replace("+", "") in [s.replace("+", "") for s in additives]:
                            addition = additives[
                                [s.replace("+", "") for s in additives].index(splits[4].replace("+", ""))]
                            color = colors[rarities.index(rarity)]
                            desc = emoji + " **[" + rarity + "]** " + adj + " " + item + " " + addition
                            fullItem = emoji + "|" + rarity + "|" + adj + "|" + item + "|" + addition
                            # send message
                            embed = discord.Embed(title="🧬 Item Generated", description=desc, color=color)
                            await message.channel.send(embed=embed)
                            if str(message.author.id) not in data["players"]:
                                data["players"][str(message.author.id)] = {"scrap": 0, "trading": "", "items": [],
                                                                           "shows": {}}
                            if str(message.guild.id) not in data["players"][str(message.author.id)]:
                                data["players"][str(message.author.id)][str(message.guild.id)] = []
                            data["players"][str(message.author.id)][str(message.guild.id)].append(fullItem)
                            update_data()
                        else:
                            await error(message, "Invalid additive")
                    else:
                        await error(message, "Invalid rarity")
                else:
                    await error(message, "Not enough arguments for item")
            else:
                await error(message, "Please specify the item")

    async def spawnChest():
        encounter = encounters[random.randint(0, len(encounters) - 1)]
        embed = discord.Embed(description="React to open!", color=0xFF0000)
        embed.set_author(name=encounter,
                         icon_url="https://cdn.discordapp.com/attachments/929182726203002920/929966082318536764/chestRed.png")
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("💎")

        def check(reaction, user):
            if reaction.message == msg and str(reaction.emoji) == "💎" and not user.bot:
                asyncio.create_task(reaction.message.clear_reactions())
                return True

        try:
            reaction, user = await client.wait_for('reaction_add', check=check, timeout=300)
        except asyncio.TimeoutError:
            embed = discord.Embed(description="🏃 Looks like someone got the loot before you...")
            await msg.edit(embed=embed)
        else:
            desc, color, fullItem = openChest()
            embed = discord.Embed(description=desc, color=color)
            embed.set_author(name=user.name + " Opened:", icon_url=user.avatar_url)
            await msg.edit(embed=embed)
            # find user in data
            if str(user.id) not in data["players"]:
                data["players"][str(user.id)] = {"scrap": 0, "trading": "", "items": [], "shows": {}}
            if str(message.guild.id) not in data["players"][str(user.id)]:
                data["players"][str(user.id)][str(message.guild.id)] = []
            # give item
            data["players"][str(user.id)][str(message.guild.id)].append(fullItem)
            update_data()

    # chest manually
    if messagecontent == prefix + "chest":
        if await checkZen(message):
            await spawnChest()

    if random.randint(1, chestChanceMAX) == 1:
        await spawnChest()

    # ULTRA SECRETS
    if random.randint(1, 1000000) == 1:
        embed = discord.Embed(
            description="Welp! Looks like you broke the entire space-time continium. If you wish to now be the **All-Watching Supreme Overlord of the Universe**, please enter **the password**.",
            title="🌌 A Multidimentional Rift Has Opened", color=0x7851A9)
        embed.set_footer(text="you have 30 seconds before the universe implodes")
        msg = await message.channel.send(embed=embed)

        def check(m):
            if m.guild.id == message.guild.id:
                if m.content == str(os.environ.get("PASSWORD")):
                    return True

        try:
            m1 = await client.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                description="The universe will never be the same thanks to you. I hope you sleep well.",
                title="💥 The End of Days...", color=0xFF0000)
            await msg.edit(embed=embed)
        else:
            embed = discord.Embed(
                description="Thank you, " + m1.author.mention + ", for embracing the universe in your arms.\n*Here is your crown.*",
                title="👑 A Ruler is Crowned", color=0xFFD700)
            await msg.edit(embed=embed)
            if str(m1.author.id) not in data["players"]:
                data["players"][str(m1.author.id)] = {"scrap": 0, "trading": "", "items": [], "shows": {}}
            if str(message.guild.id) not in data["players"][str(m1.author.id)]:
                data["players"][str(m1.author.id)][str(message.guild.id)] = []
            data["players"][str(m1.author.id)][str(message.guild.id)].append(
                "👑|Legendary|*Crown of the Supreme*|**Overlord**|+4")
            update_data()

    # help
    if messagecontent == prefix + "help":
        text = f"""
        **Member Commands**
        `{prefix}help [command]` - Displays this message
        `{prefix}prefix <new>` - Changes the command prefix
        `{prefix}bag` - Show all of your items
        `{prefix}pocket` - Show all your items from this server
        `{prefix}shop` - View the marketplace
        `{prefix}showoff <id>` - Brag about an item
        `{prefix}trade <member>` - Start a trade with another player
        `{prefix}distill <id>` - Change the adjective of your item
        `{prefix}transmute <id>` - Change the object of your item
        `{prefix}scrap <id>` - Scrap the item
        `{prefix}give <member> <id>` - Give the item to another player
        `{prefix}delete <id>` - Delete an item
        `{prefix}use <item> <collectable>` - Use a consumable item

        **Staff Commands**
        `{prefix}private` - Set your server to private
        `{prefix}public` - Set your server to public

        **Created by Zennara#8377**
        Invite the bot [here](https://discord.com/api/oauth2/authorize?client_id=929935460699082782&permissions=140929002609&scope=bot)
        """
        embed = discord.Embed(description=text, color=0x000000)
        embed.set_footer(text="<> - Required | [] - Optional")
        await message.channel.send(embed=embed)

    # help for each command
    elif messagecontent.startswith(prefix + "help"):
        commands = ["help", "prefix", "bag", "pocket", "shop", "trade", "distill", "transmute", "scrap", "give",
                    "delete", "private", "public", "showoff", "use"]
        if messagecontent.split()[1] in commands:
            cmd = commands.index(messagecontent.split()[1])
            if cmd == 0:
                text = f"""
            This shows a page with all of the available commands. Anything wrapped in `<` and `>` are **required** arguments, while anything wrapped in `[` and `]` are **optional** arguments. An argument is a value you put into the command like information, a member, or an ID. You can find more help in my [discord server](https://discord.gg/y5FJsThMsc).
            """
            elif cmd == 1:
                text = f"""
            This command will change the prefix for your server. Every server with this bot can have their own, custom prefix. {message.guild.name}'s prefix is currently `{prefix}`
            """
            elif cmd == 2:
                text = f"""
            This will show you all of the contents of your inventory across all servers. You can find your **items** and **scrap** {scrapEmoji} here. Items are seperated by server. If the server you found an item in is a public server, a hyperlink to that server will be it's name.
            """
            elif cmd == 3:
                text = f"""
            This will show you your inventory in a more simplified version. Only the items from the current server you used the command in will be shown.
            """
            elif cmd == 4:
                text = f"""
            This opens the **shop**. You can buy chests here for new items with your **scrap** {scrapEmoji}. The current price is {chestprice} {scrapEmoji}.
            """
            elif cmd == 5:
                text = f"""
            This initiates a trade with another player. If they accept, you can add and remove **items** or **scrap** {scrapEmoji} to trade. To accept a trade, react with ✅. To cancel your acceptance or to cancel the trade, react with ❌. When both player confirm the trade, the agreed upon items will be transferred.
            """
            elif cmd == 6:
                text = f"""
            This will give you a chance to get a new **adjective** for your item. Currently this costs {rerollPrice} {scrapEmoji}.
            """
            elif cmd == 7:
                text = f"""
            This will give you a chance to get a new **noun** and **emoji** for your item. Currently this costs {rerollPrice} {scrapEmoji}.
            """
            elif cmd == 8:
                text = f"""
            This will scrap the item with the `id` you inputted. A confirmation message will appear with the amount it is scrapped for. Scrap prices are determined by the **rarity** and multiplied by the **addition** (+-).
            """
            elif cmd == 9:
                text = f"""
            This will give the item matching the `id` to the designated `member`. You can use the members **mention** or **id** for the command.
            """
            elif cmd == 10:
                text = f"""
            This will delete the item matching the `id`. Warning: this **can not** be undone.
            """
            elif cmd == 11:
                text = f"""
            Set your server to `private`. This **will not allow** users from other guilds to join off items and bags. This will also delete any valid invite links created by {client.user.name}. Only usable by members with the `Manage_Guild` permission.
            """
            elif cmd == 12:
                text = f"""
            Set your server to `public`. This **will allow** users from other guilds to join off items and bags. Only usable by members with the `Manage_Guild` permission.
            """
            elif cmd == 13:
                text = f"""
            Shows off an item from the `id` and displays it in the channel along with a randomly generated message.
            """
            elif cmd == 14:
                text = f"""
            Uses an item from your consumable items list. This includes **Paintbrushes**.
            """

            # send command
            embed = discord.Embed(description=text, color=0x000000,
                                  title=commands[commands.index(messagecontent.split()[1])].capitalize())
            await message.channel.send(embed=embed)

    # private
    if messagecontent == prefix + "private":
        if checkPerms(message):
            if data[str(message.guild.id)]["join"] == True:
                embed = discord.Embed(description="🔒 Your server is now private on **" + client.user.name + "**.")
                data[str(message.guild.id)]["join"] = False
                update_data()
                for invite in await message.guild.invites():
                    if invite.inviter.id == client.user.id:
                        await invite.delete(reason="Server set to private")
                        break
            else:
                embed = discord.Embed(description="🔒 Your server is already private on **" + client.user.name + "**.",
                                      color=0x000000)
            embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
            await message.channel.send(embed=embed)

    # private
    if messagecontent == prefix + "public":
        if checkPerms(message):
            if data[str(message.guild.id)]["join"] == False:
                embed = discord.Embed(description="🔓 Your server is now public on **" + client.user.name + "**.",
                                      color=0x000000)
                data[str(message.guild.id)]["join"] = True
                update_data()
            else:
                embed = discord.Embed(description="🔓 Your server is already public on **" + client.user.name + "**.",
                                      color=0x000000)
            embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
            await message.channel.send(embed=embed)

    # view bag
    inPage = 1
    if messagecontent.startswith(prefix + "pocket") or messagecontent.startswith(prefix + "bag"):
        splits = messagecontent.split(" ", 1)
        usr = ""
        if len(splits) == 1:
            usr = message.author
        else:
            sp = splits[1].replace(">", "").replace("<", "").replace("@", "").replace("!", "")
            if sp.isnumeric():
                if message.guild.get_member(int(sp)):
                    usr = message.guild.get_member(int(sp))
                else:
                    await error(message, "Member does not exist or is not in the guild")
            else:
                await error(message, "Member must be numeric ID or mention")

        if usr != "":
            async def openBag(msg, page):
                texts = ""
                count = 0
                itemsOnPage = 0
                scrapAmount = "0"
                # check if in database
                if str(usr.id) in data["players"]:
                    scrapAmount = str(data["players"][str(usr.id)]["scrap"])
                    for guild in data["players"][str(usr.id)]:
                        if itemsOnPage >= pageSize:
                            break
                        if guild not in nonGuilds or guild == "items":
                            if data["players"][str(usr.id)][guild]:
                                if page * pageSize - (pageSize) <= count <= page * pageSize:
                                    # get invite link
                                    if guild == "items":
                                        link = "Items"
                                    else:
                                        link = data[str(guild)]["name"]
                                    try:
                                        done = False
                                        if data[str(guild)]["join"] == True:
                                            g = client.get_guild(int(guild))
                                            for invite in await g.invites():
                                                if invite.inviter.id == client.user.id:
                                                    link = "[" + g.name + "](" + invite.url + ")"
                                                    done = True
                                                    break
                                            if not done:
                                                inv = await g.text_channels[0].create_invite()
                                                link = "[" + g.name + "](" + inv.url + ")"
                                    except:
                                        pass
                                    if messagecontent.startswith(prefix + "pocket") and str(guild) == str(
                                            message.guild.id):
                                        texts = texts + "**" + link + "**\n"
                                    elif guild == "items":
                                        texts = texts + "**" + link + "**\n"
                                    elif messagecontent.startswith(prefix + "bag"):
                                        texts = texts + "**" + link + "**\n"

                                for item in data["players"][str(usr.id)][guild]:
                                    if itemsOnPage >= pageSize:
                                        break
                                    count += 1
                                    sections = item.split("|")
                                    if guild != "items" and messagecontent.startswith(prefix + "pocket"):
                                        if messagecontent.startswith(prefix + "pocket") and str(guild) != str(
                                                message.guild.id):
                                            continue
                                    if page * pageSize - (pageSize) + 1 <= count <= page * pageSize:
                                        itemsOnPage += 1
                                        if not guild == "items":
                                            texts = texts + "`" + str(count) + "` " + (
                                                    emojis[rarities.index(sections[1])] + " " + sections[
                                                0] + " **[" + sections[1] + "]** " + sections[2] + " " + sections[
                                                        3] + " " + sections[4]) + "\n"
                                        else:
                                            type = ""
                                            if sections[2] == "pba" or sections[2] == "pbn":
                                                type = "Paintbrush 🖌️"
                                            texts = texts + f"`{str(count)}` {sections[0]} {sections[1]} {type}\n"
                                if messagecontent.startswith(prefix + "bag") or (
                                        messagecontent.startswith(prefix + "pocket") and str(guild) == str(
                                    message.guild.id)):
                                    texts = texts + "\n"
                                elif guild == "items":
                                    texts = texts + "\n"
                if texts.strip() == "":
                    texts = "Your " + splits[0].replace(prefix, "") + " is awfully empty."
                # webhook = await getWebhook(message.channel)
                # add scrap
                texts = scrapEmoji + " **Scrap:** " + scrapAmount + "\n\n" + texts
                embed = discord.Embed(description=texts, color=0x000000)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/929182726203002920/930004332835930132/bag-removebg-preview_1.png")
                embed.set_author(name=usr.name + "'s " + splits[0].replace(prefix, "").capitalize(),
                                 icon_url=usr.avatar_url)
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
                            if user.id == usr.id:
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
                            await openBag(msg, page - 1)
                    elif str(reaction.emoji) == "➡️":
                        await openBag(msg, page + 1)

            embed = discord.Embed(color=0x000000, description="🎒 **Opening " + usr.name + "'s " + (
                "Bag" if messagecontent == prefix + "bag" else "Pocket") + ". . .**")
            msg = await message.channel.send(embed=embed)
            if messagecontent == prefix + "bag":
                await openBag(msg, inPage)
            else:
                await openBag(msg, inPage)

    # delete item
    if messagecontent.startswith(prefix + "delete"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 2:
                if splits[1].isnumeric():
                    id = int(splits[1])
                    if str(message.author.id) in data["players"]:
                        guild1, count1 = getItem(message.author.id, id)
                        if guild1 != False:
                            splits = data["players"][str(message.author.id)][guild1][count1 - 1].split("|")
                            if len(splits) == 5:
                                deletedItem = splits[0] + " **[" + splits[1] + "]** " + splits[2] + " " + splits[
                                    3] + " " + splits[4]
                            else:
                                type = ""
                                if splits[2] == "pba" or splits[2] == "pbn":
                                    type = "Paintbrush 🖌️"
                                deletedItem = f"{splits[0]} {splits[1]} {type}"
                            embed = discord.Embed(color=0x000000, description=deletedItem,
                                                  title="⚠️ Are you sure you want to delete?")
                            msg = await message.channel.send(embed=embed)
                            done = False

                            def checkR(reaction, user):
                                if not user.bot and user.id == message.author.id:
                                    if str(reaction.emoji) == "✅":
                                        asyncio.create_task(reaction.message.clear_reactions())
                                        return True
                                    if reaction.message == msg:
                                        if str(reaction.emoji) == "❌":
                                            asyncio.create_task(reaction.message.clear_reactions())
                                            return True

                            user2 = ""
                            tt = False

                            await msg.add_reaction("✅")
                            await msg.add_reaction("⚫")
                            await msg.add_reaction("❌")
                            while True:
                                try:
                                    reaction, user = await client.wait_for('reaction_add', check=checkR, timeout=30)
                                except asyncio.TimeoutError:
                                    break
                                else:
                                    if str(reaction.emoji) == "✅":
                                        if reaction.message == msg:
                                            break
                                        else:
                                            done = True
                                            break
                                    if str(reaction.emoji) == "❌":
                                        done = True
                                        break
                            if not done:
                                del data["players"][str(message.author.id)][guild1][count1 - 1]
                                update_data()
                                embed = discord.Embed(description=deletedItem, color=0x000000, title="🗑️ Item deleted.")
                                await msg.edit(embed=embed)
                            else:
                                asyncio.create_task(msg.clear_reactions())
                                embed = discord.Embed(description="✅ Deletion cancelled.", color=0x000000)
                                await msg.edit(embed=embed)
                        else:
                            await error(message, "Item does not exist.")
                    else:
                        await error(message, "You do not have any items.")
                else:
                    await error(message, "ID must be numeric.")
            else:
                await error(message, "Please specify the item ID.")
        else:
            await error(message, f"Current active trade [here]({trading()})")

    # give item
    if messagecontent.startswith(prefix + "give"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 3:
                if splits[2].isnumeric():
                    mbr = splits[1].replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                    if mbr.isnumeric():
                        if message.guild.get_member(int(mbr)):
                            mbr = message.guild.get_member(int(mbr))
                            if mbr.id != message.author.id:
                                guild1, count1 = getItem(message.author.id, int(splits[2]))
                                if str(message.author.id) in data["players"]:
                                    if guild1 != False:
                                        item = data["players"][str(message.author.id)][guild1][count1 - 1]
                                        del data["players"][str(message.author.id)][guild1][count1 - 1]
                                        if str(mbr.id) not in data["players"]:
                                            data["players"][str(mbr.id)] = {"scrap": 0, "trading": "", "items": [],
                                                                            "shows": {}}
                                        if guild1 not in data["players"][str(mbr.id)]:
                                            data["players"][str(mbr.id)][guild1] = []
                                        data["players"][str(mbr.id)][guild1].append(item)
                                        update_data()
                                        splits = item.split("|")
                                        if len(splits) == 5:
                                            item = splits[0] + " **[" + splits[1] + "]** " + splits[2] + " " + splits[
                                                3] + " " + splits[4]
                                            color = colors[rarities.index(splits[1])]
                                        else:
                                            type = ""
                                            if splits[2] == "pba" or splits[2] == "pbn":
                                                type = "Paintbrush 🖌️"
                                            item = f"{splits[0]} {splits[1]} {type}"
                                            color = 0x000000
                                        embed = discord.Embed(description="\n" + item + "\n", color=color)
                                        embed.set_author(name=message.author.name + " sent",
                                                         icon_url=message.author.avatar_url)
                                        embed.set_footer(text="to " + mbr.name, icon_url=mbr.avatar_url)
                                        await message.channel.send(embed=embed)
                                    else:
                                        await error(message, "Item does not exist.")
                                else:
                                    await error(message, "You have no items to give.")
                            else:
                                await error(message, "You can not give items to yourself.")
                        else:
                            await error(message, "Member not in the guild.")
                    else:
                        await error(message, "Member must be ID or mention.")
                else:
                    await error(message, "Item ID must be numeric.")
            else:
                await error(message, "Please specify the item ID and player mention.")
        else:
            await error(message, f"Current active trade [here]({trading()})")

    # use an item
    if messagecontent.startswith(prefix + "use"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 3:
                if splits[1].isnumeric() and splits[2].isnumeric():
                    guild1, count1 = getItem(message.author.id, int(splits[1]))
                    guild2, count2 = getItem(message.author.id, int(splits[2]))
                    if guild1 != False:
                        if guild1 == "items":
                            if guild2 != False:
                                if guild2 != "items":
                                    consumable = data["players"][str(message.author.id)]["items"][count1 - 1].split("|")
                                    usableItems = ["pba", "pbn"]
                                    if consumable[2] in usableItems:
                                        itm = data["players"][str(message.author.id)][guild2][count2 - 1].split("|")
                                        rarity = itm[1]
                                        noun = itm[3]
                                        emoji = itm[0]
                                        adj = itm[2]
                                        addition = itm[4]
                                        color = colors[rarities.index(rarity)]
                                        if consumable[2] == "pba":
                                            adj = consumable[1]
                                        elif consumable[2] == "pbn":
                                            emoji = consumable[0]
                                            noun = consumable[1]
                                        newItemDisplay = f"{emoji} **{rarity}** {adj} {noun} {addition}"
                                        newItemLog = f"{emoji}|{rarity}|{adj}|{noun}|{addition}"
                                        embed = discord.Embed(title="🖌️ Paintbrush Used",
                                                              description=f"{newItemDisplay}", color=color)
                                        await message.channel.send(embed=embed)
                                        del data["players"][str(message.author.id)]["items"][count1 - 1]
                                        data["players"][str(message.author.id)][guild2][count2 - 1] = newItemLog
                                        update_data()
                                    else:
                                        await error(message, "This item can not be used")
                                else:
                                    await error(message, "You can not use an item on another item")
                            else:
                                await error(message, "Item to use on does not exist")
                        else:
                            await error(message, "You can not use a collectable")
                    else:
                        await error(message, "Item to use does not exist")
                else:
                    await error(message, "Item `ID`s must be numeric")
            else:
                await error(message, "Please enter the `ID` of the item you want to use")
        else:
            await error(message, f"Current active trade [here]({trading()})")

    # pay scrap
    if messagecontent.startswith(prefix + "pay"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 3:
                splits[1] = splits[1].replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                if splits[1].isnumeric():
                    if message.guild.get_member(int(splits[1])):
                        mbr = message.guild.get_member(int(splits[1]))
                        if mbr.id != message.author.id:
                            if splits[2].isnumeric():
                                amount = int(splits[2])
                                if amount > 0:
                                    if str(message.author.id) in data["players"]:
                                        scrap = data["players"][str(message.author.id)]["scrap"]
                                        if scrap >= amount:
                                            if splits[1] not in data["players"]:
                                                data["players"][str(mbr.id)] = {"scrap": 0, "trading": "", "items": [],
                                                                                "shows": {}}
                                            # gave amount to user
                                            data["players"][str(mbr.id)]["scrap"] = data["players"][str(mbr.id)][
                                                                                        "scrap"] + amount
                                            # subtract amount
                                            data["players"][str(message.author.id)]["scrap"] = scrap - amount
                                            update_data()
                                            # confirmation message
                                            embed = discord.Embed(color=0x000000, description="gave **" + str(
                                                amount) + "** " + scrapEmoji + " to:")
                                            embed.set_author(name=message.author.name,
                                                             icon_url=message.author.avatar_url)
                                            embed.set_footer(text=mbr.name, icon_url=mbr.avatar_url)
                                            await message.channel.send(embed=embed)
                                        else:
                                            await error(message, "You only have " + str(scrap) + scrapEmoji)
                                    else:
                                        await error(message, "You do not have any scrap.")
                                else:
                                    await error(message, "Please enter an amount above `0`")
                            else:
                                await error(message, "Scrap amount should be numeric")
                        else:
                            await error(message, "You can not pay yourself.")
                    else:
                        await error(message, "Invalid player mention or ID")
                else:
                    await error(message, "Player should be mention or their ID")
            else:
                await error(message, "Please input the amount to pay and the member mention.")
        else:
            await error(message, f"Current active trade [here]({trading()})")

    # scrap item
    if messagecontent.startswith(prefix + "scrap"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 2:
                if splits[1].isnumeric():
                    if str(message.author.id) in data["players"]:
                        guild1, count1 = getItem(message.author.id, int(splits[1]))
                        if guild1 != False:
                            splits = data["players"][str(message.author.id)][guild1][count1 - 1].split("|")

                            if len(splits) != 3:
                                scrapItem = emojis[rarities.index(splits[1])] + " " + splits[0] + " **[" + splits[
                                    1] + "]** " + splits[2] + " " + splits[3] + " " + splits[4]
                                scrapAmount = int(scrapAmounts[rarities.index(splits[1])] * multipliers[
                                    int(splits[4].replace("+", ""))])
                            else:
                                type = ""
                                print(splits[2])
                                if splits[2] == "pba" or splits[2] == "pbn":
                                    # LEFTOFF
                                    type = "Paintbrush 🖌️"
                                scrapItem = f"{splits[0]} {splits[1]} {type}"
                                scrapAmount = int(brushPrice / 4)

                            embed = discord.Embed(color=0xff0000, description=scrapItem,
                                                  title="⚠️ Are you sure you want to **scrap** this item for " + str(
                                                      scrapAmount) + scrapEmoji + "?")
                            msg = await message.channel.send(embed=embed)
                            done = False

                            def checkR(reaction, user):
                                if not user.bot and user.id == message.author.id:
                                    if str(reaction.emoji) == "✅":
                                        asyncio.create_task(reaction.message.clear_reactions())
                                        return True
                                    if reaction.message == msg:
                                        if str(reaction.emoji) == "❌":
                                            asyncio.create_task(reaction.message.clear_reactions())
                                            return True

                            await msg.add_reaction("✅")
                            await msg.add_reaction("⚫")
                            await msg.add_reaction("❌")
                            while True:
                                try:
                                    reaction, user = await client.wait_for('reaction_add', check=checkR, timeout=30)
                                except asyncio.TimeoutError:
                                    break
                                else:
                                    if str(reaction.emoji) == "✅":
                                        if reaction.message == msg:
                                            break
                                        else:
                                            done = True
                                            break
                                    if str(reaction.emoji) == "❌":
                                        done = True
                                        break
                            if not done:
                                del data["players"][str(message.author.id)][guild1][count1 - 1]
                                data["players"][str(message.author.id)]["scrap"] += scrapAmount
                                update_data()
                                embed = discord.Embed(description=scrapItem, color=0x000000,
                                                      title="⚙️ Item was scrapped for " + str(scrapAmount) + scrapEmoji)
                                await msg.edit(embed=embed)
                            else:
                                asyncio.create_task(msg.clear_reactions())
                                embed = discord.Embed(description="❌ Scrap cancelled.", color=0x000000)
                                await msg.edit(embed=embed)
                        else:
                            await error(message, "You have no items to scrap.")
                    else:
                        await error(message, "Item does not exist.")
                else:
                    await error(message, "Item ID must be numeric.")
            else:
                await error(message, "Please specify the item ID.")
        else:
            await error(message, f"Current active trade [here]({trading()})")

    # reroll
    if messagecontent.startswith(prefix + "distill") or messagecontent.startswith(prefix + "transmute"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 2:
                if splits[1].isnumeric():
                    guild1, count1 = getItem(message.author.id, int(splits[1]))
                    if guild1 != False:
                        if guild1 != "items":
                            if splits[0] == prefix + "distill" or splits[0] == prefix + "transmute":
                                scrap = data["players"][str(message.author.id)]["scrap"]
                                if scrap >= rerollPrice:
                                    data["players"][str(message.author.id)]["scrap"] = scrap - rerollPrice
                                    item = ""
                                    emoji = ""
                                    splitItem = data["players"][str(message.author.id)][guild1][count1 - 1].split("|")
                                    adj = splitItem[2]
                                    item = splitItem[3]
                                    emoji = splitItem[0]
                                    if splits[0] == prefix + "distill":
                                        adj = adjectives[random.randint(0, len(adjectives) - 1)]
                                        if random.randint(1, 5) == 1:
                                            adj = adj + " " + adjectives[random.randint(0, len(adjectives) - 1)]
                                    elif splits[0] == prefix + "transmute":
                                        item = ""
                                        emoji = ""
                                        itm = items[random.randint(0, len(items) - 1)]
                                        for i in itm:
                                            if i.isalpha() or i == " ":
                                                item = item + i
                                            else:
                                                emoji = emoji + i
                                    rarity = splitItem[1]
                                    color = colors[rarities.index(rarity)]
                                    addition = splitItem[4]
                                    desc = emoji + " **[" + rarity + "]** " + adj + " " + item + " " + addition
                                    fullItem = emoji + "|" + rarity + "|" + adj + "|" + item + "|" + addition
                                    data["players"][str(message.author.id)][guild1].insert(count1 - 1, fullItem)
                                    data["players"][str(message.author.id)][guild1].pop(count1)
                                    update_data()
                                    embed = discord.Embed(description=desc, title="Item " + ("Distilled" if splits[
                                                                                                                0] == prefix + "distill" else "Transmuted") + " for " + str(
                                        rerollPrice) + " " + scrapEmoji, color=color)
                                    await message.channel.send(embed=embed)
                                else:
                                    await error(message, "You only have **" + str(scrap) + "** " + scrapEmoji)
                            else:
                                await error(message, "Reroll type needs to be `adj` or `noun`")
                        else:
                            await error(message, "You can not distill or transmute items.")
                    else:
                        await error(message, "Item does not exist")
                else:
                    await error(message, "Item ID must be numeric.")
            else:
                await error(message, "Please specify the item ID.")
        else:
            await error(message, f"Current active trade [here]({trading()})")

    # move an item in your bag
    if messagecontent.startswith(prefix + "move"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 3:
                if splits[1].isnumeric():
                    if splits[2].isnumeric():
                        if str(message.author.id) in data["players"]:
                            guild1, count1 = getItem(message.author.id, int(splits[1]))
                            if guild1 != False:
                                guild2, count2 = getItem(message.author.id, int(splits[2]))
                                if guild2 != False:
                                    if guild1 == guild2:
                                        insertItem = data["players"][str(message.author.id)][guild1][count1 - 1]
                                        data["players"][str(message.author.id)][guild1].pop(count1 - 1)
                                        data["players"][str(message.author.id)][guild1].insert(count2 - 1, insertItem)
                                        iSplit = data["players"][str(message.author.id)][guild1][count2 - 1].split("|")
                                        update_data()
                                        if len(iSplit) == 5:
                                            item1 = emojis[rarities.index(iSplit[1])] + " " + iSplit[0] + " **[" + \
                                                    iSplit[1] + "]** " + iSplit[2] + " " + iSplit[3] + " " + iSplit[4]
                                            color = colors[rarities.index(iSplit[1])]
                                        else:
                                            type = ""
                                            if iSplit[2] == "pba" or iSplit[2] == "pbn":
                                                type1 = "Paintbrush 🖌️"
                                            item1 = f"{iSplit[0]} {iSplit[1]} {type1}"
                                            color = 0x000000
                                        embed = discord.Embed(color=color, title="🚚 **Moved**",
                                                              description=item1 + "\n`" + splits[1] + "` ➡️ `" + splits[
                                                                  2] + "`")
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
        else:
            await error(message, f"Current active trade [here]({trading()})")

    # swap two items in your bag
    if messagecontent.startswith(prefix + "swap"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 3:
                if splits[1].isnumeric():
                    if splits[2].isnumeric():
                        if str(message.author.id) in data["players"]:
                            guild1, count1 = getItem(message.author.id, int(splits[1]))
                            if guild1 != False:
                                guild2, count2 = getItem(message.author.id, int(splits[2]))
                                if guild2 != False:
                                    if guild1 == guild2:
                                        item1 = data["players"][str(message.author.id)][guild1][count1 - 1].split("|")
                                        item2 = data["players"][str(message.author.id)][guild2][count2 - 1].split("|")
                                        if len(item1) == 5:
                                            item1 = "`" + splits[1] + "` " + emojis[rarities.index(item1[1])] + item1[
                                                0] + " **[" + item1[1] + "]** " + item1[2] + " " + item1[3] + " " + \
                                                    item1[4]
                                            item2 = "`" + splits[2] + "` " + emojis[rarities.index(item2[1])] + item2[
                                                0] + " **[" + item2[1] + "]** " + item2[2] + " " + item2[3] + " " + \
                                                    item2[4]
                                        else:
                                            type = ""
                                            if item1[2] == "pba" or item1[2] == "pbn":
                                                type1 = "Paintbrush 🖌️"
                                            if item2[2] == "pba" or item2[2] == "pbn":
                                                type2 = "Paintbrush 🖌️"
                                            item1 = f"{item1[0]} {item1[1]} {type1}"
                                            item2 = f"{item2[0]} {item2[1]} {type2}"
                                        data["players"][str(message.author.id)][guild1][count1 - 1], \
                                            data["players"][str(message.author.id)][guild2][count2 - 1] = \
                                            data["players"][str(message.author.id)][guild2][count2 - 1], \
                                                data["players"][str(message.author.id)][guild1][count1 - 1]
                                        update_data()
                                        embed = discord.Embed(color=0x000000, title="🔀 **Swapped**",
                                                              description=item1 + "\n**with**\n" + item2)
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
        else:
            await error(message, f"Current active trade [here]({trading()})")

    fixed = datetime(2022, 1, 12)
    now = datetime.now()
    delta = now - fixed
    rand = random.Random((int(delta.seconds / 3600)) + (message.author.id))

    adj = adjectives[rand.randint(0, len(adjectives) - 1)]
    if rand.randint(1, 5) == 1:
        adj = adj + " " + adjectives[rand.randint(0, len(adjectives) - 1)]
    itm = items[rand.randint(0, len(items) - 1)]
    item = ""
    emoji = ""
    for i in itm:
        if i.isalpha() or i == " ":
            item = item + i
        else:
            emoji = emoji + i

    genAdj = adj
    genN = item
    genEmoji = emoji

    # market
    if messagecontent == prefix + "shop":
        if trading() == "":
            scrap = 0
            if str(message.author.id) in data["players"]:
                scrap = data["players"][str(message.author.id)]["scrap"]
            embed2 = discord.Embed(color=0x000000, description="```\n▌      Welcome to the shop      ▐\n```")
            embed2.set_author(name="🛒 Marketplace")

            # items
            embed2.add_field(name=f"1️⃣ - 📦 Item Chest | " + str(chestprice) + " " + scrapEmoji,
                             value="A common chest containing an item.\n-----------------------------------------",
                             inline=False)
            embed2.add_field(name=f"2️⃣ - {genEmoji} {genN} Paintbrush | " + str(brushPrice) + " " + scrapEmoji,
                             value=f"Change the noun of your item to {genN}", inline=False)
            embed2.add_field(name=f"3️⃣ - 🖌️ {genAdj} Paintbrush | " + str(brushPrice) + " " + scrapEmoji,
                             value=f"Change the adjective of your item to {genAdj}", inline=False)

            embed2.set_footer(text="Scrap: " + str(scrap) + scrapEmoji, icon_url=message.author.avatar_url)
            msg = await message.channel.send(embed=embed2)

            numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            shopAmount = ["1️⃣", "2️⃣", "3️⃣"]

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
                shopItems.append(" ".join(msg.embeds[0].fields[x].name.split()[1:-3]))
                prices.append(" ".join(msg.embeds[0].fields[x].name.split()[-2:]))
                await msg.add_reaction(numbers[x])

            while True:
                try:
                    reaction, user = await client.wait_for('reaction_add', check=checkR, timeout=30)
                except asyncio.TimeoutError:
                    embed = discord.Embed(description="Looks like the shopkeeper got tired of waiting...",
                                          color=0xFF0000)
                    await msg.edit(embed=embed)
                    await msg.clear_reactions()
                    break
                else:
                    if str(reaction.emoji) in shopAmount:
                        if trading() == "":
                            boughtItem = shopItems[numbers.index(str(reaction.emoji))]
                            price = prices[numbers.index(str(reaction.emoji))]
                            print(price)
                            if scrap >= int(price[:-2]):
                                data["players"][str(message.author.id)]["scrap"] = scrap - int(price[:-2])
                                # find user in data
                                if str(message.author.id) not in data["players"]:
                                    data["players"][str(message.author.id)] = {"scrap": 0, "trading": "", "items": [],
                                                                               "shows": {}}
                                if str(message.guild.id) not in data["players"][str(message.author.id)]:
                                    data["players"][str(message.author.id)][str(message.guild.id)] = []

                                if str(reaction.emoji) == "1️⃣":
                                    desc, color, fullItem = openChest()
                                    # give item
                                    data["players"][str(message.author.id)][str(message.guild.id)].append(fullItem)
                                    embed = discord.Embed(
                                        description="You bought a **" + boughtItem + "** for " + price + "\n" + desc,
                                        color=color)

                                elif str(reaction.emoji) == "2️⃣":
                                    it = f"{genEmoji}|{genN}|pbn"
                                    data["players"][str(message.author.id)]["items"].append(it)
                                    embed = discord.Embed(
                                        description="You bought a **" + boughtItem + "** for " + price, color=0x000000)

                                elif str(reaction.emoji) == "3️⃣":
                                    it = f"null|{genAdj}|pba"
                                    data["players"][str(message.author.id)]["items"].append(it)
                                    embed = discord.Embed(
                                        description="You bought a **" + boughtItem + "** for " + price, color=0x000000)

                                update_data()

                                scrap = data["players"][str(message.author.id)]["scrap"]
                                await message.channel.send(embed=embed)
                                embed2.set_footer(text="Scrap: " + str(scrap) + scrapEmoji,
                                                  icon_url=message.author.avatar_url)
                                await msg.edit(embed=embed2)
                            else:
                                await error(message, "You only have " + str(scrap) + scrapEmoji)

                        else:
                            await error(message, f"Current active trade [here]({trading()})")
                    if str(reaction.emoji) == "❌":
                        embed = discord.Embed(description="You left the shop.", color=0xFF0000)
                        await msg.edit(embed=embed)
                        break
        else:
            await error(message, f"Current active trade [here]({trading()})")

    # trade command
    traderTrades = []
    tradeeTrades = []
    displayedTrader = []
    displayedTradee = []
    scrapTrader = ["0"]
    scrapTradee = ["0"]
    if messagecontent.startswith(prefix + "trade"):
        if trading() == "":
            splits = messagecontent.split()
            if len(splits) == 2:
                splits[1] = splits[1].replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                if splits[1].isnumeric():
                    if message.guild.get_member(int(splits[1])):
                        tradee = message.guild.get_member(int(splits[1]))
                        if tradee.id != message.author.id:
                            embed = discord.Embed(description="with " + message.author.mention,
                                                  title="🤝 Do you want to trade?", color=0x000000)
                            msg = await message.channel.send(embed=embed)

                            await msg.add_reaction("✅")
                            await msg.add_reaction("⚫")
                            await msg.add_reaction("❌")

                            def checkRe(reaction, user):
                                if not user.bot:
                                    if reaction.message == msg:
                                        asyncio.create_task(reaction.remove(user))
                                        if str(reaction.emoji) in ["✅", "❌"]:
                                            if user.id == tradee.id:
                                                return True

                            try:
                                r, u = await client.wait_for('reaction_add', check=checkRe, timeout=60)
                            except asyncio.TimeoutError:
                                embed = discord.Embed(description="⌛ **Trade Request Expired**")
                                await msg.edit(embed=embed)
                                await msg.clear_reactions()
                            else:
                                await msg.clear_reactions()
                                if str(r.emoji) == "✅":
                                    if str(tradee.id) not in data["players"]:
                                        data["players"][str(tradee.id)] = {"scrap": 0, "trading": "", "items": [],
                                                                           "shows": {}}
                                    if str(message.author.id) not in data["players"]:
                                        data["players"][str(message.author.id)] = {"scrap": 0, "trading": "",
                                                                                   "items": [],
                                                                                   "shows": {}}
                                    if trading() == "" and data["players"][str(tradee.id)]["trading"] == "":
                                        data["players"][str(tradee.id)]["trading"] = msg.jump_url
                                        data["players"][str(message.author.id)]["trading"] = msg.jump_url
                                        embed = discord.Embed(description="\n".join(displayedTrader) + "\n" + "".join(
                                            scrapTrader) + scrapEmoji + "\n▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃\n" + "".join(
                                            scrapTradee) + scrapEmoji + "\n" + "\n".join(displayedTradee))
                                        update_data()
                                        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                                        embed.set_footer(text=tradee.name, icon_url=tradee.avatar_url)
                                        embed.set_thumbnail(
                                            url="https://cdn.discordapp.com/attachments/929182726203002920/930381037589135390/trading.png")
                                        await msg.edit(embed=embed)
                                        await msg.add_reaction("⏫")
                                        await msg.add_reaction("✅")
                                        await msg.add_reaction("⚫")
                                        await msg.add_reaction("❌")
                                        await msg.add_reaction("⏬")
                                        done = False
                                        traderAgree = False
                                        tradeeAgree = False

                                        def checkR(reaction, user):
                                            if not user.bot:
                                                if reaction.message == msg:
                                                    asyncio.create_task(reaction.remove(user))
                                                    if str(reaction.emoji) in ["⏫", "⏬", "✅", "❌"]:
                                                        if user.id == message.author.id or user.id == tradee.id:
                                                            return True

                                        user2 = ""
                                        tt = False

                                        while True:
                                            try:
                                                reaction, user = await client.wait_for('reaction_add', check=checkR,
                                                                                       timeout=45)
                                            except asyncio.TimeoutError:
                                                data["players"][str(tradee.id)]["trading"] = ""
                                                data["players"][str(message.author.id)]["trading"] = ""
                                                update_data()
                                                tt = True
                                                break
                                            else:
                                                embed2 = discord.Embed(
                                                    description="\n".join(displayedTrader) + "\n" + "".join(
                                                        scrapTrader) + scrapEmoji + "\n▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃\n" + "".join(
                                                        scrapTradee) + scrapEmoji + "\n" + "\n".join(displayedTradee))
                                                embed2.set_author(name=message.author.name + (
                                                    " -- [✅ Agreed]" if traderAgree else ""),
                                                                  icon_url=message.author.avatar_url)
                                                embed2.set_footer(
                                                    text=tradee.name + (" -- [✅ Agreed]" if tradeeAgree else ""),
                                                    icon_url=tradee.avatar_url)
                                                embed2.set_thumbnail(
                                                    url="https://cdn.discordapp.com/attachments/929182726203002920/930381037589135390/trading.png")

                                                reactor = user

                                                def check2(m):
                                                    error = ""
                                                    if not m.author.bot:
                                                        if m.author.id == reactor.id:
                                                            scrap = data["players"][str(m.author.id)]["scrap"]
                                                            if m.content.isnumeric():
                                                                guild1, count1 = getItem(m.author.id, int(m.content))
                                                                if guild1 != False:
                                                                    i = guild1 + "|" + str(count1)
                                                                    splits = data["players"][str(m.author.id)][guild1][
                                                                        count1 - 1].split("|")
                                                                    if len(splits) == 5:
                                                                        addItem = "`" + m.content + "` " + emojis[
                                                                            rarities.index(splits[1])] + " " + splits[
                                                                                      0] + " **[" + splits[1] + "]** " + \
                                                                                  splits[2] + " " + splits[3] + " " + \
                                                                                  splits[4]
                                                                    else:
                                                                        type = ""
                                                                        if splits[2] == "pba" or splits[2] == "pbn":
                                                                            type = "Paintbrush 🖌️"
                                                                        addItem = f"{splits[0]} {splits[1]} {type}"
                                                                    if m.author.id == message.author.id:
                                                                        if guild1 + "|" + str(
                                                                                count1) not in traderTrades:
                                                                            traderTrades.append(i)
                                                                            displayedTrader.append(addItem)
                                                                            asyncio.create_task(m.delete())
                                                                            return True
                                                                        else:
                                                                            error = "Item already in trade"
                                                                    elif m.author.id == tradee.id:
                                                                        if guild1 + "|" + str(
                                                                                count1) not in tradeeTrades:
                                                                            tradeeTrades.append(i)
                                                                            displayedTradee.append(addItem)
                                                                            asyncio.create_task(m.delete())
                                                                            return True
                                                                        else:
                                                                            error = "Item already in trade"
                                                                else:
                                                                    error = "Item does not exist"
                                                            elif m.content.startswith("scrap"):
                                                                if m.content[5:].isnumeric():
                                                                    if scrap >= int(m.content[5:]):
                                                                        if m.author.id == message.author.id:
                                                                            prev = int(scrapTrader[0])
                                                                            scrapTrader.pop(0)
                                                                            scrapTrader.append(
                                                                                str(prev + int(m.content[5:])))
                                                                        elif m.author.id == tradee.id:
                                                                            prev = int(scrapTradee[0])
                                                                            scrapTradee.pop(0)
                                                                            scrapTradee.append(
                                                                                str(prev + int(m.content[5:])))
                                                                        asyncio.create_task(m.delete())
                                                                        return True
                                                                    else:
                                                                        error = "You do not have enough scrap."
                                                                else:
                                                                    error = "Scrap amount must be numeric"
                                                            else:
                                                                error = "Invalid ID or scrap"
                                                            embed = discord.Embed(
                                                                description="Enter the `ID` of the item you want to add.\nOr, type `scrap` followed by the amount.\n**" + error + "**")
                                                            asyncio.create_task(m2.edit(embed=embed))
                                                            asyncio.create_task(m.delete())

                                                def check(m):
                                                    if not m.author.bot:
                                                        if m.author.id == reactor.id:
                                                            if m.content.isnumeric():
                                                                guild1, count1 = getItem(m.author.id, int(m.content))
                                                                if guild1 != False:
                                                                    i = guild1 + "|" + str(count1)
                                                                    splits = data["players"][str(m.author.id)][guild1][
                                                                        count1 - 1].split("|")
                                                                    if len(splits) == 5:
                                                                        addItem = "`" + m.content + "` " + emojis[
                                                                            rarities.index(splits[1])] + " " + splits[
                                                                                      0] + " **[" + splits[1] + "]** " + \
                                                                                  splits[2] + " " + splits[3] + " " + \
                                                                                  splits[4]
                                                                    else:
                                                                        type = ""
                                                                        if splits[2] == "pba" or splits[2] == "pbn":
                                                                            type = "Paintbrush 🖌️"
                                                                        addItem = f"{splits[0]} {splits[1]} {type}"
                                                                    if m.author.id == message.author.id:
                                                                        if guild1 + "|" + str(count1) in traderTrades:
                                                                            traderTrades.remove(i)
                                                                            displayedTrader.remove(addItem)
                                                                            asyncio.create_task(m.delete())
                                                                            return True
                                                                        else:
                                                                            error = "Item not in trade"
                                                                    elif m.author.id == tradee.id:
                                                                        if guild1 + "|" + str(count1) in tradeeTrades:
                                                                            tradeeTrades.remove(i)
                                                                            displayedTradee.remove(addItem)
                                                                            asyncio.create_task(m.delete())
                                                                            return True
                                                                        else:
                                                                            error = "Item not in trade"
                                                            elif m.content.startswith("scrap"):
                                                                if m.content[5:].isnumeric():
                                                                    if m.author.id == message.author.id:
                                                                        if int(scrapTrader[0]) >= int(m.content[5:]):
                                                                            prev = int(scrapTrader[0])
                                                                            scrapTrader.pop(0)
                                                                            scrapTrader.append(
                                                                                str(prev - int(m.content[5:])))
                                                                            asyncio.create_task(m.delete())
                                                                            return True
                                                                        else:
                                                                            error = "Not enough scrap in trade"
                                                                    elif m.author.id == tradee.id:
                                                                        if int(scrapTradee[0]) >= int(m.content[5:]):
                                                                            prev = int(scrapTradee[0])
                                                                            scrapTradee.pop(0)
                                                                            scrapTradee.append(
                                                                                str(prev - int(m.content[5:])))
                                                                            asyncio.create_task(m.delete())
                                                                            return True
                                                                        else:
                                                                            error = "Not enough scrap in trade"
                                                                else:
                                                                    error = "Scrap amount must be numeric"
                                                            else:
                                                                error = "Invalid ID or scrap"
                                                            embed = discord.Embed(
                                                                description="Enter the `ID` of the item you want to remove.\nOr, type `scrap` followed by the amount.\n**" + error + "**")
                                                            asyncio.create_task(m2.edit(embed=embed))
                                                            asyncio.create_task(m.delete())

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

                                                # add item
                                                elif str(reaction.emoji) == "⏫" and str(user.id) in data["players"]:
                                                    traderAgree = False
                                                    tradeeAgree = False
                                                    embed = discord.Embed(
                                                        description="Enter the `ID` of the item you want to add.\nOr, type `scrap` followed by the amount.")
                                                    m2 = await message.channel.send(embed=embed)
                                                    embed2.set_thumbnail(
                                                        url="https://cdn.discordapp.com/attachments/929182726203002920/930749285463650354/pause.png")
                                                    await msg.edit(embed=embed2)
                                                    try:
                                                        await client.wait_for('message', check=check2, timeout=10)
                                                    except asyncio.TimeoutError:
                                                        pass

                                                    await m2.delete()

                                                # remove item
                                                elif str(reaction.emoji) == "⏬" and str(user.id) in data["players"]:
                                                    traderAgree = False
                                                    tradeeAgree = False
                                                    embed = discord.Embed(
                                                        description="Enter the `ID` of the item you want to remove.\nOr, type `scrap` followed by the amount.")
                                                    m2 = await message.channel.send(embed=embed)
                                                    embed2.set_thumbnail(
                                                        url="https://cdn.discordapp.com/attachments/929182726203002920/930749285463650354/pause.png")
                                                    await msg.edit(embed=embed2)
                                                    try:
                                                        await client.wait_for('message', check=check, timeout=10)
                                                    except asyncio.TimeoutError:
                                                        pass

                                                    await m2.delete()

                                                embed2 = discord.Embed(
                                                    description="\n".join(displayedTrader) + "\n" + "".join(
                                                        scrapTrader) + scrapEmoji + "\n▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃\n" + scrapEmoji.join(
                                                        scrapTradee) + scrapEmoji + "\n" + "\n".join(displayedTradee))
                                                embed2.set_author(name=message.author.name + (
                                                    " -- [✅ Agreed]" if traderAgree else ""),
                                                                  icon_url=message.author.avatar_url)
                                                embed2.set_footer(
                                                    text=tradee.name + (" -- [✅ Agreed]" if tradeeAgree else ""),
                                                    icon_url=tradee.avatar_url)
                                                embed2.set_thumbnail(
                                                    url="https://cdn.discordapp.com/attachments/929182726203002920/930381037589135390/trading.png")
                                                await msg.edit(embed=embed2)

                                                if traderAgree and tradeeAgree:
                                                    done = True
                                                    break
                                        if done:
                                            await msg.clear_reactions()
                                            embed = discord.Embed(
                                                description="\n".join(displayedTrader) + "\n" + "".join(
                                                    scrapTrader) + scrapEmoji + "\n▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃\n" + "".join(
                                                    scrapTradee) + scrapEmoji + "\n" + "\n".join(displayedTradee))
                                            embed.set_author(
                                                name=message.author.name + (" -- [✅ Confirmed]" if traderAgree else ""),
                                                icon_url=message.author.avatar_url)
                                            embed.set_footer(
                                                text=tradee.name + (" -- [✅ Confirmed]" if tradeeAgree else ""),
                                                icon_url=tradee.avatar_url)
                                            embed.set_thumbnail(
                                                url="https://cdn.discordapp.com/attachments/929182726203002920/930380635300823060/temp-removebg-preview.png")
                                            await msg.edit(embed=embed)

                                            if str(tradee.id) not in data["players"]:
                                                data["players"][str(tradee.id)] = {"scrap": 0, "trading": "",
                                                                                   "items": [],
                                                                                   "shows": {}}
                                            if str(message.author.id) not in data["players"]:
                                                data["players"][str(message.author.id)] = {"scrap": 0, "trading": "",
                                                                                           "items": [], "shows": {}}

                                            update_data()

                                            for x in traderTrades:
                                                gi = x.split("|")
                                                other = data["players"][str(message.author.id)][gi[0]]
                                                if gi[0] not in data["players"][str(tradee.id)]:
                                                    data["players"][str(tradee.id)][gi[0]] = []
                                                data["players"][str(tradee.id)][gi[0]].append(other[int(gi[1]) - 1])
                                                data["players"][str(message.author.id)][gi[0]].remove(
                                                    other[int(gi[1]) - 1])

                                                update_data()

                                            for x in tradeeTrades:
                                                gi = x.split("|")
                                                other = data["players"][str(tradee.id)][gi[0]]
                                                if gi[0] not in data["players"][str(message.author.id)]:
                                                    data["players"][str(message.author.id)][gi[0]] = []
                                                data["players"][str(message.author.id)][gi[0]].append(
                                                    other[int(gi[1]) - 1])
                                                data["players"][str(tradee.id)][gi[0]].remove(other[int(gi[1]) - 1])

                                            if scrapTrader[0] != "0":
                                                data["players"][str(tradee.id)]["scrap"] = \
                                                    data["players"][str(tradee.id)][
                                                        "scrap"] + int(
                                                        scrapTrader[0])
                                                data["players"][str(message.author.id)]["scrap"] = \
                                                    data["players"][str(message.author.id)]["scrap"] - int(
                                                        scrapTrader[0])

                                            if scrapTradee[0] != "0":
                                                data["players"][str(tradee.id)]["scrap"] = \
                                                    data["players"][str(tradee.id)][
                                                        "scrap"] - int(
                                                        scrapTradee[0])
                                                data["players"][str(message.author.id)]["scrap"] = \
                                                    data["players"][str(message.author.id)]["scrap"] + int(
                                                        scrapTradee[0])

                                            data["players"][str(tradee.id)]["trading"] = ""
                                            data["players"][str(message.author.id)]["trading"] = ""

                                            update_data()

                                        else:
                                            await msg.clear_reactions()
                                            if tt:
                                                embed = discord.Embed(
                                                    description="\n".join(displayedTrader) + "\n" + "".join(
                                                        scrapTrader) + scrapEmoji + "\n▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃\n" + "".join(
                                                        scrapTradee) + scrapEmoji + "\n" + "\n".join(displayedTradee))
                                                embed.set_author(name=message.author.name + " -- [🚫 Timed Out]",
                                                                 icon_url=message.author.avatar_url)
                                                embed.set_footer(text=tradee.name + " -- [🚫 Timed Out]",
                                                                 icon_url=tradee.avatar_url)
                                                embed.set_thumbnail(
                                                    url="https://cdn.discordapp.com/attachments/929182726203002920/930793220760285245/hourglass.png")
                                            else:
                                                embed = discord.Embed(
                                                    description="\n".join(displayedTrader) + "\n" + "".join(
                                                        scrapTrader) + scrapEmoji + "\n▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃\n" + "".join(
                                                        scrapTradee) + scrapEmoji + "\n" + "\n".join(displayedTradee))
                                                embed.set_author(name=message.author.name + (
                                                    " -- [🚫 Cancelled]" if user2.id == message.author.id else ""),
                                                                 icon_url=message.author.avatar_url)
                                                embed.set_footer(text=tradee.name + (
                                                    " -- [🚫 Cancelled]" if user2.id == tradee.id else ""),
                                                                 icon_url=tradee.avatar_url)
                                                embed.set_thumbnail(
                                                    url="https://cdn.discordapp.com/attachments/929182726203002920/930394152309510184/images-removebg-preview.png")
                                            await msg.edit(embed=embed)
                                            data["players"][str(tradee.id)]["trading"] = ""
                                            data["players"][str(message.author.id)]["trading"] = ""

                                            update_data()
                                    else:
                                        embed.set_author(name=message.author.name + (
                                            " -- [🚫 Cancelled]" if user2.id == message.author.id else ""),
                                                         icon_url=message.author.avatar_url)
                                        embed.set_footer(
                                            text=tradee.name + (" -- [🚫 Cancelled]" if user2.id == tradee.id else ""),
                                            icon_url=tradee.avatar_url)
                                        embed.set_thumbnail(
                                            url="https://cdn.discordapp.com/attachments/929182726203002920/930394152309510184/images-removebg-preview.png")
                                        await msg.edit(embed=embed)
                                        if trading() == "":
                                            await error(message,
                                                        f"{message.author.mention}, Current active trade [here]({trading()})")
                                        if data["players"][str(tradee.id)]["trading"] == "":
                                            tr = data["players"][str(tradee.id)]["trading"]
                                            await error(message, f"{tradee.mention}, Current active trade [here]({tr})")
                                else:
                                    embed = discord.Embed(description="🚫 **Trade Denied**")
                                    await msg.edit(embed=embed)
                        else:
                            await error(message, "You can not trade with yourself.")
                    else:
                        await error(message, "Member does not exist.")
                else:
                    await error(message, "Member must be mention or ID.")
            else:
                await error(message, "Please specify the member mention or ID.")
        else:
            await error(message, f"Current active trade [here]({trading()})")


@client.event
async def on_guild_join(guild):
    if str(guild.id) not in data:
        data[str(guild.id)] = {"prefix": "!", "name": guild.name, "join": False}
    update_data()


@client.event
async def on_guild_update(before, after):
    if str(before.id) not in data:
        data[str(before.id)] = {"prefix": "!", "name": after.name, "join": False}
    data[str(before.id)] = {"prefix": data[str(before.id)]["prefix"], "name": after.name, "join": False}
    update_data()


with open('data.json', encoding="utf-8") as f:
    data = json.load(f)

with open('config.json', encoding="utf-8") as f:
    config = json.load(f)

client.run(config['token'])
