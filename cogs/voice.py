import discord, asyncio, traceback, sqlite3, validators
from discord.ext import commands

class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Création des channels + cooldown
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
        voice=c.fetchone()
        if voice is None:
            pass
        else:
            voiceID = voice[0]
            try:
                if after.channel.id == voiceID:
                    c.execute("SELECT * FROM voiceChannel WHERE userID = ?", (member.id,))
                    cooldown=c.fetchone()
                    # Cooldown
                    if cooldown is None or member.id == 484007826696568842:
                        pass
                    else:
                        await member.send("Tu crées des salons trop rapidement, tu as été mis dans un cooldown de 15 secondes !")
                        await asyncio.sleep(15)
                    c.execute("SELECT voiceCategoryID FROM guild WHERE guildID = ?", (guildID,))
                    voice=c.fetchone()
                    c.execute("SELECT channelName, channelLimit FROM userSettings WHERE userID = ?", (member.id,))
                    setting=c.fetchone()
                    c.execute("SELECT channelLimit FROM guildSettings WHERE guildID = ?", (guildID,))
                    guildSetting=c.fetchone()
                    if setting is None:
                        name = f"Salon de {member.name}"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting[0]
                    else:
                        if guildSetting is None:
                            name = setting[0]
                            limit = setting[1]
                        elif guildSetting is not None and setting[1] == 0:
                            name = setting[0]
                            limit = guildSetting[0]
                        else:
                            name = setting[0]
                            limit = setting[1]
                    categoryID = voice[0]
                    id = member.id
                    # Création du channel + move
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(name,category=category)
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True,read_messages=True)
                    await channel2.edit(name= name, user_limit = limit)
                    c.execute("INSERT INTO voiceChannel VALUES (?, ?)", (id,channelID))
                    conn.commit()
                    # Suppression du channel quand il y a personne
                    def check(a,b,c):
                        return len(channel2.members) == 0
                    await self.bot.wait_for('voice_state_update', check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    c.execute('DELETE FROM voiceChannel WHERE userID=?', (id,))
            except:
                pass
        conn.commit()
        conn.close()

    # Commande invite
    @commands.command()
    async def invite(self, ctx):
        await ctx.channel.send('**Utilises ce lien pour inviter le bot sur ton serveur :**\nhttps://discord.com/oauth2/authorize?client_id=669960409884655618&scope=bot&permissions=288374865')

    # Commande help
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Panneau d\'aide", description="",color=0x7289da)
        embed.set_author(name=f"{ctx.guild.me.display_name}",url="https://discordbots.org/bot/472911936951156740", icon_url=f"{ctx.guild.me.avatar_url}")
        embed.add_field(name=f'**Commandes**', value=f'**Bloque le canal, empêchant de le rejoindre par un autre utilisateur :**\n`.voice lock`\n------------\n'
                        f'**Débloquer le canal :**\n`.voice unlock`\n------------\n'
                        f'**Changer le nom du canal :**\n`.voice name <name>` (alias : rename)\n**Example:** `.voice name EU 5kd+`\n------------\n'
                        f'**Limite le nombre d\'utilisateur pouvant rejoindre le canal :**\n`.voice limit number`\n**Example:** `.voice limit 2`\n------------\n'
                        f'**Prendre le contrôle du canal si le créateur l\'as quitté :**\n`.voice claim`\n**Example:** `.voice claim`\n------------\n'
                        f'**Accorde la permission à certains utilisateurs de rejoindre le canal :**\n`.voice permit @person` (alias : allow)\n**Example:** `.voice permit @</cнαxιяαxι>#1136`\n------------\n'
                        f'**Expluse certains utilisateurs de rejoindre le canal :**\n`.voice reject @person` (alias : deny)\n**Example:** `.voice reject @</cнαxιяαxι>#1136`\n', inline='false')
        embed.set_footer(text='Bot developed by </cнαxιяαxι>#1136')
        await ctx.channel.send(embed=embed)

    # Commande de base voice
    @commands.group()
    async def voice(self, ctx):
        pass

    # Commande de setup
    @voice.command()
    async def setup(self, ctx):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        guildID = ctx.guild.id
        id = ctx.author.id
        if ctx.author.id == ctx.guild.owner_id or ctx.author.id == 484007826696568842:
            def check(m):
                return m.author.id == ctx.author.id
            await ctx.channel.send("**Tu as 60 secondes pour réponde à chaque question !**")
            await ctx.channel.send(f"**Entrez le nom de la catégorie où les channels vont être :(e.g Voice Channels)**")
            try:
                category = await self.bot.wait_for('message', check=check, timeout = 60.0)
            except asyncio.TimeoutError:
                await ctx.channel.send('Tu as pris trop longtemps pour répondre !')
            else:
                new_cat = await ctx.guild.create_category_channel(category.content)
                await ctx.channel.send('**Entre le nom du channel vocal : (e.g Join To Create)**')
                try:
                    channel = await self.bot.wait_for('message', check=check, timeout = 60.0)
                except asyncio.TimeoutError:
                    await ctx.channel.send('Tu as pris trop longtemps pour répondre !')
                else:
                    try:
                        channel = await ctx.guild.create_voice_channel(channel.content, category=new_cat)
                        c.execute("SELECT * FROM guild WHERE guildID = ? AND ownerID=?", (guildID, id))
                        voice=c.fetchone()
                        if voice is None:
                            c.execute ("INSERT INTO guild VALUES (?, ?, ?, ?)",(guildID,id,channel.id,new_cat.id))
                        else:
                            c.execute ("UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",(guildID,id,channel.id,new_cat.id, guildID))
                        await ctx.channel.send("**Setup terminé !**")
                    except:
                        await ctx.channel.send("Tu n'as pas rentré les noms correctement.\nUtilises `.voice setup` de nouveau !")
        else:
            await ctx.channel.send(f"{ctx.author.mention} Seulement le propriétaire du serveur peut setup le bot !")
        conn.commit()
        conn.close()

    # Commande de limite de salons vocaux
    @commands.command()
    async def setlimit(self, ctx, num):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        if ctx.author.id == ctx.guild.owner_id or ctx.author.id == 484007826696568842:
            c.execute("SELECT * FROM guildSettings WHERE guildID = ?", (ctx.guild.id,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO guildSettings VALUES (?, ?, ?)", (ctx.guild.id,f"Salon de {ctx.author.name}",num))
            else:
                c.execute("UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?", (num, ctx.guild.id))
            await ctx.send("Tu as changé la limite par défaut pour ton serveur !")
        else:
            await ctx.channel.send(f"{ctx.author.mention} Seulement le propriétaire du serveur peut setup le bot !")
        conn.commit()
        conn.close()

    # Fonction affichage erreurs dans console
    @setup.error
    async def info_error(self, ctx, error):
        print(error)

    # Commande de vérouillage lock
    @voice.command()
    async def lock(self, ctx):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Tu ne possèdes pas de channel.")
        else:
            channelID = voice[0]
            role = discord.utils.get(ctx.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False,read_messages=True)
            await ctx.channel.send(f'{ctx.author.mention} Salon vocal bloqué ! 🔒')
        conn.commit()
        conn.close()

    # Commande de dévérouillage unlock
    @voice.command()
    async def unlock(self, ctx):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Tu ne possèdes pas de channel.")
        else:
            channelID = voice[0]
            role = discord.utils.get(ctx.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True,read_messages=True)
            await ctx.channel.send(f'{ctx.author.mention} Salon vocal débloqué ! 🔓')
        conn.commit()
        conn.close()

    # Commande d'autorisation permit/allow
    @voice.command(aliases=["allow"])
    async def permit(self, ctx, member : discord.Member):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Tu ne possèdes pas de channel.")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await ctx.channel.send(f'{ctx.author.mention} Tu as autorisé {member.name} d\'accéder au channel. ✅')
        conn.commit()
        conn.close()

    # Commande de refus reject/deny
    @voice.command(aliases=["deny"])
    async def reject(self, ctx, member : discord.Member):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Tu ne possèdes pas de channel.")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
                    voice=c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False,read_messages=True)
            await ctx.channel.send(f'{ctx.author.mention} Tu as refusé l\'accès au channel pour {member.name}. ❌')
        conn.commit()
        conn.close()

    # Commande de limite de membre par channel limit
    @voice.command()
    async def limit(self, ctx, limit):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Tu ne possèdes pas de channel.")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit = limit)
            await ctx.channel.send(f'{ctx.author.mention} Tu as mis la limite du channel à '+ '{}!'.format(limit))
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id,f'{ctx.author.name}',limit))
            else:
                c.execute("UPDATE userSettings SET channelLimit = ? WHERE userID = ?", (limit, id))
        conn.commit()
        conn.close()

    # Commande de rename name/rename
    @voice.command(aliases=["rename"])
    async def name(self, ctx,*, name):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Tu ne possèdes pas de channel.")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name = name)
            await ctx.channel.send(f'{ctx.author.mention} Tu as changé le nom du channel pour '+ '{}!'.format(name))
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id,name,0))
            else:
                c.execute("UPDATE userSettings SET channelName = ? WHERE userID = ?", (name, id))
        conn.commit()
        conn.close()

    # Commande de claim
    @voice.command()
    async def claim(self, ctx):
        x = False
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        channel = ctx.author.voice.channel
        if channel == None:
            await ctx.channel.send(f"{ctx.author.mention} Tu n'es pas dans un salon vocal.")
        else:
            id = ctx.author.id
            c.execute("SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,))
            voice=c.fetchone()
            if voice is None:
                await ctx.channel.send(f"{ctx.author.mention} Tu ne peux pas claim ce channel !")
            else:
                for data in channel.members:
                    if data.id == voice[0]:
                        owner = ctx.guild.get_member(voice [0])
                        await ctx.channel.send(f"{ctx.author.mention} Ce channel appartient déjà à {owner.mention} !")
                        x = True
                if x == False:
                    await ctx.channel.send(f"{ctx.author.mention} Tu es désormais le propriétaire du channel !")
                    c.execute("UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (id, channel.id))
            conn.commit()
            conn.close()


def setup(bot):
    bot.add_cog(voice(bot))
