import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)



class Player:
    def __init__(self, name, mod, bonus):
        self.n: str = name
        self.m: int = mod
        self.b: str = bonus
    
    def roll(self):
        if self.b == "a" or self.b == "d":
            self.roll_roll()
        elif self.b == "antre":
            self.r = 20
        else:
            self.r = random.randint(1, 20)

    def roll_roll(self):
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        if self.b == "a":
            self.r = max(roll1, roll2)
            self.rr = min(roll1, roll2)
        else:
            self.r = min(roll1, roll2)
            self.rr = max(roll1, roll2)


test1 = Player("elfe", +5, "a")
test2 = Player("humain", +1, "")
test3 = Player("orc", -5, "d")
initiative = [test1, test2, test3]

@bot.event
async def on_ready():
    print(f"{bot.user.name} online")
    try:
        synced = await bot.tree.sync()
        print(f"{synced} commande(s) synchronisée(s)")
    except Exception as e:
        print(e)

def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def check_d(s):
    if "d" in s and s.count("d") == 1:
        test = s.replace("d", "")
        return check_int(test)
    else:
        return False

def roll_dice(dice):
    d = dice.split("d")
    if d[0] == '':
        nb_dice = 1
    else:
        nb_dice = int(d[0])
    rolls = []
    total = 0

    for i in range(nb_dice):
        roll = random.randint(1, int(d[1]))
        rolls.append(roll)
        total = total + roll

    return rolls, total

@bot.hybrid_command()
async def roll(ctx, *, msg):
    dices = msg.replace(" ", "")
    dices_split = dices.split("+")
    total = 0
    results = []

    for e in dices_split:
        if check_int(e):
            total = total + int(e)

        elif check_d(e):
            dice_rolls, total_roll = roll_dice(e)
            for i in range(len(dice_rolls)):
                results.append(dice_rolls[i])
            total = total + total_roll

        else:
            await ctx.reply(f"```ml\nERREUR COMMANDE```")
            return
    
    await ctx.reply(f"```md\n# {total}\n{dices} : {results}\n```")
    #await ctx.message.delete()


def sort_ini(p: Player):
    if p.r == 20 and p.b != "antre":
        return 100
    elif p.r == 1:
        return -100
    else:
        return p.r+p.m

def roll_initiative():
    biggest = 0
    for i in initiative:
        i.roll()
        if len(i.n)+len(str(i.r + i.m)) > biggest:
            biggest = len(i.n)+len(str(i.r + i.m))
    initiative.sort(reverse=True, key=lambda p: (sort_ini(p), p.m))
    return biggest 


@bot.hybrid_command()
async def i(ctx, *, msg):
    data = msg.split(" ")

    # check if entity is already in initiative
    for i in initiative:
        if i.n.lower() == data[0].lower():
            await ctx.reply(f"```ml\n{data[0]} EST DEJA DANS L'INITIATIVE```")
            return

    # create player and add to initiative
    try:
        if len(data) == 2:
            player = Player(data[0], int(data[1]), "")
        else:
            player = Player(data[0], int(data[1]), data[2])
        initiative.append(player)
    except:
        await ctx.reply(f'```ml\nERREURE COMMANDE : "/i {msg}"\n```')

    await ctx.reply(f"```md\n{player.n} ajouté à l'initiative\n```")

@bot.tree.command(name="roll_ini", description="roll initiative")
async def roll_ini(interaction: discord.Interaction):
    biggest = roll_initiative()
    res = ""
    for i in initiative:
        sign = ""
        outcoms = str(i.r)
        space_brake = (biggest+5-len(i.n)-len(str(i.r+i.m)))*" "
        if i.m >= 0:
            sign = "+"
        if hasattr(i, 'rr') :
            outcoms += "|" + str(i.rr)

        res += f"{i.n} : {i.r+i.m}{space_brake}{outcoms} {sign}{i.m}\n"

    await interaction.response.send_message(f"```md\n{res}```")

@bot.tree.command(name="see_ini", description="see everyone in initiative")
async def see_ini(interaction: discord.Interaction):
    res = ""
    for i in initiative:
        res += f"{i.n} : {i.m} {i.b}\n"

    await interaction.response.send_message(f"```md\n{res}```")

@bot.tree.command(name="clear_ini", description="clear the initiative")
async def clear_ini(interaction: discord.Interaction):
    initiative.clear()

    await interaction.response.send_message(f"```md\nInitiative vidée```")

@bot.hybrid_command()
async def remove_from_ini(ctx, *, msg):
    removed = False
    for i in initiative:
        if i.n.lower() == msg.lower():
            initiative.remove(i)
            removed = True
    
    if removed:
        await ctx.reply(f"```md\n{msg} à été supprimé de l'initiative\n```")
    else:
        await ctx.reply(f"```ml\n{msg} n'est pas dans l'initiative```")

@bot.tree.command(name="add_antre", description="add antre to initiative")
async def add_antre(interaction: discord.Interaction):

    # check if entity is already in initiative
    for i in initiative:
        if i.b == "antre":
            await interaction.response.send_message(f"```ml\nIL Y A DEJA UNE ANTRE DANS L'INITIATIVE```")
            return

    # create antre and add to initiative
    antre = Player("Antre", 0, "antre")
    antre.r = 20
    initiative.append(antre)
    await interaction.response.send_message(f"```md\nAntre ajoutée !```")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)

