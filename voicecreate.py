import discord, traceback, sys
from discord.ext import commands

bot = commands.Bot(command_prefix=".")

bot.remove_command("help")

DISCORD_TOKEN = 'Enter Discord Token here'

initial_extensions = ['cogs.voice']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

@bot.event
async def on_ready():
    print('=-=-=-=-=-=-=-=-=-=-=-=')
    print('Connecté en tant que :')
    print(bot.user.name)
    print('\nID du bot :')
    print(bot.user.id)
    print("=-=-=-=-=-=-=-=-=-=-=-=")

bot.run(DISCORD_TOKEN)
