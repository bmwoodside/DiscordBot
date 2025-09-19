# bot.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot_prefix="!"
bot = commands.Bot(command_prefix=bot_prefix, intents = intents)


#### Bot Events ####

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{bot_prefix}commands")
    )

@bot.event
async def on_member_join(member):
    try:
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member.name}, welcome to my Discord server!'
        )
    except discord.Forbidden:
            pass

@bot.event # ensures that if message originates from bot that it won't trigger additional onMessage() commands.
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    elif message.content == 'raise-exception':
        raise discord.DiscordException
    
    await bot.process_commands(message)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a', encoding="utf-8") as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

#### End Bot Events ####

#### BOT COMMANDS ####

@bot.command(name="commands", help="List of Bot Commands.")
async def list_commands(ctx: commands.Context):
    return await ctx.send("commands, join, leave")

@bot.command(name="join", help="Bot joins your current voice channel.")
async def join(ctx: commands.Context):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("You need to be in a voice channel first.")
    
    channel = ctx.author.voice.channel
    vc: discord.VoiceClient | None = ctx.voice_client
    try:
        if vc and vc.is_connected():
            if vc.channel.id == channel.id:
                return await ctx.send(f"Already connected to **{channel}** voice channel.")
            
            await vc.move_to(channel)
            return await ctx.send(f"Moved to **{channel}** voice channel.")
        else:
            await channel.connect(reconnect=True)
            return await ctx.send(f"Joined **{channel}** voice channel.")
    except discord.Forbidden:
        await ctx.send(f"I don't have permission to connect/speak in that channel.")
    except discord.ClientException as e:
        await ctx.send(f"Could not connect: {e}")
    except Exception as e:
        await ctx.send("Unexpected error while connecting.")
        raise

@bot.command(name="leave", aliases=["dc", "disconnect"], help="Bot leaves the Voice Channel.")
async def leave(ctx: commands.Context):
    vc: discord.VoiceClient | None = ctx.voice_client
    if not vc or not vc.is_connected():
        return await ctx.send("I'm not connected to a voice channel.")
    channel_name = vc.channel.name
    await vc.disconnect(force = True)
    await ctx.send(f"Left **{channel_name}** voice channel.")

#### END BOT COMMANDS ####

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Put it in your .env file.")

bot.run(TOKEN)