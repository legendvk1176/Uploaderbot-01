import os
import re
import sys
import m3u8
import json
import time
import pytz
import asyncio
import requests
import subprocess
import urllib
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from logs import logging
from bs4 import BeautifulSoup
import saini as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

AUTH_USER = os.environ.get('AUTH_USERS', '8032590813,7578460365').split(',')
AUTH_USERS = [int(user_id) for user_id in AUTH_USER]
if int(OWNER) not in AUTH_USERS:
    AUTH_USERS.append(int(OWNER))
CHANNEL_OWNERS = {}
CHANNELS = os.environ.get('CHANNELS', '').split(',')
CHANNELS_LIST = [int(channel_id) for channel_id in CHANNELS if channel_id.isdigit()]
cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")
api_url = "http://master-api-v3.vercel.app/"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
token_cp ='eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'
adda_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJkcGthNTQ3MEBnbWFpbC5jb20iLCJhdWQiOiIxNzg2OTYwNSIsImlhdCI6MTc0NDk0NDQ2NCwiaXNzIjoiYWRkYTI0Ny5jb20iLCJuYW1lIjoiZHBrYSIsImVtYWlsIjoiZHBrYTU0NzBAZ21haWwuY29tI"
photologo = 'https://telegra.ph/file/513781fc10729ce618f65-82e00d1e4b19bd50dd.jpg'
photoyt = 'https://tinypic.host/images/2025/03/18/YouTube-Logo.wine.png'
photocp = 'https://telegra.ph/file/513781fc10729ce618f65-82e00d1e4b19bd50dd.jpg'
photozip = 'https://envs.sh/cD_.jpg'

async def show_random_emojis(message):
    emojis = ['🐼', '🐶', '🐅', '⚡️', '🚀', '✨', '💥', '☠️', '🥂', '🍾', '📬', '👻', '👀', '🌹', '💀', '🐇', '⏳', '🔮', '🦔', '📖', '🦁', '🐱', '🐻']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message

# Inline keyboard for start command
BUTTONSCONTACT = InlineKeyboardMarkup([[InlineKeyboardButton(text="☏𝗖𝗢𝗡𝗧𝗔𝗖𝗧☏", url="https://t.me/VK_0786BOT")]])
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="☏𝗖𝗢𝗡𝗧𝗔𝗖𝗧☏", url="https://t.me/VK_0786BOT"),
            InlineKeyboardButton(text="🛠️Help", url="https://t.me/VK_0786BOT"),
        ],
    ]
)

# Image URLs for the random image feature
image_urls = [
    "https://telegra.ph/file/513781fc10729ce618f65-82e00d1e4b19bd50dd.jpg",
    "https://telegra.ph/file/badc46e24928b0efa4ca9-9bfac2a3382b30153e.jpg",
]

@bot.on_message(filters.command("addauth") & filters.private)
async def add_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    try:
        new_user_id = int(message.command[1])
        if new_user_id in AUTH_USERS:
            await message.reply_text("User ID is already authorized.")
        else:
            AUTH_USERS.append(new_user_id)
            os.environ['AUTH_USERS'] = ','.join(map(str, AUTH_USERS))
            await message.reply_text(f"User ID {new_user_id} added to authorized users.")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid user ID.")
        
@bot.on_message(filters.command("remauth") & filters.private)
async def remove_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    try:
        user_id_to_remove = int(message.command[1])
        if user_id_to_remove not in AUTH_USERS:
            await message.reply_text("User ID is not in the authorized users list.")
        else:
            AUTH_USERS.remove(user_id_to_remove)
            os.environ['AUTH_USERS'] = ','.join(map(str, AUTH_USERS))
            await message.reply_text(f"User ID {user_id_to_remove} removed from authorized users.")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid user ID.")

