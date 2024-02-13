import commune as c
import discord
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from discord.ext import commands
from io import BytesIO

client = commands.Bot(intents=discord.Intents.default(), command_prefix='/')

# Read Discord bot token from token.txt
with open('token.txt', 'r') as f:
    TOKEN = f.read().strip()

model = c.module('model.PhotoMaker')()

    # model.generate(imgUrl=image_url, promptText=prompt_text)
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.command()
async def generate(ctx, *args):
    image_url = None
    if ctx.message.attachments:
        image_url = ctx.message.attachments[0].url

    # Combine the arguments to form the prompt text
    prompt_text = ' '.join(args)
    response = requests.get(image_url)

    images = model.generate(imgUrl=BytesIO(response.content), promptText=prompt_text)
    files = []
    
    for i, imageUrl in enumerate(images):
        files.append(discord.File(imageUrl))
    await ctx.send(files=files)

    # Send the image to the Discord channel
    # await ctx.send(file=discord.File('generated_image.jpg'))


client.run(TOKEN)
