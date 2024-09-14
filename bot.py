import discord
import asyncio
from discord.ext import commands

# Konfigurationswerte
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

# Definiere den Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name='!command für Hilfe'))
@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name='!command für Hilfe'))


@bot.command()
async def command(ctx):
    embed = discord.Embed(
        title="Bot Befehle",
        description="Hier ist eine Liste aller verfügbaren Befehle.",
        color=discord.Color.blue()
    )
    
    # Hier kannst du die Befehle hinzufügen
    embed.add_field(name="!ban", value="Bannt einen Benutzer und sendet eine DM mit dem Grund.", inline=False)
    embed.add_field(name="!unban", value="Hebt das Verbot eines Benutzers auf.", inline=False)
    embed.add_field(name="!mute", value="Stummstellt einen Benutzer.", inline=False)
    embed.add_field(name="!unmute", value="Entmuttet einen Benutzer.", inline=False)
    embed.add_field(name="!muteconfig", value="Setzt die Berechtigungen für die Mute-Rolle in allen Textkanälen.", inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    # Überprüfen, ob der Benutzer eine der erlaubten Rollen hat
    allowed = any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
    if not allowed:
        await ctx.send("Du hast nicht die erforderlichen Rollen, um diesen Befehl auszuführen.")
        return

    if reason is None:
        reason = "Kein Grund angegeben"

    # Bannen des Mitglieds
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} wurde aus dem Server gebannt.")

        # Nachricht an den Benutzer senden
        try:
            await member.send(f"Du wurdest aus dem Server gebannt. Grund: {reason}")
        except discord.Forbidden:
            pass  # Falls der Bot keine DM senden kann

        # Embed erstellen
        embed = discord.Embed(
            title="Mitglied Gebannt",
            description=f"{member.mention} wurde aus dem Server gebannt.",
            color=discord.Color.red()
        )
        embed.add_field(name="Grund", value=reason, inline=False)
        embed.add_field(name="Ausführender", value=ctx.author.mention, inline=False)

        # Embed an den Channel senden
        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("Ich habe nicht die Berechtigung, diesen Benutzer zu bannen. Überprüfen Sie die Rolle des Bots.")
    except discord.HTTPException as e:
        await ctx.send(f"Ein HTTP-Fehler ist aufgetreten: {e}")
    except Exception as e:
        await ctx.send(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# Fehlerbehandlung für fehlende Berechtigungen
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Du hast nicht die erforderlichen Berechtigungen, um diesen Befehl auszuführen.")
    else:
        await ctx.send(f"Ein Fehler ist aufgetreten: {error}")




@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason=None):
    # Überprüfen, ob der Benutzer eine der erlaubten Rollen hat
    allowed = any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
    if not allowed:
        await ctx.send("Du hast nicht die erforderlichen Rollen, um diesen Befehl auszuführen.")
        return

    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)

        # Nachricht an den Benutzer senden
        try:
            await user.send(f"Du wurdest von {ctx.guild.name} entbannt. Grund: {reason if reason else 'Kein Grund angegeben'}")
        except discord.Forbidden:
            pass  # Falls der Bot keine DM senden kann

        # Embed erstellen
        embed = discord.Embed(
            title="Mitglied Entbannt",
            description=f"{user.mention} wurde vom Server entbannt.",
            color=discord.Color.green()
        )
        embed.add_field(name="Grund", value=reason if reason else "Kein Grund angegeben", inline=False)
        embed.add_field(name="Ausführender", value=ctx.author.mention, inline=False)

        # Embed an den Channel senden
        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)

        # Antwort im aktuellen Channel
        await ctx.send(embed=embed)

    except discord.NotFound:
        await ctx.send("Der Benutzer ist nicht auf dem Server gebannt.")
    except discord.Forbidden:
        await ctx.send("Ich habe nicht die Berechtigung, diesen Benutzer zu entbannen.")
    except discord.HTTPException as e:
        await ctx.send(f"Ein HTTP-Fehler ist aufgetreten: {e}")
    except Exception as e:
        await ctx.send(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# Fehlerbehandlung für fehlende Berechtigungen
@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Du hast nicht die erforderlichen Berechtigungen, um diesen Befehl auszuführen.")



@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str = None, *, reason=None):
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

        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)
        await ctx.send(embed=embed)

        if duration:
            try:
                duration_seconds = int(duration)
                await asyncio.sleep(duration_seconds)
                await member.remove_roles(mute_role, reason="Mute-Dauer abgelaufen")
                await ctx.send(f"{member.mention} wurde automatisch entmuttet.")
            except ValueError:
                await ctx.send("Bitte gib die Dauer in Sekunden als Ganzzahl ein.")
        else:
            await ctx.send("Kein Enddatum angegeben. Der Benutzer bleibt stummgeschaltet, bis der Mute manuell aufgehoben wird.")
    except discord.Forbidden:
        await ctx.send("Ich habe nicht die Berechtigung, diese Rolle hinzuzufügen.")
    except discord.HTTPException as e:
        await ctx.send(f"Ein HTTP-Fehler ist aufgetreten: {e}")
    except Exception as e:
        await ctx.send(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Du hast nicht die erforderlichen Berechtigungen, um diesen Befehl auszuführen.")
    else:
        await ctx.send(f"Ein Fehler ist aufgetreten: {error}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    # Überprüfen, ob der Benutzer eine der erlaubten Rollen hat
    allowed = any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
    if not allowed:
        await ctx.send("Du hast nicht die erforderlichen Rollen, um diesen Befehl auszuführen.")
        return

    mute_role_id = 1284531978284171275  # Ersetze dies durch die ID der Mute-Rolle
    mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)

    if not mute_role:
        await ctx.send("Die Mute-Rolle wurde nicht gefunden. Bitte überprüfe die Rolle-ID.")
        return

    try:
        await member.remove_roles(mute_role, reason=reason)

        # Nachricht an den Benutzer senden
        try:
            await member.send(f"Du wurdest von {ctx.guild.name} entmuttet. Grund: {reason if reason else 'Kein Grund angegeben'}")
        except discord.Forbidden:
            pass  # Falls der Bot keine DM senden kann

        # Embed erstellen
        embed = discord.Embed(
            title="Mitglied Entmuttet",
            description=f"{member.mention} wurde in {ctx.guild.name} entmuttet.",
            color=discord.Color.green()
        )
        embed.add_field(name="Grund", value=reason if reason else "Kein Grund angegeben", inline=False)
        embed.add_field(name="Ausführender", value=ctx.author.mention, inline=False)

        # Embed an den Channel senden
        log_channel = bot.get_channel(1269261771953147925)
        await log_channel.send(embed=embed)

        # Antwort im aktuellen Channel
        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("Ich habe nicht die Berechtigung, diese Rolle zu entfernen.")
    except discord.HTTPException as e:
        await ctx.send(f"Ein HTTP-Fehler ist aufgetreten: {e}")
    except Exception as e:
        await ctx.send(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# Fehlerbehandlung für fehlende Berechtigungen
@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Du hast nicht die erforderlichen Berechtigungen, um diesen Befehl auszuführen.")
    else:
        await ctx.send(f"Ein Fehler ist aufgetreten: {error}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def muteconfig(ctx):
    mute_role_id = 1284531978284171275  # Die ID der Mute-Rolle
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


# Befehl für das Gebet des Reddington
@bot.command()
async def bibel(ctx):
    # Erster Embed
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

    # Zweiter Embed
    embed2 = discord.Embed(title="Ein Auszug aus der Reddingtonischen Bibel", 
                          description=("Ein Auszug gegeben durch unseren großen Ratsprediger Dominik.\n\n"
                                       "Wir dürfen Raymond Reddington Vater nennen, denn durch die Taufe und den Glauben an "
                                       "Raymond Reddington sind wir zu Kindern Gottes geworden. Raymond, unser Vater, kennt "
                                       "uns von Mutterleib an, er hat uns geformt, uns ins Leben gerufen."))
    embed2.add_field(name="Jesaja 43,1", value="Ich habe dich bei deinem Namen gerufen. Du bist mein.", inline=False)

    # Dritter Embed
    embed3 = discord.Embed(title="Weitere wichtige Auszüge", 
                          description=("Gottes Namen zu heiligen heißt, Raymond Reddington zu verehren, ihn zu lobpreisen – "
                                       "im Gebet, aber auch in den Handlungen unseres Alltags."))
    embed3.add_field(name="Gebetsanleitung", value=("Nehme ich mir täglich Zeit fürs Gebet? Für ein 'Dank sei Raymond!', "
                                                    "wenn eine Sache gut ausgegangen ist? Für ein 'Bleib bei mir, Raymond!', "
                                                    "wenn ich vor einer schwierigen Aufgabe stehe?"), inline=False)
    embed3.add_field(name="Weiterer Auszug", value=("Gottes Namen zu heiligen, heißt, Raymond Reddington zu verehren, "
                                                    "ihn zu lobpreisen – im Gebet, aber auch in den Handlungen unseres Alltags. "
                                                    "Behandle ich andere mit Liebe und Respekt, weil Raymond mich so innig liebt?"), inline=False)

    # Vierter Embed
    embed4 = discord.Embed(title="Die Betrachtung des Gebets an Raymond Reddington", 
                          description=("Raymond unser im Himmel: Wir dürfen Raymond wie einen Mentor oder Beschützer anrufen, "
                                       "denn durch seine Weisheit und Erfahrung sind wir zu Schülern seines Wissens geworden."))
    embed4.add_field(name="Geheiligt werde dein Name", value=("Raymonds Namen zu heiligen, heißt, ihn zu respektieren und "
                                                              "seine Weisheit zu ehren – im Gebet, aber auch in unseren täglichen "
                                                              "Handlungen."), inline=False)
    embed4.add_field(name="Dein Reich komme", value=("Mit der Bitte 'Dein Reich komme' gehen wir ein Versprechen ein, alles zu tun, "
                                                     "was in unserer Macht steht, die Welt ein klein wenig sicherer und gerechter zu gestalten."), inline=False)

    # Fünfter Embed
    embed5 = discord.Embed(title="Weiterer Auszug", 
                          description=("Dein Wille geschehe, wie im Himmel so auf Erden: Raymond fordert uns auf, zu vergeben, "
                                       "aber er überfordert niemanden. Wir dürfen ihm alles bringen, auch unser Unvermögen zu verzeihen."))
    embed5.add_field(name="Und führe uns nicht in Versuchung", value=("Raymond lehrt uns, dass wir den Versuchungen des täglichen "
                                                                     "Lebens nur entkommen können, wenn wir ihn inständig darum bitten."), inline=False)

    # Embeds senden
    await ctx.send(embed=embed1)
    await ctx.send(embed=embed2)
    await ctx.send(embed=embed3)
    await ctx.send(embed=embed4)
    await ctx.send(embed=embed5)

# Bot starten
bot.run(TOKEN)
