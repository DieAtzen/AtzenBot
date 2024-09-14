import json
import discord
import asyncio
from discord.ext import commands

# Config
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


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
async def command(ctx):
    embed = discord.Embed(
        title="Bot Befehle",
        description="Hier ist eine Liste aller verfügbaren Befehle.",
        color=discord.Color.blue()
    )
    
    
    embed.add_field(name="!ban", value="Bannt einen Benutzer und sendet eine DM mit dem Grund.", inline=False)
    embed.add_field(name="!unban", value="Hebt das Verbot eines Benutzers auf.", inline=False)
    embed.add_field(name="!mute", value="Stummstellt einen Benutzer.", inline=False)
    embed.add_field(name="!unmute", value="Entmuttet einen Benutzer.", inline=False)
    embed.add_field(name="!warn", value="warnt einen User", inline=False)
    embed.add_field(name="!unwarn", value="unwarnt einen User", inline=False)
    embed.add_field(name="!cases", value="Zeigt die Cases eines Users an", inline=False)
    embed.add_field(name="!muteconfig", value="Setzt die Berechtigungen für die Mute-Rolle in allen Textkanälen.", inline=False)
    embed.add_field(name="!purge", value="Löscht Nachrichten in einem Kanal", inline=False)
    embed.add_field(name="!bibel", value="Schickt die Bibel des heiligen Reddington", inline=False)
    embed.add_field(name="**/**embed", value="Schickt eine Nachricht in einem Embed", inline=False)

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name='!command für Hilfe'))

@bot.tree.command(name="embed", description="Sendet eine Embed-Nachricht")
async def embed(interaction: discord.Interaction, title: str, description: str, color: str):
    try:
        # Hex zu Integer
        color_int = int(color.replace('#', ''), 16)
    except ValueError:
        # Fehlerbehandlung, wenn die Farbe nicht im richtigen Format ist
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



@bot.command(name='github')
async def github(ctx):
    github_url = "https://github.com/DieAtzen/AtzenBot/"
    await ctx.send(f"Hier ist der Link zu unserem GitHub-Repository: {github_url}")
    await ctx.author.send(f"Hier ist der Link zu unserem GitHub-Repository: {github_url}")

warns = {}
archived_warns = {}

print("Lade Daten...")

def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'warns': {}}
    except json.JSONDecodeError:
        print("Fehler beim Lesen der JSON-Datei")
        return {'warns': {}}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

data = load_data()

print("Daten geladen:", data)

@bot.command(name='warn')
async def warn(ctx, member: discord.Member, *, reason: str):
    try:
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
            description=f"Grund: {reason}",
            color=discord.Color.red()
        )
        
        
        embed.set_thumbnail(url=member.avatar.url)
        
        
        embed.set_footer(text="Made with ♥️ by Atzen Development")

        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Beim Ausführen des Warnbefehls ist ein Fehler aufgetreten: {str(e)}")
        print(f"Fehler beim Ausführen des Warnbefehls: {e}")


def validate_warns(data):
    if 'warns' not in data:
        data['warns'] = {}
    for user_id, warns in data['warns'].items():
        if not isinstance(warns, list):
            data['warns'][user_id] = []
        for i, warn in enumerate(warns):
            if not isinstance(warn, dict):
                data['warns'][user_id][i] = {'reason': 'Unknown', 'author': None, 'archived': False}
            else:
                if 'reason' not in warn:
                    warn['reason'] = 'Unknown'
                if 'author' not in warn:
                    warn['author'] = None
                if 'archived' not in warn:
                    warn['archived'] = False

def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

def load_data():
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {'warns': {}, 'archived_warns': {}}
    return data

def validate_warns(data):
    if 'warns' not in data:
        data['warns'] = {}
    for user_id, warns in data['warns'].items():
        if not isinstance(warns, list):
            data['warns'][user_id] = []
        for i, warn in enumerate(warns):
            if not isinstance(warn, dict):
                data['warns'][user_id][i] = {'reason': 'Unknown', 'author': None, 'archived': False}
            else:
                if 'reason' not in warn:
                    warn['reason'] = 'Unknown'
                if 'author' not in warn:
                    warn['author'] = None
                if 'archived' not in warn:
                    warn['archived'] = False

data = load_data()
validate_warns(data)

@bot.command(name='unwarn')
async def unwarn(ctx, member: discord.Member, *, reason: str):
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
                        description=f"Grund: {reason} wurde aufgehoben",
                        color=discord.Color.green()
                    )
                    
                    
                    embed.set_thumbnail(url=member.avatar.url)
                    
                    
                    embed.set_footer(text="Made with ♥️ by Atzen Development")

                    log_channel = bot.get_channel(1269261771953147925)
                    await log_channel.send(embed=embed)

                    await ctx.send(embed=embed)
                    return
            
            await ctx.send(f"{member.mention} hat keine Warnung mit dem Grund '{reason}'.")

        else:
            await ctx.send(f"{member.mention} hat keine Warnungen.")

    except Exception as e:
        await ctx.send(f"Beim Ausführen des Unwarnbefehls ist ein Fehler aufgetreten: {str(e)}")
        print(f"Fehler beim Ausführen des Unwarnbefehls: {e}")





@bot.command(name='cases')
async def cases(ctx, member: discord.Member):
    try:
        user_id = str(member.id)
        warns = data['warns'].get(user_id, [])
        embed = discord.Embed(
            title=f"Warnungen für {member}",
            color=discord.Color.blue()
        )
        
        
        embed.set_thumbnail(url=member.avatar.url)

        # die warns
        if warns:
            for i, warn in enumerate(warns, 1):
                if isinstance(warn, dict):
                    reason = warn.get('reason', 'Keine Angabe')
                    author = bot.get_user(warn.get('author')) or "Unbekannt"
                    archived = "Archiviert" if warn.get('archived') else "Offen"
                    embed.add_field(name=f"Warnung {i}", value=f"Grund: {reason}\nAutor: {author}\nStatus: {archived}", inline=False)
                else:
                    embed.add_field(name=f"Warnung {i}", value=f"Grund: {warn}", inline=False)
        else:
            embed.add_field(name="Keine Warnungen", value=f"{member.mention} hat keine Warnungen.", inline=False)

        # unser geiler footer
        embed.set_footer(text="Made with ♥️ by Atzen Development")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Beim Ausführen des Cases-Befehls ist ein Fehler aufgetreten: {str(e)}")
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

if __name__ == "__main__":
    bot.run(TOKEN)
