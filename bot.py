import os
import asyncio
import subprocess
from discord.ext import commands
from dotenv import load_dotenv
from discord import Intents, Embed, File
import logging
import time
from configs.helper import help_commands
from configs import helper

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.default()
intents.message_content = True

# Configure logging to capture logs in a date-wise file
log_filename = os.path.join('logs', f"bot_log_{time.strftime('%Y_%m_%d')}.log")

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set up logging to capture both info and error logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename),  # Save logs to a file
        logging.StreamHandler()  # Also print logs to the console
    ]
)


# class MyBot(commands.Bot):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.command_lock = asyncio.Lock()

#     def get_command_lock(self):
#         return self.command_lock


# Use MyBot instead of commands.Bot
# bot = MyBot(command_prefix='/', intents=intents)

bot = commands.Bot(command_prefix='/', intents=intents)

# command for help
@bot.command(name='bot_help')
async def help_command(ctx):
    help_embed = Embed(title="Bot Commands", description="Here are the commands you can use:")
    commands_desc = help_commands()
    for command, description in commands_desc.items():
        help_embed.add_field(
            name=f"{command}",
            value=description,
            inline=False
        )
    await ctx.send(embed=help_embed)

# command for log file
@bot.command(name='logs')
async def send_log(ctx, date):
    await ctx.send(file=File(f"{os.getcwd()}/logs/bot_log_{date}.log"))

# command for set config
@bot.command(name='generate_project_id')
async def generate_id(ctx, project_name):
    project_id = helper.generate_id(project_name)
    await ctx.send(project_id)
    
# command for count
@bot.command(name='counts')
async def get_counts(ctx, project_id, from_date, to_date):
    result = helper.counts(project_id, from_date, to_date)
    if isinstance(result, dict):
        if result['status_code'] == 200:
            await ctx.send(file=File(f"{os.getcwd()}/{result['file']}"))
    else:
        await ctx.send(result)

# For error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Send a custom error message if the command is not found
        await ctx.send("**Oops! Command not found.** Please check the available commands using **/bot_help** command..")
        logging.error(f"Command not found: {ctx.message.content}")
    else:
        await ctx.send("**An error occurred while processing your command.** Please check the available commands using **/bot_help** command..")
        logging.error(f"Error in command {ctx.message.content}: {error}")


bot.run(TOKEN)