@bot.on_message(filters.command("users") & filters.private)
async def list_auth_users(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    user_list = '\n'.join(map(str, AUTH_USERS))
    await message.reply_text(f"<blockquote>Authorized Users:</blockquote>\n{user_list}")

@bot.on_message(filters.command("addchnl") & filters.private)
async def add_channel(client: Client, message: Message):
    if message.from_user.id not in AUTH_USERS:
        return await message.reply_text("You are not authorized to use this command.")

    try:
        new_channel_id = int(message.command[1])
        
        if not str(new_channel_id).startswith("-100"):
            return await message.reply_text("Invalid channel ID. Channel IDs must start with -100.")
        
        if new_channel_id in CHANNELS_LIST:
            await message.reply_text("Channel ID is already added.")
        else:
            CHANNELS_LIST.append(new_channel_id)
            CHANNEL_OWNERS[new_channel_id] = message.from_user.id
            os.environ['CHANNELS'] = ','.join(map(str, CHANNELS_LIST))
            await message.reply_text(f"Channel ID {new_channel_id} added to the list and you are now the owner.")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid channel ID.")

@bot.on_message(filters.command("remchnl") & filters.private)
async def remove_channel(client: Client, message: Message):
    try:
        channel_id_to_remove = int(message.command[1])
        
        if channel_id_to_remove not in CHANNELS_LIST:
            return await message.reply_text("Channel ID is not in the list.")
        
        if message.from_user.id != OWNER and CHANNEL_OWNERS.get(channel_id_to_remove) != message.from_user.id:
            return await message.reply_text("You are not authorized to remove this channel.")

        CHANNELS_LIST.remove(channel_id_to_remove)
        if channel_id_to_remove in CHANNEL_OWNERS:
            del CHANNEL_OWNERS[channel_id_to_remove]
        
        os.environ['CHANNELS'] = ','.join(map(str, CHANNELS_LIST))
        await message.reply_text(f"Channel ID {channel_id_to_remove} removed from the list.")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid channel ID.")

@bot.on_message(filters.command("channels") & filters.private)
async def list_channels(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    if not CHANNELS_LIST:
        await message.reply_text("No channels have been added yet.")
    else:
        channel_list = '\n'.join(map(str, CHANNELS_LIST))
        await message.reply_text(f"<blockquote>Authorized Channels:</blockquote>\n{channel_list}")
        
@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text("Please upload the cookies file (.txt format).", quote=True)

    try:
        input_message: Message = await client.listen(m.chat.id)

        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        downloaded_path = await input_message.download()

        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text("✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`.")

    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["t2t"]))
async def text_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    editable = await message.reply_text(f"<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("🚨 **error**: Send valid text data")
        return

    text_data = input_message.text.strip()
    await input_message.delete()
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text
    await inputn.delete()
    await editable.delete()

    if raw_textn == '/d':
        custom_file_name = 'txt_file'
    else:
        custom_file_name = raw_textn

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(document=txt_file, caption=f"`{custom_file_name}.txt`\n\nYou can now download your content! 📥")
    os.remove(txt_file)

UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'

@bot.on_message(filters.command(["y2t"]))
async def youtube_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    
    editable = await message.reply_text("Send YouTube Website/Playlist link for convert in .txt file")

    input_message: Message = await bot.listen(message.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)
    await editable.delete(True)

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': 'youtube_cookies.txt'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            if 'entries' in result:
                title = result.get('title', 'youtube_playlist')
            else:
                title = result.get('title', 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await message.reply_text(f"<pre><code>🚨 Error occurred {str(e)}</code></pre>")
            return

    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry['url']
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result['url']
        videos.append(f"{video_title}: {url}")

    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    await message.reply_document(
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<pre><code>{title}.txt</code></pre>\n'
    )

    os.remove(txt_file)


m_file_path = "main.py"
@bot.on_message(filters.command("getcookies") & filters.private)
async def getcookies_handler(client: Client, m: Message):
    try:
        await client.send_document(
            chat_id=m.chat.id,
            document=cookies_file_path,
            caption="Here is the `youtube_cookies.txt` file."
        )
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")
        
@bot.on_message(filters.command("mfile") & filters.private)
async def mfile_handler(client: Client, m: Message):
    try:
        await client.send_document(
            chat_id=m.chat.id,
            document=m_file_path,
            caption="Here is the `main.py` file."
        )
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["stop"]))
async def restart_handler(_, m):
    await m.reply_text("**🚦STOPPED🚦**", True)
    os.execl(sys.executable, sys.executable, *sys.argv)
        
