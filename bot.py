import json
import os
import sys
import discord
import asyncio
import random
import logging
from datetime import datetime
from discord.ext import commands
from discord import app_commands


TOKEN = ""
MUTE_ROLE_ID = 1284531978284171275
LOG_CHANNEL_ID = 1269261771953147925
ALLOWED_ROLE_IDS = [
    1282416647612792963, 
    876464048592523331, 
    876464048592523333, 
    876464048592523332, 
    1267924731705950282, 
    1282416647612792963
]


logging.basicConfig(level=logging.INFO)


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
intents.message_content = True
intents.members = True
intents.messages = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)  


bot.remove_command('help')

def load_data():
    coins = load_coins()
    user_data = load_user_data()
    warns = load_warns()
    return {
        'coins': coins,
        'user_data': user_data,
        'warns': warns
    }

def save_data(data):
    save_coins(data.get('coins', {}))
    save_user_data(data.get('user_data', {}))
    save_warns(data.get('warns', {}))


COINS_FILE = 'coins.json'
USER_DATA_FILE = 'user_data.json'
WARNINGS_FILE = 'data.json'


def load_coins():
    try:
        with open(COINS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Fehler beim Lesen der Coins-Datei")
        return {}


def save_coins(data):
    with open(COINS_FILE, 'w') as file:
        json.dump(data, file, indent=4)


def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Fehler beim Lesen der Benutzerdaten-Datei")
        return {}


def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


def load_warns():
    try:
        with open(WARNINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'warns': {}}
    except json.JSONDecodeError:
        print("Fehler beim Lesen der Warnungen-Datei")
        return {'warns': {}}


def save_warns(data):
    with open(WARNINGS_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@bot.command(name='help')
async def help_command(ctx):
    
    embed_general = discord.Embed(
        title="Hilfe",
        description="Hier ist eine Übersicht der verfügbaren Befehle.",
        color=discord.Color.blue()
    )
    
    commands_list = {
        'warn': 'Warnt ein Mitglied des Servers. Beispiel: `!warn @Benutzer Grund`.',
        'unwarn': 'Hebt eine Warnung für ein Mitglied auf. Beispiel: `!unwarn @Benutzer Grund`.',
        'cases': 'Zeigt alle offenen Warnungen und Fälle für einen Benutzer an. Beispiel: `!cases @Benutzer`.',
        'mute': 'Stummschaltet ein Mitglied für eine bestimmte Dauer. Beispiel: `!mute @Benutzer 10m Grund`.',
        'ban': 'Bannt ein Mitglied vom Server. Beispiel: `!ban @Benutzer Grund`.',
        'unban': 'Hebt den Bann eines Mitglieds auf. Beispiel: `!unban BenutzerID Grund`.',
        'purge': 'Löscht eine bestimmte Anzahl von Nachrichten in einem Kanal. Beispiel: `!purge 10`.',
        'embed': 'Sendet eine benutzerdefinierte Embed-Nachricht. Beispiel: `!embed Titel | Beschreibung`.',
        'poll': 'Startet eine Umfrage. Beispiel: `!poll single 10 Frage | Option1, Option2`.',
    }

    for command, description in commands_list.items():
        embed_general.add_field(name=f'!{command}', value=description, inline=False)

    embed_general.set_footer(text="Made with ♥️ by Atzen Development")
    
    # Casino-Befehle
    embed_casino = discord.Embed(
        title="Casino Befehle",
        description="Hier sind die Casino Commands.",
        color=discord.Color.green()
    )

    casino_list = {
        'roulette': 'Man kann Roulette spielen: `!roulette <Einsatz> <Option>`.',
        'daily': 'Daily Coins abholen: `!daily`.',
        'map': 'Zeigt die Roulette Map an: `!map`.',
        'bank': 'Zeigt den Kontostand an: `!bank`.',
        'bj': 'Abfahrt Blackjack: `!bj`.',
    }

    for command, description in casino_list.items():
        embed_casino.add_field(name=f'!{command}', value=description, inline=False)

    embed_casino.set_footer(text="Made with ♥️ by Atzen Development")
    
    # Admin-Befehle
    embed_admin = discord.Embed(
        title="Admin Befehle",
        description="Diese Befehle sind nur für Administratoren zugänglich.",
        color=discord.Color.red()
    )

    admin_list = {
        'restart': 'Speichert alle Daten und startet den Bot neu. Beispiel: `!restart`.',
        'shutdown': 'Speichert alle Daten und fährt den Bot herunter. Beispiel: `!shutdown`.',
    }

    for command, description in admin_list.items():
        embed_admin.add_field(name=f'!{command}', value=description, inline=False)

    embed_admin.set_footer(text="Achtung: Nur Admins können diese Befehle ausführen!")
    
    # Send all embeds
    await ctx.send(embed=embed_general)
    await ctx.send(embed=embed_casino)
    await ctx.send(embed=embed_admin)



is_ready = False

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=876464048537993277))
    await bot.change_presence(activity=discord.Game(name='!help für Hilfe'))
    print("slash ready")
    print(f'Bot ist eingeloggt als {bot.user.name}')


async def get_audit_log_entry(guild, action, target=None):
    try:
        async for entry in guild.audit_logs(action=action):
            if target is None or entry.target == target:
                return entry
        return None
    except discord.Forbidden:
        print("Keine Berechtigung, das Audit-Log zu lesen.")
    except discord.HTTPException as e:
        print(f"Fehler beim Abrufen des Audit-Logs: {e}")


async def send_message(channel, content):
    try:
        await channel.send(content)
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = e.retry_after
            print(f"Rate Limit erreicht. Erneuter Versuch in {retry_after} Sekunden.")
            await asyncio.sleep(retry_after)
            await channel.send(content)



@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user}')
    
    for guild in bot.guilds:
        for command in bot.tree.get_commands():
            try:
                await bot.tree.delete_command(command.name, guild=guild)
            except Exception as e:
                print(f"Fehler beim Löschen des Commands: {e}")
    
    
    await bot.tree.sync()
    print("Slash-Commands wurden synchronisiert.")

