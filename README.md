# RPG-Central
A Discord bot for generating, trading, and collecting items. Currently, there are over **550** items with matching emojis, and **500** unique adjectives. That is over **688,875,000** different combinations of items to collect.

## Forking / Custom Bots
I highly advise **not** to fork this code to create your own version of the bot unless you are changing many things. This bot uses a global trading system across all servers, and creating a custom bot from this code will not allow you to communicate over the global network.

## Invite the bot
You can invite this bot to your servers using the link [here](https://discord.com/api/oauth2/authorize?client_id=929935460699082782&permissions=140929002609&scope=bot). The bot requests many permissions in the event I update the bot to need more. You can always remove permissions if you'd like, but I can not guarantee everything will continue working.

## Enjoy the bot?
If you enjoy this free bot, it would mean the world to [donate](https://paypal.me/keaganlandfried). This ensures I can keep this bot and others like it online for years to come.

# Commands
## General Commands
| **Command** | **Arguments**   | **Description**                                                  | **Public?** |
|-------------|-----------------|------------------------------------------------------------------|-------------|
| `help`      | `[command]`     | Shows the help page                                              | yes         |
| `prefix`    | `<new>`         | Changes the bot prefix                                           | yes         |
| `bag`       | `[member]`      | Shows all your items from all servers                            | yes         |
| `pocket`    | `[member]`      | Shows your items for the current server                          | yes         |
| `shop`      | none            | Opens the marketplace                                            | yes         |
| `trade`     | `<member>`      | Sends a trade request with another player                        | yes         |
| `distill`   | `<id>`          | Changes the item adjective                                       | yes         |
| `transmute` | `<id>`          | Changes the item itself                                          | yes         |
| `scrap`     | `<id>`          | Scraps the item for scrap                                        | yes         |
| `give`      | `<member> <id>` | Give an item to another player                                   | yes         |
| `delete`    | `<id>`          | Delete an item permanently                                       | yes         |

## Staff Commands
|  **Command**  | **Arguments**     | **Description**                                                  | **Public?** |
|---------------|-------------------|------------------------------------------------------------------|-------------|
| `private`   | none            | Change the server to private in the bot                          | no          |
| `public`    | none            | Change the server to public in the bot                           | no          |

## Bot Owner Commands
|  **Command**  | **Arguments**     | **Description**                                                  | **Public?** |
|---------------|-------------------|------------------------------------------------------------------|-------------|
| `testgen`     | none              | Tests item generation                                            | no          |
| `gen`         | `<item>`          | Generates an item in `emoji\|rarity\|adj\|noun\|additive` format | no          |
| `chest`       | none              | Spawns a chest                                                   | no          |