@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, message: Message):
    random_image_url = random.choice(image_urls)
    caption = (
        "𝐇𝐞𝐥𝐥𝐨 𝐃𝐞𝐚𝐫 👋!\n\n➠ 𝐈 𝐚𝐦 𝐚 VK 𝐓𝐞𝐱𝐭 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫 𝐁𝐨𝐭\n\n➠ Can Extract Videos & PDFs"
    )
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=random_image_url,
        caption=caption,
        reply_markup=keyboard
    )

@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(f"<blockquote>The ID of this chat id is:</blockquote>\n`{chat_id}`")

@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    text = (
        f"╭────────────────╮\n"
        f"│✨ **__Your Telegram Info__**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else 'None'}`\n"
        f"├🔹**User ID :** @{update.from_user.username}\n"
        f"├🔹**TG ID :** `{update.from_user.id}`\n"
        f"├🔹**Profile :** {update.from_user.mention}\n"
        f"╰────────────────╯"
    )
    
    await update.reply_text(text=text, disable_web_page_preview=True, reply_markup=BUTTONSCONTACT)

@bot.on_message(filters.command(["help"]))
async def txt_handler(client: Client, m: Message):
    await bot.send_message(m.chat.id, text=(
        f"╭━━━━━━━✦✧✦━━━━━━━╮\n"
        f"💥 @VK_0786BOT\n"
        f"╰━━━━━━━✦✧✦━━━━━━━╯\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
        f"📌 𝗠𝗮𝗶𝗻 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:\n\n"  
        f"➥ /start – Bot Status Check\n"
        f"➥ /drm – Extract from .txt (Auto)\n"
        f"➥ /y2t – YouTube → .txt Converter\n"  
        f"➥ /t2t – Text → .txt Generator\n" 
        f"➥ /stop – Cancel Running Task\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰ \n" 
        f"⚙️ 𝗧𝗼𝗼𝗹𝘀 & 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀: \n\n" 
        f"➥ /cookies – Update YT Cookies\n" 
        f"➥ /id – Get Chat/User ID\n"  
        f"➥ /info – User Details\n"  
        f"➥ /logs – View Bot Activity\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"👤 𝐔𝐬𝐞𝐫 𝐀𝐮𝐭𝐡𝐞𝐧𝐭𝐢𝐜𝐚𝐭𝐢𝐨𝐧: **(OWNER)**\n\n" 
        f"➥ /addauth xxxx – Add User ID\n" 
        f"➥ /remauth xxxx – Remove User ID\n"  
        f"➥ /users – Total User List\n"  
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"📁 𝐂𝐡𝐚𝐧𝐧𝐞𝐥𝐬: **(Auth Users)**\n\n" 
        f"➥ /addchnl -100xxxx – Add\n" 
        f"➥ /remchnl -100xxxx – Remove\n"  
        f"➥ /channels – List - (OWNER)\n"  
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"💡 𝗡𝗼𝘁𝗲:\n\n"  
        f"• Send any link for auto-extraction\n"  
        f"• Supports batch processing\n\n"  
        f"╭────────⊰◆⊱────────╮\n"   
        f" ➠𝐌𝐚𝐝𝐞 𝐁𝐲:[VISHALKUMAR](@VK_0786BOT) 💻\n"
        f"╰────────⊰◆⊱────────╯\n"
    ))
          
@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("**📤 Sending you ....**")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs: {e}")

@bot.on_message(filters.command(["drm"]))
async def drm_handler(bot: Client, m: Message):
    if m.chat.id not in AUTH_USERS and m.chat.id not in CHANNELS_LIST:
        await m.reply_text("__**Oops, you are not authorized to use this command**__")
        return
    await m.reply_text("__**DRM feature is being processed**__")

@bot.on_message(filters.text & filters.private)
async def text_handler(bot: Client, m: Message):
    if m.from_user.is_bot:
        return
    links = m.text
    match = re.search(r'https?://\S+', links)
    if match:
        link = match.group(0)
    else:
        await m.reply_text("<pre><code>Invalid link format.</code></pre>")
        return
        
    editable = await m.reply_text(f"<pre><code>**🔹Processing your link...\n🔁Please wait...⏳**</code></pre>")
    await m.delete()

    await editable.edit("Processing your request...")
    try:
        await editable.edit(f"Link received: {link}\n\nProcessing...")
    except Exception as e:
        await m.reply_text(f"Error: {str(e)}")

bot.run()
