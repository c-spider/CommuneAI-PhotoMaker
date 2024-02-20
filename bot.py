import commune as c
import discord
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from discord.ext import commands
from io import BytesIO
from datetime import datetime

intents = discord.Intents.default()
intents.messages = True  # For receiving messages
intents.message_content = True  # For receiving message content

client = commands.Bot(intents=intents, command_prefix='/')

# Read Discord bot token from token.txt
with open('token.txt', 'r') as f:
    TOKEN = f.read().strip()

# Modules from Commune
photoMaker = c.module('model.PhotoMaker')()
translator = c.module('model.Translation')()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):

    # Check if the message has an attachment and starts with the command prefix
    if message.attachments and message.content.startswith('/generate'):
        # Get the prompt text by removing the command from the message content
        prompt_text = message.content[len('/generate '):].strip()

        # Download the image from the attachment
        image_url = message.attachments[0].url
        response = requests.get(image_url)

        images = photoMaker.generate(imgUrl=BytesIO(response.content), promptText=prompt_text)

        files = []
        for i, imageUrl in enumerate(images):
            files.append(discord.File(imageUrl))

        await message.channel.send(files=files)

    elif message.content.startswith('/translate'):
        parts = message.content[len('/translate'):].strip().split()

        # Initialize variables for source and target languages
        mode = "T2TT" # Text to Text Translation
        srcLang = "eng"
        tarLang = "cmn"
        prompt_text = None

        # Iterate over the parts to find srcLang and tarLang
        for part in parts:
            if part.startswith('src_lang='):
                srcLang = part.split('=')[1]
            elif part.startswith('tar_lang='):
                tarLang = part.split('=')[1]
            elif part.startswith('mode='):
                mode = part.split('=')[1]
            else:
                # Once we find a part that is not a parameter, the rest is considered the prompt text
                prompt_text = ' '.join(parts[parts.index(part):])
                break

        # Check if we have both languages and the prompt text
        if srcLang and tarLang and prompt_text:
            # Do something with the parameters and the prompt text
            
            if mode == "T2TT":
                ans = translator.text2text(text=prompt_text, src_lang=srcLang, target_lang=tarLang)
                await message.reply(ans)
            elif mode == "T2ST":
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                ans = translator.text2speech(text=prompt_text, src_lang=srcLang, target_lang=tarLang, output_file=f"./speeches/{timestamp}.wav")
                await message.reply(ans, file=discord.File(f"./speeches/{timestamp}.wav"))
            elif mode == "S2TT":
                ans = translator.speech2text(text=prompt_text, src_lang=srcLang, target_lang=tarLang)
                await message.reply(ans)
            elif mode == "S2ST":
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                ans = translator.speech2speech(text=prompt_text, src_lang=srcLang, target_lang=tarLang, output_file=f"/speeches/{timestamp}.wav")
                await message.reply(ans)

client.run(TOKEN)