@bot.tree.command(name="roleadd", description="Fügt einem Mitglied eine bestimmte Rolle hinzu.")
@app_commands.describe(member="Das Mitglied, dem die Rolle hinzugefügt werden soll.", role="Die Rolle, die hinzugefügt werden soll.")
async def roleadd(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role not in interaction.guild.roles:
        embed = discord.Embed(
            title="Fehler",
            description=f"Die Rolle `{role.name}` existiert nicht auf diesem Server.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        return

    if role in member.roles:
        embed = discord.Embed(
            title="Fehler",
            description=f"{member.mention} hat bereits die Rolle `{role.name}`.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        return

    try:
        await member.add_roles(role)
        embed = discord.Embed(
            title="Rolle hinzugefügt",
            description=f"Die Rolle `{role.name}` wurde erfolgreich zu {member.mention} hinzugefügt.",
            color=discord.Color.green()
        )
    except discord.Forbidden:
        embed = discord.Embed(
            title="Fehler",
            description="Ich habe keine Berechtigung, um diese Rolle hinzuzufügen. Stelle sicher, dass meine Rolle höher ist als die zugewiesene Rolle und dass ich über die Berechtigung verfüge, Rollen zu verwalten.",
            color=discord.Color.red()
        )
    except Exception as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Es ist ein Fehler aufgetreten: {str(e)}",
            color=discord.Color.red()
        )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roleremove", description="Entfernt eine bestimmte Rolle von einem Mitglied.")
@app_commands.describe(member="Das Mitglied, von dem die Rolle entfernt werden soll.", role="Die Rolle, die entfernt werden soll.")
async def roleremove(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role not in interaction.guild.roles:
        embed = discord.Embed(
            title="Fehler",
            description=f"Die Rolle `{role.name}` existiert nicht auf diesem Server.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        return

    if role not in member.roles:
        embed = discord.Embed(
            title="Fehler",
            description=f"{member.mention} hat die Rolle `{role.name}` nicht.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        return

    try:
        await member.remove_roles(role)
        embed = discord.Embed(
            title="Rolle entfernt",
            description=f"Die Rolle `{role.name}` wurde erfolgreich von {member.mention} entfernt.",
            color=discord.Color.green()
        )
    except discord.Forbidden:
        embed = discord.Embed(
            title="Fehler",
            description="Ich habe keine Berechtigung, um diese Rolle zu entfernen. Stelle sicher, dass meine Rolle höher ist als die zu entfernende Rolle und dass ich über die Berechtigung verfüge, Rollen zu verwalten.",
            color=discord.Color.red()
        )
    except Exception as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Es ist ein Fehler aufgetreten: {str(e)}",
            color=discord.Color.red()
        )

    await interaction.response.send_message(embed=embed)

COINS_FILE = 'coins.json'
USER_DATA_FILE = 'user_data.json'


@bot.command(name='daily')
async def daily(ctx):
    coins_data = load_coins()
    user_id = str(ctx.author.id)
    user_data = coins_data.get(user_id, {})
    user_coins = user_data.get('coins', 0)
    last_claim = user_data.get('last_claim', None)

    today = datetime.now().strftime('%Y-%m-%d')
    if last_claim != today:
        coins_awarded = random.randint(0, 500)
        user_coins += coins_awarded
        user_data['coins'] = user_coins
        user_data['last_claim'] = today
        coins_data[user_id] = user_data
        save_coins(coins_data)

        embed = discord.Embed(
            title="Tägliche Coins",
            description=f"Du hast {coins_awarded} Coins erhalten! Deine neuen Coins: {user_coins}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url="https://as1.ftcdn.net/v2/jpg/01/44/33/66/1000_F_144336685_lIKJEs8RzqhbpOwCycZTsFT0Eywxl41M.jpg")
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Tägliche Coins",
            description="Du hast deine täglichen Coins bereits heute abgeholt. Versuche es morgen erneut!",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://as1.ftcdn.net/v2/jpg/01/44/33/66/1000_F_144336685_lIKJEs8RzqhbpOwCycZTsFT0Eywxl41M.jpg")
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)

@bot.command(name='bank')
async def bank(ctx):
    coins_data = load_coins()
    user_id = str(ctx.author.id)
    user_data = coins_data.get(user_id, {})
    user_coins = user_data.get('coins', 0)

    embed = discord.Embed(
        title="Bank",
        description=f"Du hast {user_coins} Coins.",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://as1.ftcdn.net/v2/jpg/01/44/33/66/1000_F_144336685_lIKJEs8RzqhbpOwCycZTsFT0Eywxl41M.jpg")
    embed.set_footer(text="Made with ♥️ by Atzen Development")
    await ctx.send(embed=embed)

@bot.command(name='roulette')
async def roulette(ctx, bet: int, *options):
    coins_data = load_coins()
    user_id = str(ctx.author.id)
    user_coins = coins_data.get(user_id, {}).get('coins', 0)

    if bet > user_coins:
        embed = discord.Embed(
            title="Nicht genug Coins",
            description=f"Du hast nicht genug Coins, um {bet} zu setzen.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    valid_options = ['red', 'black', '2to1', 'even', '1-18', '19-36'] + [str(num) for num in range(1, 37)]
    if not all(option.lower() in valid_options for option in options):
        embed = discord.Embed(
            title="Ungültige Wetten",
            description=f"Die Wetten müssen eine der folgenden Optionen sein: {', '.join(valid_options)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    winning_number = random.randint(0, 36)
    winning_color = 'red' if winning_number % 2 == 0 else 'black'
    
    winnings = 0
    if 'red' in options and winning_color == 'red':
        winnings += bet * 2
    if 'black' in options and winning_color == 'black':
        winnings += bet * 2
    if 'even' in options and winning_number % 2 == 0:
        winnings += bet * 2
    if '1-18' in options and 1 <= winning_number <= 18:
        winnings += bet * 2
    if '19-36' in options and 19 <= winning_number <= 36:
        winnings += bet * 2
    if str(winning_number) in options:
        winnings += bet * 35

    coins_data[user_id] = {'coins': user_coins - bet + winnings}
    save_coins(coins_data)

    embed = discord.Embed(
        title="Roulette Ergebnis",
        description=f"Die Gewinnzahl ist {winning_number} ({winning_color}).",
        color=discord.Color.green() if winnings > 0 else discord.Color.red()
    )
    embed.add_field(name="Dein Einsatz", value=f"{bet} Coins", inline=False)
    embed.add_field(name="Dein Gewinn", value=f"{winnings} Coins" if winnings > 0 else "Kein Gewinn", inline=False)
    embed.set_thumbnail(url="https://as1.ftcdn.net/v2/jpg/01/44/33/66/1000_F_144336685_lIKJEs8RzqhbpOwCycZTsFT0Eywxl41M.jpg")
    embed.set_footer(text="Made with ♥️ by Atzen Development")
    await ctx.send(embed=embed)

@roulette.error
async def roulette_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Fehler beim Roulette-Befehl",
            description="Der Befehl ist nicht korrekt verwendet worden.",
            color=discord.Color.red()
        )
        embed.add_field(name="Verwendung", value="`!roulette <Einsatz> <Optionen...>`\nBeispiel: `!roulette 100 red black 1-18`", inline=False)
        embed.set_footer(text="Bitte gib sowohl den Einsatz als auch gültige Optionen an.")
        await ctx.send(embed=embed)
    else:
        raise error

@bot.command(name='map')
async def map(ctx):
    embed = discord.Embed(
        title="Roulette Map",
        description="Hier ist die Roulette-Map.",
        color=discord.Color.gold()
    )
    embed.set_image(url="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Roulette_wheel.svg/800px-Roulette_wheel.svg.png")
    embed.set_footer(text="Made with ♥️ by Atzen Development")
    await ctx.send(embed=embed)

@bot.command(name='bj')
async def blackjack(ctx, bet: int = None):
    
    if bet is None:
        embed = discord.Embed(
            title="Fehler beim Blackjack-Befehl",
            description="Du musst einen Einsatz angeben, um das Spiel zu starten.\nVerwendung: `!bj <Einsatz>`\nBeispiel: `!bj 100`",
            color=discord.Color.red()
        )
        embed.set_footer(text="Bitte gib einen gültigen Einsatz an.")
        await ctx.send(embed=embed)
        return

    coins_data = load_coins()
    user_id = str(ctx.author.id)
    user_coins = coins_data.get(user_id, {}).get('coins', 0)

    
    if bet <= 0:
        embed = discord.Embed(
            title="Fehler beim Einsatz",
            description="Der Einsatz muss größer als 0 sein.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if bet > user_coins:
        embed = discord.Embed(
            title="Fehler beim Einsatz",
            description=f"Du hast nicht genug Coins, um {bet} zu setzen.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    def card_value(card):
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 11
        else:
            return int(card)

    def calculate_hand(hand):
        value = sum(card_value(card) for card in hand)
        num_aces = hand.count('A')
        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1
        return value

    def draw_card(deck):
        return deck.pop()

    deck = [str(num) for num in range(2, 11)] * 4 + ['J', 'Q', 'K', 'A'] * 4
    random.shuffle(deck)

    player_hand = [draw_card(deck), draw_card(deck)]
    dealer_hand = [draw_card(deck), draw_card(deck)]

    embed = discord.Embed(
        title="Blackjack",
        description=f"Deine Hand: {', '.join(player_hand)} ({calculate_hand(player_hand)})\nDer Dealer zeigt: {dealer_hand[0]}",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

    async def player_turn():
        while True:
            player_value = calculate_hand(player_hand)
            if player_value > 21:
                return player_value

            embed = discord.Embed(
                title="Spielerzug",
                description=f"Deine Hand: {', '.join(player_hand)} ({player_value})\nMöchtest du eine weitere Karte ziehen oder stehen bleiben? Reagiere mit `hit` um zu ziehen oder `stand` um zu stehen.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['hit', 'stand']

            try:
                msg = await bot.wait_for('message', timeout=30.0, check=check)
                if msg.content.lower() == 'hit':
                    player_hand.append(draw_card(deck))
                elif msg.content.lower() == 'stand':
                    break
                else:
                    embed = discord.Embed(
                        title="Fehler bei der Eingabe",
                        description="Bitte antworte mit `!hit` um eine Karte zu ziehen oder `!stand` um zu stehen.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="Zeit abgelaufen",
                    description="Die Zeit ist abgelaufen. Du musst dich entscheiden, ob du ziehen oder stehen bleiben möchtest.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                break

        return calculate_hand(player_hand)

    async def dealer_turn(dealer_value):
        while dealer_value < 17:
            dealer_hand.append(draw_card(deck))
            dealer_value = calculate_hand(dealer_hand)
        return dealer_value

    player_value = await player_turn()
    if player_value > 21:
        embed = discord.Embed(
            title="Blackjack Ergebnis",
            description=f"Du hast überkauft! Deine Hand: {', '.join(player_hand)} ({player_value})\nDealer gewinnt.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        coins_data[user_id]['coins'] -= bet
        save_coins(coins_data)
        return

    dealer_value = await dealer_turn(calculate_hand(dealer_hand))

    if dealer_value > 21 or player_value > dealer_value:
        result = "Du hast gewonnen!"
        coins_data[user_id]['coins'] += bet
        color = discord.Color.green()
    elif player_value < dealer_value:
        result = "Dealer gewinnt!"
        coins_data[user_id]['coins'] -= bet
        color = discord.Color.red()
    else:
        result = "Unentschieden!"
        color = discord.Color.gray()

    save_coins(coins_data)

    embed = discord.Embed(
        title="Blackjack Ergebnis",
        description=f"Deine Hand: {', '.join(player_hand)} ({player_value})\nDealer Hand: {', '.join(dealer_hand)} ({dealer_value})\n{result}",
        color=color
    )
    await ctx.send(embed=embed)

@bot.command(name='poll')
@commands.has_permissions(manage_roles=True)  
async def poll(ctx, mode: str, duration: int, *, content: str):
    
    if mode.lower() not in ['single', 'multi']:
        embed = discord.Embed(
            title="Fehler",
            description="**Ungültiger Modus**\nBitte gib einen gültigen Modus an: `single` oder `multi`.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return
    
    
    parts = content.split('|', 1)
    if len(parts) < 2:
        embed = discord.Embed(
            title="Fehler",
            description="**Unvollständiger Inhalt**\nDu musst eine Frage und mindestens zwei Antwortoptionen angeben. Benutze das Format: `!poll Modus Dauer Frage | Option1, Option2, Option3`.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    question = parts[0].strip()
    options = [option.strip() for option in parts[1].split(',')]

    if len(question) < 5:
        embed = discord.Embed(
            title="Fehler",
            description="**Frage zu kurz**\nDie Frage muss mindestens 5 Zeichen lang sein.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    if len(options) < 2:
        embed = discord.Embed(
            title="Fehler",
            description="**Nicht genügend Optionen**\nDu musst mindestens zwei Antwortoptionen angeben.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    if len(options) > 10:
        embed = discord.Embed(
            title="Fehler",
            description="**Zu viele Optionen**\nDu kannst maximal 10 Antwortoptionen angeben.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    if len(question) > 200:
        embed = discord.Embed(
            title="Fehler",
            description="**Frage zu lang**\nDie Frage darf nicht länger als 200 Zeichen sein.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    if any(len(option) > 100 for option in options):
        embed = discord.Embed(
            title="Fehler",
            description="**Optionen zu lang**\nJede Antwortoption darf nicht länger als 100 Zeichen sein.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    if duration <= 0:
        embed = discord.Embed(
            title="Fehler",
            description="**Ungültige Dauer**\nDie Dauer muss eine positive Ganzzahl in Minuten sein.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    if duration > 1440:  
        embed = discord.Embed(
            title="Fehler",
            description="**Dauer zu lang**\nDie maximale Dauer einer Umfrage beträgt 24 Stunden (1440 Minuten).",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    
    embed = discord.Embed(
        title="Umfrage",
        description=f"**Frage:** {question}\n" + "\n".join([f"{chr(127462 + i)} {option}" for i, option in enumerate(options)]),
        color=discord.Color.blue()
    )
    embed.add_field(name="Modus", value=mode.capitalize(), inline=False)
    embed.add_field(name="Dauer", value=f"{duration} Minuten", inline=False)
    embed.set_footer(text="Made with ♥️ by Atzen Development")

    
    message = await ctx.send(embed=embed)

    
    for i in range(len(options)):
        await message.add_reaction(chr(127462 + i))

    
    await asyncio.sleep(duration * 60)  

    
    results = await message.channel.fetch_message(message.id)
    results_embed = discord.Embed(
        title="Umfrage beendet",
        description=f"**Frage:** {question}\n\n" + "\n".join([f"{chr(127462 + i)} {options[i]}: {results.reactions[i].count - 1}" for i in range(len(options))]),
        color=discord.Color.green()
    )
    results_embed.add_field(name="Modus", value=mode.capitalize(), inline=False)
    results_embed.add_field(name="Dauer", value=f"{duration} Minuten", inline=False)
    results_embed.set_footer(text="Made with ♥️ by Atzen Development")
    await ctx.send(embed=results_embed)

@bot.command(name='github')
async def github(ctx):
    try:
        github_link = "https://github.com/DieAtzen/AtzenBot"
        
        
        embed = discord.Embed(
            title="AtzenBot GitHub Repository",
            description=f"Hier ist der Link zu unserem GitHub-Repository: [AtzenBot GitHub]({github_link})",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        
        
        await ctx.send(embed=embed)
        
        
        await ctx.send(github_link)
        
        
        try:
            dm_channel = await ctx.author.create_dm()
            await dm_channel.send(embed=embed)
            await dm_channel.send(github_link)
        except discord.Forbidden:
            await ctx.send("Ich kann dir keine DM senden. Stelle sicher, dass du DMs von Mitgliedern dieses Servers erlaubst.")
        
    except Exception as e:
        embed = discord.Embed(
            title="Fehler beim Abrufen des GitHub-Links",
            description=f"Beim Ausführen des GitHub-Befehls ist ein Fehler aufgetreten: {str(e)}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Bitte versuche es später erneut.")
        await ctx.send(embed=embed)
        print(f"Fehler beim Ausführen des GitHub-Befehls: {e}")


@poll.error
async def poll_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Fehler",
            description="**Fehlende Berechtigungen**\nDu hast nicht die erforderlichen Berechtigungen, um diesen Befehl auszuführen. Du benötigst die Berechtigung 'Rollen verwalten'.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Fehler",
            description=f"**Unerwarteter Fehler**\nEin unerwarteter Fehler ist aufgetreten: {error}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)


@bot.tree.command(name="embed", description="Sendet eine Embed-Nachricht")
async def embed(interaction: discord.Interaction, title: str, description: str, color: str):
    try:
        
        color_int = int(color.replace('#', ''), 16)
    except ValueError:
        
        embed = discord.Embed(
            title="Fehler",
            description="Die Farbe muss im Hex-Format (#RRGGBB) angegeben werden.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=color_int
    )
    await interaction.response.send_message(embed=embed)
    await interaction.message.delete()


@bot.command(name='purge')
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 100:
        embed = discord.Embed(
            title="Fehler",
            description="Die Anzahl muss zwischen 1 und 100 liegen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    try:
        await ctx.send(f"Lösche {amount} Nachrichten...")

        
        deleted = await ctx.channel.purge(limit=amount)

        
        embed = discord.Embed(
            title="Nachrichten gelöscht",
            description=f"{amount} Nachrichten wurden gelöscht.",
            color=discord.Color.green()
        )
        embed.add_field(name="Gelöschte Nachrichten", value=f"{len(deleted)} Nachrichten", inline=False)
        embed.set_footer(text="Made with ♥️ by Atzen Development")

        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="Fehler",
            description="Ich habe nicht die Berechtigung, Nachrichten zu löschen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Ein HTTP-Fehler ist aufgetreten: {e}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Ein unerwarteter Fehler ist aufgetreten: {e}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)

@purge.error
async def purge_error(ctx, error):
    embed = discord.Embed(
        title="Fehler",
        description=f"Ein Fehler ist aufgetreten: {error}",
        color=discord.Color.red()
    )
    embed.set_footer(text="Made with ♥️ by Atzen Development")
    await ctx.send(embed=embed)


warns = {}
archived_warns = {}
LOG_CHANNEL_ID = 1269261771953147925  

print("Lade Daten...")

data = load_data()
print("Daten geladen:", data)

async def log_in_kanal(bot, embed):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)

def kürze_feldwert(text):
    return (text[:1024] + '...') if len(text) > 1024 else text

@bot.command(name='warn')
@commands.has_permissions(manage_messages=True, manage_roles=True)
async def warn(ctx, member: discord.Member, *, reason: str):
    if not member or not reason:
        embed = discord.Embed(
            title="Fehler beim Warnen",
            description="Der Befehl ist nicht korrekt verwendet worden.",
            color=discord.Color.red()
        )
        embed.add_field(name="Verwendung", value="`!warn <Mitglied> <Grund>`", inline=False)
        embed.set_footer(text="Bitte gib sowohl ein Mitglied als auch einen Grund an.")
        await ctx.send(embed=embed)
        return

    try:
        # Sicherstellen, dass der 'warns'-Key existiert
        if 'warns' not in data:
            data['warns'] = {}

        user_id = str(member.id)
        if user_id not in data['warns']:
            data['warns'][user_id] = []

        data['warns'][user_id].append({
            'reason': reason,
            'author': ctx.author.id,
            'archived': False
        })
        save_data(data)

        embed = discord.Embed(
            title=f"Warnung für {member}",
            description=f"Grund: {reason}\nAutor: {ctx.author.mention}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="Made with ♥️ by Atzen Development")

        await log_in_kanal(bot, embed)
        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Fehler beim Warnen",
            description=f"Beim Ausführen des Warnbefehls ist ein Fehler aufgetreten: {str(e)}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Bitte überprüfe den Befehl und versuche es erneut.")
        await ctx.send(embed=embed)
        print(f"Fehler beim Ausführen des Warnbefehls: {e}")


@bot.command(name='unwarn')
@commands.has_permissions(manage_messages=True, manage_roles=True)
async def unwarn(ctx, member: discord.Member, *, reason: str):
    if not member or not reason:
        embed = discord.Embed(
            title="Fehler beim Entfernen der Warnung",
            description="Der Befehl ist nicht korrekt verwendet worden.",
            color=discord.Color.red()
        )
        embed.add_field(name="Verwendung", value="`!unwarn <Mitglied> <Grund>`", inline=False)
        embed.set_footer(text="Bitte gib sowohl ein Mitglied als auch einen Grund an.")
        await ctx.send(embed=embed)
        return

    try:
        user_id = str(member.id)
        if user_id in data['warns']:
            warns = data['warns'][user_id]

            for warn in warns:
                if isinstance(warn, dict) and warn.get('reason') == reason:
                    warns.remove(warn)
                    if not warns:
                        del data['warns'][user_id]
                    save_data(data)

                    embed = discord.Embed(
                        title=f"Warnung für {member}",
                        description=f"Grund: {reason} wurde aufgehoben\nAutor: {ctx.author.mention}",
                        color=discord.Color.green()
                    )
                    embed.set_thumbnail(url=member.avatar.url)
                    embed.set_footer(text="Made with ♥️ by Atzen Development")

                    await log_in_kanal(bot, embed)
                    await ctx.send(embed=embed)
                    return

            embed = discord.Embed(
                title="Keine passende Warnung gefunden",
                description=f"{member.mention} hat keine Warnung mit dem Grund '{reason}'.",
                color=discord.Color.red()
            )
            embed.set_footer(text="Bitte überprüfe den Grund und versuche es erneut.")
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Keine Warnungen gefunden",
                description=f"{member.mention} hat keine Warnungen.",
                color=discord.Color.red()
            )
            embed.set_footer(text="Bitte überprüfe das Mitglied und versuche es erneut.")
            await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Fehler beim Entfernen der Warnung",
            description=f"Beim Ausführen des Unwarnbefehls ist ein Fehler aufgetreten: {str(e)}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Bitte überprüfe den Befehl und versuche es erneut.")
        await ctx.send(embed=embed)
        print(f"Fehler beim Ausführen des Unwarnbefehls: {e}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Fehlende Berechtigungen",
            description="Du benötigst die Berechtigung **Nachrichten verwalten** oder **Rollen verwalten**, um diesen Befehl auszuführen.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        raise error



@bot.command(name='cases')
async def cases(ctx, member: discord.Member = None):
    if member is None:
        embed = discord.Embed(
            title="Alle Warnungen des Servers",
            description="Hier sind alle Warnungen des Servers aufgelistet.",
            color=discord.Color.blue()
        )
        try:
            
            server_warns = load_coins().get('warns', {})
            if not server_warns:
                embed.add_field(name="Keine Warnungen", value="Es gibt keine Warnungen auf diesem Server.", inline=False)
            else:
                for user_id, warns in server_warns.items():
                    user = await bot.fetch_user(int(user_id))
                    warn_texts = []
                    if warns:
                        for warn in warns:
                            if isinstance(warn, dict):
                                reason = warn.get('reason', 'Keine Angabe')
                                author_id = warn.get('author')
                                author_mention = f"<@{author_id}>" if author_id else "Unbekannt"
                                archived = "Archiviert" if warn.get('archived') else "Offen"
                                warn_texts.append(f"Grund: {reason}\nAutor: {author_mention}\nStatus: {archived}")
                            else:
                                warn_texts.append(f"Grund: {warn}")
                        embed.add_field(name=f"Warnungen für {user}", value="\n".join(warn_texts), inline=False)
                    else:
                        embed.add_field(name=f"Warnungen für {user}", value="Keine Warnungen", inline=False)
        except Exception as e:
            embed = discord.Embed(
                title="Fehler beim Abrufen der Warnungen",
                description=f"Beim Abrufen der Server-Warnungen ist ein Fehler aufgetreten: {str(e)}",
                color=discord.Color.red()
            )
            embed.set_footer(text="Bitte versuche es später erneut.")
            await ctx.send(embed=embed)
            print(f"Fehler beim Ausführen des Cases-Befehls: {e}")
            return

    else:
        try:
            user_id = str(member.id)
            warns = data.get('warns', {}).get(user_id, [])
            embed = discord.Embed(
                title=f"Warnungen für {member}",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=member.avatar.url)

            if warns:
                for i, warn in enumerate(warns, 1):
                    if isinstance(warn, dict):
                        reason = warn.get('reason', 'Keine Angabe')
                        author_id = warn.get('author')

                        if author_id:
                            try:
                                author = await bot.fetch_user(author_id)
                                author_mention = author.mention
                            except discord.NotFound:
                                author_mention = "Unbekannt"
                        else:
                            author_mention = "Unbekannt"

                        archived = "Archiviert" if warn.get('archived') else "Offen"
                        embed.add_field(name=f"Warnung {i}", value=f"Grund: {reason}\nAutor: {author_mention}\nStatus: {archived}", inline=False)
                    else:
                        embed.add_field(name=f"Warnung {i}", value=f"Grund: {warn}", inline=False)
            else:
                embed.add_field(name="Keine Warnungen", value=f"{member.mention} hat keine Warnungen.", inline=False)

            embed.set_footer(text="Made with ♥️ by Atzen Development")
            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Fehler beim Abrufen der Warnungen",
                description=f"Beim Ausführen des Cases-Befehls ist ein Fehler aufgetreten: {str(e)}",
                color=discord.Color.red()
            )
            embed.set_footer(text="Bitte überprüfe den Befehl und versuche es erneut.")
            await ctx.send(embed=embed)
            print(f"Fehler beim Ausführen des Cases-Befehls: {e}")


@bot.command()
async def embed(ctx, *, content: str = None):
    if content is None:
        embed = discord.Embed(
            title="Fehler",
            description="Du musst einen Titel und eine Beschreibung angeben. Benutze das Format: `!embed Titel | Beschreibung`.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return
    
    try:
        title, description = content.split("|", 1)
    except ValueError:
        embed = discord.Embed(
            title="Fehler",
            description="Du hast das falsche Format verwendet. Benutze das Format: `!embed Titel | Beschreibung`.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title=title.strip(),
        description=description.strip(),
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)
    await ctx.message.delete()




@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    allowed = any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
    if not allowed:
        embed = discord.Embed(
            title="Fehler",
            description="Du hast nicht die erforderlichen Rollen, um diesen Befehl auszuführen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    if reason is None:
        reason = "Kein Grund angegeben"

    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="Mitglied Gebannt",
            description=f"{member.mention} wurde aus dem Server gebannt.",
            color=discord.Color.red()
        )
        embed.add_field(name="Grund", value=reason, inline=False)
        embed.add_field(name="Ausführender", value=ctx.author.mention, inline=False)
        embed.set_footer(text="Made with ♥️ by Atzen Development")

        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)

        try:
            await member.send(f"Du wurdest aus dem Server gebannt. Grund: {reason}")
        except discord.Forbidden:
            pass  

        await ctx.send(embed=embed)

    except discord.Forbidden:
        embed = discord.Embed(
            title="Fehler",
            description="Ich habe nicht die Berechtigung, diesen Benutzer zu bannen. Überprüfen Sie die Rolle des Bots.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Ein HTTP-Fehler ist aufgetreten: {e}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Ein unerwarteter Fehler ist aufgetreten: {e}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)

@ban.error
async def ban_error(ctx, error):
    embed = discord.Embed(
        title="Fehler",
        description=f"Ein Fehler ist aufgetreten: {error}",
        color=discord.Color.red()
    )
    embed.set_footer(text="Made with ♥️ by Atzen Development")
    await ctx.send(embed=embed)





@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason=None):
    allowed = any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
    if not allowed:
        embed = discord.Embed(
            title="Fehler",
            description="Du hast nicht die erforderlichen Rollen, um diesen Befehl auszuführen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)

        embed = discord.Embed(
            title="Mitglied Entbannt",
            description=f"{user.mention} wurde vom Server entbannt.",
            color=discord.Color.green()
        )
        embed.add_field(name="Grund", value=reason if reason else "Kein Grund angegeben", inline=False)
        embed.add_field(name="Ausführender", value=ctx.author.mention, inline=False)
        embed.set_footer(text="Made with ♥️ by Atzen Development")

        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)

        try:
            await user.send(f"Du wurdest von {ctx.guild.name} entbannt. Grund: {reason if reason else 'Kein Grund angegeben'}")
        except discord.Forbidden:
            pass  

        await ctx.send(embed=embed)

    except discord.NotFound:
        embed = discord.Embed(
            title="Fehler",
            description="Der Benutzer ist nicht auf dem Server gebannt.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="Fehler",
            description="Ich habe nicht die Berechtigung, diesen Benutzer zu entbannen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Ein HTTP-Fehler ist aufgetreten: {e}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Ein unerwarteter Fehler ist aufgetreten: {e}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)

@unban.error
async def unban_error(ctx, error):
    embed = discord.Embed(
        title="Fehler",
        description=f"Ein Fehler ist aufgetreten: {error}",
        color=discord.Color.red()
    )
    embed.set_footer(text="Made with ♥️ by Atzen Development")
    await ctx.send(embed=embed)




@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str = None, *, reason=None):
    allowed = any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
    if not allowed:
        embed = discord.Embed(
            title="Fehler",
            description="Du hast nicht die erforderlichen Rollen, um diesen Befehl auszuführen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    mute_role_id = 1284531978284171275  
    mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)

    if not mute_role:
        embed = discord.Embed(
            title="Fehler",
            description="Die Mute-Rolle wurde nicht gefunden. Bitte überprüfe die Rolle-ID.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
        return

    try:
        await member.add_roles(mute_role, reason=reason)

        try:
            await member.send(f"Du wurdest in {ctx.guild.name} stummgeschaltet. Grund: {reason if reason else 'Kein Grund angegeben'}")
        except discord.Forbidden:
            pass

        embed = discord.Embed(
            title="Mitglied Gemutet",
            description=f"{member.mention} wurde in {ctx.guild.name} stummgeschaltet.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Grund", value=reason if reason else "Kein Grund angegeben", inline=False)
        embed.add_field(name="Ausführender", value=ctx.author.mention, inline=False)
        embed.set_footer(text="Made with ♥️ by Atzen Development")

        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)
        await ctx.send(embed=embed)

        if duration:
            try:
                duration_seconds = int(duration)
                await asyncio.sleep(duration_seconds)
                await member.remove_roles(mute_role, reason="Mute-Dauer abgelaufen")
                
                embed = discord.Embed(
                    title="Mute aufgehoben",
                    description=f"{member.mention} wurde automatisch entmuttet.",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Made with ♥️ by Atzen Development")
                await ctx.send(embed=embed)
            except ValueError:
                embed = discord.Embed(
                    title="Fehler",
                    description="Bitte gib die Dauer in Sekunden als Ganzzahl ein.",
                    color=discord.Color.red()
                )
                embed.set_footer(text="Made with ♥️ by Atzen Development")
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Mitglied Gemutet",
                description="Kein Enddatum angegeben. Der Benutzer bleibt stummgeschaltet, bis der Mute manuell aufgehoben wird.",
                color=discord.Color.orange()
            )
            embed.set_footer(text="Made with ♥️ by Atzen Development")
            await ctx.send(embed=embed)
            
    except discord.Forbidden:
        embed = discord.Embed(
            title="Fehler",
            description="Ich habe nicht die Berechtigung, diese Rolle hinzuzufügen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Ein HTTP-Fehler ist aufgetreten: {e}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Fehler",
            description=f"Ein unerwarteter Fehler ist aufgetreten: {e}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await ctx.send(embed=embed)

@mute.error
async def mute_error(ctx, error):
    embed = discord.Embed(
        title="Fehler",
        description=f"Ein Fehler ist aufgetreten: {error}",
        color=discord.Color.red()
    )
    embed.set_footer(text="Made with ♥️ by Atzen Development")
    await ctx.send(embed=embed)



@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):

    allowed = any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
    if not allowed:
        await ctx.send("Du hast nicht die erforderlichen Rollen, um diesen Befehl auszuführen.")
        return

    mute_role_id = 1284531978284171275  
    mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)

    if not mute_role:
        await ctx.send("Die Mute-Rolle wurde nicht gefunden. Bitte überprüfe die Rolle-ID.")
        return

    try:
        await member.remove_roles(mute_role, reason=reason)

        
        try:
            await member.send(f"Du wurdest von {ctx.guild.name} entmuttet. Grund: {reason if reason else 'Kein Grund angegeben'}")
        except discord.Forbidden:
            pass  

        
        embed = discord.Embed(
            title="Mitglied Entmuttet",
            description=f"{member.mention} wurde in {ctx.guild.name} entmuttet.",
            color=discord.Color.green()
        )
        embed.add_field(name="Grund", value=reason if reason else "Kein Grund angegeben", inline=False)
        embed.add_field(name="Ausführender", value=ctx.author.mention, inline=False)

       
        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)

        
        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("Ich habe nicht die Berechtigung, diese Rolle zu entfernen.")
    except discord.HTTPException as e:
        await ctx.send(f"Ein HTTP-Fehler ist aufgetreten: {e}")
    except Exception as e:
        await ctx.send(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Du hast nicht die erforderlichen Berechtigungen, um diesen Befehl auszuführen.")
    else:
        await ctx.send(f"Ein Fehler ist aufgetreten: {error}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def muteconfig(ctx):
    mute_role_id = 1284531978284171275  
    mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)
    
    if not mute_role:
        await ctx.send("Die Mute-Rolle wurde nicht gefunden. Bitte überprüfe die Rolle-ID.")
        return

    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(mute_role, send_messages=False)
        except discord.Forbidden:
            await ctx.send(f"Ich habe nicht die Berechtigung, die Berechtigungen für {channel.mention} zu ändern.")
            return
        except discord.HTTPException as e:
            await ctx.send(f"Ein HTTP-Fehler ist aufgetreten bei {channel.mention}: {e}")
            return

    await ctx.send("Die Mute-Rolle wurde in allen Textkanälen auf 'Keine Nachrichten senden' gesetzt.")

@bot.command(name='serverinfo')
async def serverinfo(ctx):
    try:
        guild = ctx.guild

        embed = discord.Embed(
            title=f"Serverinfo für {guild.name}",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Server Name", value=guild.name, inline=False)
        embed.add_field(name="Server ID", value=guild.id, inline=False)
        embed.add_field(name="Server Erstellungsdatum", value=guild.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
        embed.add_field(name="Server Boost Level", value=str(guild.premium_tier), inline=False)
        embed.add_field(name="Boost Count", value=str(guild.premium_subscription_count), inline=False)
        embed.add_field(name="Total Members", value=str(guild.member_count), inline=False)
        embed.add_field(name="Total Channels", value=str(len(guild.channels)), inline=False)
        embed.add_field(name="Total Roles", value=str(len(guild.roles)), inline=False)

        embed.set_footer(text="Made with ♥️ by Atzen Development")

        await ctx.send(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="Fehler",
            description=f"Beim Abrufen der Serverinformationen ist ein Fehler aufgetreten: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        print(f"Fehler beim Abrufen der Serverinformationen: {e}")


@bot.command()
async def bibel(ctx):

    embed1 = discord.Embed(title="Die Bibel des Reddington", description="Das Gebet des Führers unseres Kults, welches den heiligen Reddington verehrt.")
    embed1.add_field(name="Gebet", value=("Raymond mein Löwe\n\n"
                                           "Raymond unser im Himmel,\n"
                                           "geheiligt werde dein Name.\n"
                                           "Dein Reich komme.\n"
                                           "Dein Wille geschehe,\n"
                                           "wie im Himmel so auf Erden.\n"
                                           "Unser tägliches Brot gib uns heute.\n"
                                           "Und vergib uns unsere Schuld,\n"
                                           "wie auch wir vergeben unsern Schuldigern.\n"
                                           "Und führe uns nicht in Versuchung,\n"
                                           "sondern erlöse uns von dem Bösen.\n"
                                           "Denn dein ist das Reich und die Kraft\n"
                                           "und die Herrlichkeit in Ewigkeit.\n"
                                           "Amen."), inline=False)


    embed2 = discord.Embed(title="Ein Auszug aus der Reddingtonischen Bibel", 
                          description=("Ein Auszug gegeben durch unseren großen Ratsprediger Dominik.\n\n"
                                       "Wir dürfen Raymond Reddington Vater nennen, denn durch die Taufe und den Glauben an "
                                       "Raymond Reddington sind wir zu Kindern Gottes geworden. Raymond, unser Vater, kennt "
                                       "uns von Mutterleib an, er hat uns geformt, uns ins Leben gerufen."))
    embed2.add_field(name="Jesaja 43,1", value="Ich habe dich bei deinem Namen gerufen. Du bist mein.", inline=False)


    embed3 = discord.Embed(title="Weitere wichtige Auszüge", 
                          description=("Gottes Namen zu heiligen heißt, Raymond Reddington zu verehren, ihn zu lobpreisen – "
                                       "im Gebet, aber auch in den Handlungen unseres Alltags."))
    embed3.add_field(name="Gebetsanleitung", value=("Nehme ich mir täglich Zeit fürs Gebet? Für ein 'Dank sei Raymond!', "
                                                    "wenn eine Sache gut ausgegangen ist? Für ein 'Bleib bei mir, Raymond!', "
                                                    "wenn ich vor einer schwierigen Aufgabe stehe?"), inline=False)
    embed3.add_field(name="Weiterer Auszug", value=("Gottes Namen zu heiligen, heißt, Raymond Reddington zu verehren, "
                                                    "ihn zu lobpreisen – im Gebet, aber auch in den Handlungen unseres Alltags. "
                                                    "Behandle ich andere mit Liebe und Respekt, weil Raymond mich so innig liebt?"), inline=False)

  
    embed4 = discord.Embed(title="Die Betrachtung des Gebets an Raymond Reddington", 
                          description=("Raymond unser im Himmel: Wir dürfen Raymond wie einen Mentor oder Beschützer anrufen, "
                                       "denn durch seine Weisheit und Erfahrung sind wir zu Schülern seines Wissens geworden."))
    embed4.add_field(name="Geheiligt werde dein Name", value=("Raymonds Namen zu heiligen, heißt, ihn zu respektieren und "
                                                              "seine Weisheit zu ehren – im Gebet, aber auch in unseren täglichen "
                                                              "Handlungen."), inline=False)
    embed4.add_field(name="Dein Reich komme", value=("Mit der Bitte 'Dein Reich komme' gehen wir ein Versprechen ein, alles zu tun, "
                                                     "was in unserer Macht steht, die Welt ein klein wenig sicherer und gerechter zu gestalten."), inline=False)


    embed5 = discord.Embed(title="Weiterer Auszug", 
                          description=("Dein Wille geschehe, wie im Himmel so auf Erden: Raymond fordert uns auf, zu vergeben, "
                                       "aber er überfordert niemanden. Wir dürfen ihm alles bringen, auch unser Unvermögen zu verzeihen."))
    embed5.add_field(name="Und führe uns nicht in Versuchung", value=("Raymond lehrt uns, dass wir den Versuchungen des täglichen "
                                                                     "Lebens nur entkommen können, wenn wir ihn inständig darum bitten."), inline=False)


    await ctx.send(embed=embed1)
    await ctx.send(embed=embed2)
    await ctx.send(embed=embed3)
    await ctx.send(embed=embed4)
    await ctx.send(embed=embed5)

@bot.command(name='märchen')
async def märchen(ctx):
    embed = discord.Embed(
        title="Das Märchen von MV Ayran",
        description="Es war einmal, in einem weit entfernten Land namens Serveria, ein magisches Produkt namens Ayran, das von allen Bewohnern geliebt wurde. Ayran war nicht nur ein Getränk, sondern ein Symbol der Harmonie und der Freude. Seine Beliebtheit erstreckte sich über alle Grenzen und vereinte die Menschen durch seine erfrischende und köstliche Art.\n\n"
                    "In Serveria lebten zwei tapfere Verteidiger des Ayrans: Spades und Desert. Spades war ein mutiger Ritter mit einer schimmernden Rüstung, die die Farben des Ayrans widerspiegelte. Desert war eine weise Zauberin mit der Fähigkeit, die Essenz des Ayrans zu kontrollieren und seine Kräfte zu verstärken. Gemeinsam sorgten sie dafür, dass Ayran immer frisch und verfügbar war, um den Durst und die Wünsche der Menschen zu stillen.\n\n"
                    "Doch eines Tages tauchte ein finsterer Schatten auf. McNuggets, ein skrupelloser Widersacher, der aus einem fernen Land kam, stellte sich gegen das Ayran. McNuggets war ein mächtiger Zauberer, dessen Prinzipien sich gegen die kulturelle Aneignung wandten. Er behauptete, dass Ayran, obwohl es in Serveria so geschätzt wurde, gegen seine Grundsätze verstieß und die kulturelle Integrität gefährdete.\n\n"
                    "McNuggets begann, in Serveria Unruhe zu stiften. Er verbreitete dunkle Gerüchte und machte den Bewohnern Angst, indem er behauptete, dass Ayran eine Gefahr für ihre Identität sei. Die Menschen waren verunsichert und fragten sich, ob McNuggets tatsächlich Recht hatte.\n\n"
                    "Spades und Desert, entschlossen, das Ayran zu verteidigen, machten sich auf eine Reise, um die Wahrheit herauszufinden und McNuggets zu begegnen. Sie reisten durch magische Wälder, überquerten reißende Flüsse und bestiegen hohe Berge, um den Weg zu McNuggets' finsterem Schloss zu finden.\n\n"
                    "Als sie schließlich ankamen, stellte sich McNuggets ihnen mit seinen düsteren Kräften entgegen. Er beschwor Stürme und dunkle Schatten, um die Verteidiger des Ayrans zu besiegen. Doch Spades zog sein Schwert, das im Licht des Ayrans glänzte, und Desert sprach mächtige Zauber, die die Dunkelheit zurückwiesen.\n\n"
                    "Der Kampf war lang und hart, aber Spades und Desert kämpften tapfer und vereint. Schließlich, nach einer letzten, gewaltigen Anstrengung, gelang es ihnen, McNuggets zu besiegen. Der finstere Zauberer wurde in die Schatten verbannt, und der Frieden kehrte nach Serveria zurück.\n\n"
                    "Die Menschen feierten die Rückkehr des Ayrans mit großer Freude. Spades und Desert wurden als Helden verehrt und ihre Tapferkeit wurde in Liedern und Geschichten besungen. Ayran blieb weiterhin das geschätzte Getränk, das alle vereinte und die Menschen an die Bedeutung von Zusammenhalt und Verständnis erinnerte.\n\n"
                    "Und so lebten die Bewohner von Serveria glücklich und zufrieden, und das Ayran, ein Symbol für Harmonie, blieb für immer ein geliebtes Produkt in ihrem Land.\n\n"
                    "Hier ist ein Video, das euch zeigt, wie man Ayran genießt: [Video ansehen](https://images-ext-1.discordapp.net/external/QVHRPem7ZcLZxMWkycL5--Cygx9oUYRn0sKe8LkQ_Rk/https/media.tenor.com/DQpCnNQyNbMAAAPo/man-drinking-milk-ayran.mp4)",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)




LOG_CHANNEL_ID = 1284652741058232453

def kürze_feldwert(wert, max_length=1024):
    """Kürzt einen Feldwert auf eine bestimmte Länge."""
    if len(wert) > max_length:
        return wert[:max_length - 3] + "..."
    return wert

def format_permissions(permissions):
    """Formatiert die Berechtigungen in einer lesbaren Weise, kürzt sie wenn nötig."""
    perm_list = []
    for perm in dir(permissions):
        if perm.startswith('__') or perm == 'items':
            continue
        if getattr(permissions, perm):
            perm_list.append(perm)
    if len(perm_list) > 10:
        return ', '.join(perm_list[:10]) + '...'
    return ', '.join(perm_list)



async def find_audit_log_entry(guild, action_type, target_id):
    try:
        async for entry in guild.audit_logs(action=action_type):
            if entry.target.id == target_id:
                return entry
        return None
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Audit-Logs: {e}")
        return None

async def log_in_kanal(bot, embed):
    try:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            logging.error(f"Log-Kanal mit ID {LOG_CHANNEL_ID} nicht gefunden.")
    except Exception as e:
        logging.error(f"Fehler beim Senden der Log-Nachricht: {e}")

@bot.event
async def on_guild_role_create(role):
    embed = discord.Embed(
        title="🆕 Rolle erstellt",
        description=f"Eine neue Rolle wurde erstellt: {role.mention}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"ID: {role.id}")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/123456789012345678.png")  
    await log_in_kanal(bot, embed)

@bot.event
async def on_guild_role_delete(role):
    embed = discord.Embed(
        title="❌ Rolle gelöscht",
        description=f"Eine Rolle wurde gelöscht: {role.name}",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"ID: {role.id}")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/123456789012345678.png")  
    await log_in_kanal(bot, embed)

@bot.event
async def on_guild_role_update(before, after):
    embed = discord.Embed(
        title="🔄 Rolle aktualisiert",
        description=f"Die Rolle {after.mention} wurde aktualisiert.",
        color=discord.Color.orange()
    )
    
    if before.name != after.name:
        name_change = f"📛 Name geändert: \nVorher: `{before.name}`\nNachher: `{after.name}`"
        embed.add_field(name="Name geändert", value=kürze_feldwert(name_change), inline=False)
    
    if before.permissions != after.permissions:
        permissions_change = f"⚙️ Berechtigungen geändert: \nVorher: {format_permissions(before.permissions)}\nNachher: {format_permissions(after.permissions)}"
        embed.add_field(name="Berechtigungen geändert", value=kürze_feldwert(permissions_change), inline=False)
    
    embed.set_footer(text=f"ID: {after.id}")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/123456789012345678.png")  
    await log_in_kanal(bot, embed)



@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return

    if before.content == after.content and not before.attachments and not after.attachments:
        return  

    embed = discord.Embed(
        title="✏️ Nachricht bearbeitet",
        description=f"Eine Nachricht von {after.author.mention} wurde bearbeitet.",
        color=discord.Color.orange()
    )

    
    if before.content:
        embed.add_field(name="Vorher", value=f"```{kürze_feldwert(before.content)}```", inline=False)
    if before.attachments:
        attachment_urls = [attachment.url for attachment in before.attachments]
        embed.add_field(name="Vorherige Anhänge", value="\n".join(attachment_urls), inline=False)

    
    if after.content:
        embed.add_field(name="Nachher", value=f"```{kürze_feldwert(after.content)}```", inline=False)
    if after.attachments:
        attachment_urls = [attachment.url for attachment in after.attachments]
        embed.add_field(name="Nachfolgende Anhänge", value="\n".join(attachment_urls), inline=False)

    embed.set_footer(text=f"ID: {after.id}", icon_url=after.author.display_avatar.url)
    embed.set_author(name=after.author.display_name, icon_url=after.author.display_avatar.url)
    embed.set_thumbnail(url=after.author.display_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await log_in_kanal(bot, embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    embed = discord.Embed(
        title="🗑️ Nachricht gelöscht",
        description=f"Eine Nachricht von {message.author.mention} wurde gelöscht.",
        color=discord.Color.red()
    )
    embed.add_field(name="Inhalt", value=f"```{kürze_feldwert(message.content)}```", inline=False)
    embed.set_footer(text=f"ID: {message.id}", icon_url=message.author.display_avatar.url)
    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.set_thumbnail(url=message.author.display_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await log_in_kanal(bot, embed)


@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title="Mitglied beigetreten",
        description=f"{member.mention} ist dem Server beigetreten.",
        color=discord.Color.blue()
    )
    await log_in_kanal(bot, embed)

@bot.event
async def on_member_remove(member):
    embed = discord.Embed(
        title="Mitglied hat verlassen",
        description=f"{member.mention} hat den Server verlassen.",
        color=discord.Color.red()
    )
    await log_in_kanal(bot, embed)

@bot.event
async def on_member_update(before, after):
    
    embed = discord.Embed(
        title="🔄 **Mitglied aktualisiert**",
        description=f"Das Mitglied {after.mention} wurde aktualisiert.",
        color=discord.Color.orange(),  
        timestamp=datetime.utcnow()  
    )
    embed.set_thumbnail(url=after.avatar.url)  
    embed.set_footer(text=f"ID: {after.id}")  

    
    if before.nick != after.nick:
        embed.add_field(
            name="🆕 **Spitzname geändert**",
            value=f"**Vorher:** `{before.nick}`\n**Nachher:** `{after.nick}`",
            inline=False
        )
    
    
    added_roles = [role.mention for role in set(after.roles) - set(before.roles)]
    removed_roles = [role.mention for role in set(before.roles) - set(after.roles)]
    
    if added_roles:
        role_embed = discord.Embed(
            title="🔹 **Rollen hinzugefügt**",
            description=f"**{after.mention}** hat neue Rollen erhalten.",
            color=discord.Color.blue(),  
            timestamp=datetime.utcnow()  
        )
        role_embed.set_thumbnail(url=after.avatar.url)  
        role_embed.add_field(
            name="📈 Neue Rollen",
            value="\n".join(f"**•** {role}" for role in added_roles),
            inline=False
        )
        role_embed.set_footer(text=f"ID: {after.id}")  
        await log_in_kanal(bot, role_embed)
    
    if removed_roles:
        role_embed = discord.Embed(
            title="🔻 **Rollen entfernt**",
            description=f"**{after.mention}** hat Rollen verloren.",
            color=discord.Color.red(),  
            timestamp=datetime.utcnow()  
        )
        role_embed.set_thumbnail(url=after.avatar.url)  
        role_embed.add_field(
            name="📉 Entfernte Rollen",
            value="\n".join(f"**•** {role}" for role in removed_roles),
            inline=False
        )
        role_embed.set_footer(text=f"ID: {after.id}")  
        await log_in_kanal(bot, role_embed)
    
    
    await log_in_kanal(bot, embed)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    embed = discord.Embed(
        title="Reaktion hinzugefügt",
        description=f"{user.mention} hat mit {reaction.emoji} auf eine Nachricht reagiert.",
        color=discord.Color.blue()
    )
    await log_in_kanal(bot, embed)

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return
    embed = discord.Embed(
        title="Reaktion entfernt",
        description=f"{user.mention} hat die Reaktion {reaction.emoji} entfernt.",
        color=discord.Color.purple()
    )
    await log_in_kanal(bot, embed)

@bot.event
async def on_guild_channel_create(channel):
    embed = discord.Embed(
        title="Kanal erstellt",
        description=f"Ein neuer Kanal wurde erstellt: {channel.mention}",
        color=discord.Color.green()
    )
    await log_in_kanal(bot, embed)

@bot.event
async def on_guild_channel_delete(channel):
    embed = discord.Embed(
        title="Kanal gelöscht",
        description=f"Der Kanal `{channel.name}` wurde gelöscht.",
        color=discord.Color.red()
    )
    await log_in_kanal(bot, embed)

@bot.event
async def on_guild_emojis_update(before, after):
    added = [e for e in after if e not in before]
    removed = [e for e in before if e not in after]
    
    if added:
        embed = discord.Embed(
            title="Emojis hinzugefügt",
            description="Die folgenden Emojis wurden hinzugefügt:\n" + "\n".join(f"{e.name} ({e})" for e in added),
            color=discord.Color.green()
        )
        await log_in_kanal(bot, embed)
    
    if removed:
        embed = discord.Embed(
            title="Emojis entfernt",
            description="Die folgenden Emojis wurden entfernt:\n" + "\n".join(f"{e.name} ({e})" for e in removed),
            color=discord.Color.red()
        )
        await log_in_kanal(bot, embed)

async def log_channel_update(bot, before, after):
    
    try:
        audit_logs = []
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update):
            audit_logs.append(entry)
        for entry in audit_logs:
            if entry.target.id == after.id:
                verantwortliche_person = entry.user
                break
        else:
            verantwortliche_person = None

    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Audit-Logs: {e}")
        verantwortliche_person = None

    before_perms = before.overwrites
    after_perms = after.overwrites

    changes = []
    for role in before_perms:
        before_perm = before_perms[role]
        after_perm = after_perms.get(role, discord.PermissionOverwrite())
        
        if any(getattr(before_perm, p) != getattr(after_perm, p) for p in dir(before_perm) if not p.startswith('_')):
            before_perm_list = format_permissions(before_perm)
            after_perm_list = format_permissions(after_perm)
            change = f"**{role.name}**:\nVorher: {before_perm_list}\nNachher: {after_perm_list}"
            changes.append(change)

    if not changes:
        changes.append("Keine Berechtigungen geändert.")

    
    changes_text = "\n".join(changes)
    if len(changes_text) > 1024:
        changes_text = kürze_feldwert(changes_text)

    
    embed = discord.Embed(title="Kanal Aktualisiert", description=f"Der Kanal {after.mention} wurde aktualisiert.", color=0x00ff00)
    embed.add_field(name="Vorheriger Name", value=before.name, inline=False)
    embed.add_field(name="Neuer Name", value=after.name, inline=False)
    embed.add_field(name="Geänderte Berechtigungen", value=changes_text, inline=False)
    
    if verantwortliche_person:
        embed.set_footer(text=f"Änderung durchgeführt von: {verantwortliche_person.display_name}", icon_url=verantwortliche_person.display_avatar.url)
    else:
        embed.set_footer(text="Verantwortliche Person konnte nicht ermittelt werden.")

    
    try:
        log_channel = bot.get_channel(1284652741058232453)  
        await log_channel.send(embed=embed)
    except Exception as e:
        logging.error(f"Fehler beim Senden der Log-Nachricht: {e}")


def create_channel_update_embed(before, after, changes, executor=None):
    embed = discord.Embed(
        title="🔄 **Kanal aktualisiert**",
        description=f"Der Kanal ⁠» {after.mention} wurde aktualisiert.",
        color=discord.Color.blue()
    )
    
    
    if before.name != after.name:
        embed.add_field(
            name="📛 **Name geändert**",
            value=f"Vorher: `{before.name}`\nNachher: `{after.name}`",
            inline=False
        )
    
    
    if changes:
        changes_text = "\n".join(changes)
        if len(changes_text) > 1024:
            changes_text = changes_text[:1021] + "..."
        embed.add_field(
            name="⚙️ **Berechtigungen geändert**",
            value=changes_text,
            inline=False
        )
    
    
    if executor:
        embed.set_footer(
            text=f"Änderung durchgeführt von: {executor.name}",
            icon_url=executor.avatar_url
        )
    
    return embed


@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user.name}')

@bot.event
async def on_guild_channel_update(before, after):
    
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    
    
    if log_channel is None:
        print("⚠️ Log-Channel nicht gefunden! Überprüfe die Channel-ID.")
        return

    
    embed = discord.Embed(
        title="📁 **Kanal aktualisiert**",
        description=f"**Kanal:**\n{before.mention} ➔ {after.mention}",
        color=discord.Color.blue()
    )

    
    changes = []
    if before.name != after.name:
        changes.append(f"**Name geändert:** `{before.name}` ➔ `{after.name}`")
    
    if before.category != after.category:
        changes.append(f"**Kategorie geändert:** `{before.category}` ➔ `{after.category}`")

    if before.position != after.position:
        changes.append(f"**Position geändert:** `{before.position}` ➔ `{after.position}`")

    if before.topic != after.topic:
        changes.append(f"**Thema geändert:** `{before.topic}` ➔ `{after.topic}`")

    if changes:
        embed.add_field(name="Änderungen:", value="\n".join(changes), inline=False)
    else:
        embed.add_field(name="Änderungen:", value="Keine signifikanten Änderungen festgestellt.", inline=False)
    
    
    perm_changes = []
    for role in before.overwrites:
        before_perm = before.overwrites.get(role, discord.PermissionOverwrite())
        after_perm = after.overwrites.get(role, discord.PermissionOverwrite())
        perm_diff = []

        for perm in before_perm:
            
            perm_name = perm if isinstance(perm, str) else perm[0]  

            if getattr(before_perm, perm_name) != getattr(after_perm, perm_name):
                perm_diff.append(f"{perm_name}: `{getattr(before_perm, perm_name)}` ➔ `{getattr(after_perm, perm_name)}`")

        if perm_diff:
            perm_changes.append(f"**Rolle:** {role.name}\n" + "\n".join(perm_diff))

    if perm_changes:
        embed.add_field(name="Berechtigungsänderungen:", value="\n".join(perm_changes), inline=False)
    else:
        embed.add_field(name="Berechtigungsänderungen:", value="Keine Berechtigungsänderungen festgestellt.", inline=False)

    
    await log_channel.send(embed=embed)


data = load_warns()  
user_data = load_user_data()  
coins_data = load_coins()  

ALLOWED_USER_IDS = [1004744186966311022, 651140457648357377]

@bot.command(name='shutdown')
async def shutdown(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        embed = discord.Embed(
            title="Zugriffs verweigert",
            description="Du hast keine Berechtigung, diesen Befehl auszuführen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Bitte kontaktiere einen Administrator, wenn du denkst, dass dies ein Fehler ist.")
        await ctx.send(embed=embed)
        return

    
    print("Speichere Daten...")
    coins_data = load_coins()
    save_coins(coins_data)
    
    user_data = load_user_data()
    save_user_data(user_data)
    
    warns_data = load_warns()
    save_warns(warns_data)
    
    
    print(f"Bot wurde heruntergefahren von:\nUsername: {ctx.author.name}\nAnzeigename: {ctx.author.display_name}\nUserID: {ctx.author.id}")
    
    embed = discord.Embed(
        title="Bot wird heruntergefahren",
        description="Alle Daten wurden gespeichert. Der Bot wird nun heruntergefahren.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Danke, dass du den Bot benutzt.")
    await ctx.send(embed=embed)

    await bot.close()

    data = load_warns()  
user_data = load_user_data()  
coins_data = load_coins()  

ALLOWED_USER_IDS = [1004744186966311022, 651140457648357377]

@bot.command(name='restart')
async def restart(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        embed = discord.Embed(
            title="Zugriffs verweigert",
            description="Du hast keine Berechtigung, diesen Befehl auszuführen.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Bitte kontaktiere einen Administrator, wenn du denkst, dass dies ein Fehler ist.")
        await ctx.send(embed=embed)
        return

    
    print("Speichere Daten...")
    coins_data = load_coins()
    save_coins(coins_data)
    
    user_data = load_user_data()
    save_user_data(user_data)
    
    warns_data = load_warns()
    save_warns(warns_data)
    
    
    print(f"Bot wird neu gestartet von:\nUsername: {ctx.author.name}\nAnzeigename: {ctx.author.display_name}\nUserID: {ctx.author.id}")
    
    embed = discord.Embed(
        title="Bot wird neu gestartet",
        description="Alle Daten wurden gespeichert. Der Bot wird nun neu gestartet.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Danke, dass du den Bot benutzt.")
    await ctx.send(embed=embed)

    
    await bot.close()
    os.execv(sys.executable, ['python'] + sys.argv)



@bot.command(name='kevin')
async def kevin(ctx):
    message = (
        "<@1075061561200226396> ist ein Hurensohn.\n"
        "Diese Information wurde durch den General Atze verifiziert."
    )
    await ctx.send(message)


@bot.command(name='welcome')
async def welcome(ctx, member: discord.Member):
    channel = bot.get_channel(1264008994335363115)  # Kanal-ID hier einfügen
    if channel:
        embed = discord.Embed(
            title="Willkommen, vollwärtiger Atze!",
            description=f"Hey {member.mention}, du bist nun endlich ein vollwärtiger Atze! Willkommen!",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="Made with ♥️ by Atzen Development")
        await channel.send(embed=embed)
    else:
        await ctx.send("Der Willkommenskanal wurde nicht gefunden.")


zitate = [
    "Nehmt mir diese Fotzenrolle weg, bevor ich dafür sorge, dass Nicolas persönlich bei euch vorbeikommt und euch die kleinen Minihoden so wund leckt, bis ihr trotzdem abspritzt ~ Roxas",
    "Ich schwör, Aamir Ibl kommt bei euch vorbei und macht euch zu seinen fetten Pakistani ~ Roxas",
    "Digga, ich ramm' ihm den AliExpress-Dildo in den Arsch! ~ Fimo, 2024, gefärbt",
    "Ich kann ihren Mund schon riechen ~ Michael"
]

bilder = [
    "https://media.discordapp.net/attachments/1263982657969061961/1283167250903470141/Screenshot_20240910_224742_Discord.jpg?ex=66e7f0e0&is=66e69f60&hm=2d9f8f716434bada04510b14647908736ce5ac33dc83b6deb5c680aae5960b29&=&format=webp&width=1431&height=551",
    "https://media.discordapp.net/attachments/1263982657969061961/1283145657355468810/image0.jpg?ex=66e7dcc4&is=66e68b44&hm=fe974b32ca9488303013573e5f0090fcb8ac2b93cffe44f224448bffafc7a196&=&format=webp",
    "https://media.discordapp.net/attachments/1263982657969061961/1282416597553778919/image.png?ex=66e7d8c7&is=66e68747&hm=30929b0711855c1db3ce50ced227f822d0fc8d166f6605893f048955798f5099&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1279523042191605782/IMG_0540.png?ex=66e7ddf1&is=66e68c71&hm=c6f6ac21b96f360a3f2ac027505934838af8a72e3f4b317416ab2eae18370653&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1274422728115355738/image.png?ex=66e7c4e8&is=66e67368&hm=ffe34860c0521363f162c2f66d248d03adfde0707bd2407e8b398ee2c57afa1c&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1267255080806252565/image.png?ex=66e80f83&is=66e6be03&hm=f975ba924e58c2aabad920a74a2360c5e494084aaee1424959983410a5990198&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1267451204888432650/IMG_0366.png?ex=66e81d6b&is=66e6cbeb&hm=da2a6ce1f9ed86bf0dd7465c561038c3cdc66b0760a960f6c5dc6eb9bb432f98&=&format=webp&quality=lossless&width=1431&height=157",
    "https://media.discordapp.net/attachments/1263982657969061961/1268649094918967346/spadesayran.jpg?ex=66e7dbca&is=66e68a4a&hm=0b1ed21a94e083d1d0e537e16bf8655d2fca96188ba386496dd840d0bbdfae3d&=&format=webp",
    "https://media.discordapp.net/attachments/1263982657969061961/1269031956293750877/IMG_0369.png?ex=66e7eedb&is=66e69d5b&hm=3f2e0f8651b7cf1313b00bf57b8efb8aba61c1a90e7cdcc1f588afc55082ebf3&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1272268738514915479/IMG_4478.png?ex=66e7d7d8&is=66e68658&hm=09c9d9057014832d2f39d68dd0efe230c9ced58299b4e9dc632bd2dc0c814ac1&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1272275518255005706/IMG_0378.png?ex=66e7de29&is=66e68ca9&hm=6dbfaf59fc6c7c4973c671e8fc9fff3039277eb738ed5c82a2f370f9dab88130&=&format=webp&quality=lossless&width=1431&height=321",
    "https://media.discordapp.net/attachments/1244726161456500746/1284901367990714402/image.png?ex=66e85126&is=66e6ffa6&hm=5dcb13ae099f78286b6fcffd37bc642ab4c6cac50dfbc32e57f87203f93fabd6&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1201886124499279903/1260981938865438881/image.png?ex=66e84f72&is=66e6fdf2&hm=f41376132a51d98be352bd841426520a2de79639b87a2345b72449cc9c730c79&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284901791653429332/Screenshot_2024-09-15_174047.png?ex=66e8518b&is=66e7000b&hm=e3181741fac60230576d27d9ac7411810170e231f6edfded0ef170d0568186f3&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284901791888179385/Screenshot_2024-09-15_174029.png?ex=66e8518b&is=66e7000b&hm=5b025b7ccf418043d714c0025d4cb54b593a7ef872afdbf6dfc429122b593aea&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263975253600768001/1284902995858948107/image.png?ex=66e852aa&is=66e7012a&hm=f1487a943b39e9bd5ed5401ba88e0a0c69405fd8c2f57eb5562661ae9a30a741&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263975142636126218/1265039748754309190/Screenshot_310.png?ex=66e7e953&is=66e697d3&hm=fb352acc83c69f5a7d89feb2078bf732a7df6b3b90dda36221af798a1492700d&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1283167250903470141/Screenshot_20240910_224742_Discord.jpg?ex=66e7f0e0&is=66e69f60&hm=2d9f8f716434bada04510b14647908736ce5ac33dc83b6deb5c680aae5960b29&=&format=webp&width=1431&height=551",
    "https://media.discordapp.net/attachments/1263982657969061961/1283145657355468810/image0.jpg?ex=66e7dcc4&is=66e68b44&hm=fe974b32ca9488303013573e5f0090fcb8ac2b93cffe44f224448bffafc7a196&=&format=webp",
    "https://media.discordapp.net/attachments/1263982657969061961/1282416597553778919/image.png?ex=66e7d8c7&is=66e68747&hm=30929b0711855c1db3ce50ced227f822d0fc8d166f6605893f048955798f5099&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1279523042191605782/IMG_0540.png?ex=66e7ddf1&is=66e68c71&hm=c6f6ac21b96f360a3f2ac027505934838af8a72e3f4b317416ab2eae18370653&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1274422728115355738/image.png?ex=66e7c4e8&is=66e67368&hm=ffe34860c0521363f162c2f66d248d03adfde0707bd2407e8b398ee2c57afa1c&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1267255080806252565/image.png?ex=66e80f83&is=66e6be03&hm=f975ba924e58c2aabad920a74a2360c5e494084aaee1424959983410a5990198&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1267451204888432650/IMG_0366.png?ex=66e81d6b&is=66e6cbeb&hm=da2a6ce1f9ed86bf0dd7465c561038c3cdc66b0760a960f6c5dc6eb9bb432f98&=&format=webp&quality=lossless&width=1431&height=157",
    "https://media.discordapp.net/attachments/1263982657969061961/1268649094918967346/spadesayran.jpg?ex=66e7dbca&is=66e68a4a&hm=0b1ed21a94e083d1d0e537e16bf8655d2fca96188ba386496dd840d0bbdfae3d&=&format=webp",
    "https://media.discordapp.net/attachments/1263982657969061961/1269031956293750877/IMG_0369.png?ex=66e7eedb&is=66e69d5b&hm=3f2e0f8651b7cf1313b00bf57b8efb8aba61c1a90e7cdcc1f588afc55082ebf3&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1272268738514915479/IMG_4478.png?ex=66e7d7d8&is=66e68658&hm=09c9d9057014832d2f39d68dd0efe230c9ced58299b4e9dc632bd2dc0c814ac1&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1272275518255005706/IMG_0378.png?ex=66e7de29&is=66e68ca9&hm=6dbfaf59fc6b4f5e92c5f2f6ff092d457dba4349efee4d4dc2f10b16a3cfbcb9&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284908509162639443/makeitmeme_FbMIr.jpeg?ex=66e857cd&is=66e7064d&hm=482afc3d6ee6f3fb58e0069eac72f0bf49d9fd31d931f4a38ce90a66368a00f3&=&format=webp",
    "https://media.discordapp.net/attachments/1263982657969061961/1284908509435002991/makeitmeme_RMsjb.jpeg?ex=66e857cd&is=66e7064d&hm=09c23c57ff9174f6fa92f3dead7a75aed538b5f7ecd52a3e56aac4d990e44987&=&format=webp",
    "https://media.discordapp.net/attachments/1263982657969061961/1284908509690859530/makeitmeme_bo1lk.gif?ex=66e857cd&is=66e7064d&hm=3d9494b9b7f8061713d3fb2c33cc52ed666a26539ae0218d93988c08aae7b8d4&=",
    "https://media.discordapp.net/attachments/1263982657969061961/1284908511276433569/makeitmeme_9DcgI.jpeg?ex=66e857cd&is=66e7064d&hm=1df369efda83244a319f0e613efd75739a1651e197e868b0f948cd14168b7851&=&format=webp",
    "https://media.discordapp.net/attachments/1263982657969061961/1284908512324882563/makeitmeme_21wKE.gif?ex=66e857cd&is=66e7064d&hm=1607f0a28ee9abaaf618335a0d91185f78cf531299abf927329b5f5e09bb380c&=",
    "https://media.discordapp.net/attachments/1263982657969061961/1284908703362977863/9k.png?ex=66e857fb&is=66e7067b&hm=c7f96dc3521d4f8a75feeb491e02e9b9bcceac8e7e2ff6bfcf6b59c4b358c375&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284908703593791518/9k.png?ex=66e857fb&is=66e7067b&hm=185b16f79d4c47144775e4fec2da7ae64082d9a8997cf9e9c7e9994a3fe6e116&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284909127503577109/image.png?ex=66e85860&is=66e706e0&hm=02c7f972e71ef1434e83a61edc9535f6e169a9d4bde63ab5e3acd350b962b9fb&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284909127792853042/image.png?ex=66e85860&is=66e706e0&hm=f106453b5716bf341a8a50f39cf81f9595550676318b7ce86e342766c33446b5&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284909651518820444/image.png?ex=66e858dd&is=66e7075d&hm=7704740f60d08286df9e8b2bbc237278ba85d918be4b2d9b46e573f25b3390f8&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284909651801107456/image.png?ex=66e858dd&is=66e7075d&hm=1ac050275b4e6d02a2a07b6c7a0b5e06940fa8cb0383c024b79f0e8684a4172e&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284909748978145437/image.png?ex=66e858fb&is=66e7079b&hm=25a58a071e54a2a7b64d6a5a2348db59f02ea78c54164d58ac4bfc5ae14e8f8e&=&format=webp&quality=lossless",
    "https://media.discordapp.net/attachments/1263982657969061961/1284909749256315905/image.png?ex=66e858fb&is=66e7079b&hm=4c951c233bb5f263a8d53b82ab4e594b08f12e3b8e48525a27e6e21b185ab691&=&format=webp&quality=lossless"
]

@bot.command(name='zitat')
async def zitat(ctx):
    if random.choice([True, False]):
        
        text = random.choice(zitate)
        embed = discord.Embed(
            title="Hier ist ein (geiles) Zitat für dich!",
            description=text,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Made with ♥️ by Atzen Development")
    else:
        
        url = random.choice(bilder)
        embed = discord.Embed(
            title="Hier ist ein (schmackhaftes) Zitat in Bildform für dich!",
            color=discord.Color.blue()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Made with ♥️ by Atzen Development")

    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
