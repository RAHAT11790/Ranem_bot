# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from helper.utils import progress_for_pyrogram, convert
from pyrogram import Client, filters
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, Message)
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.database import db
import os 
import humanize
from PIL import Image
import time

@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
    except:
        return

@Client.on_callback_query(filters.regex('rename'))
async def rename(bot, update):
    user_id = update.message.chat.id
    date = update.message.date
    await update.message.delete()
    await update.message.reply_text("__𝙿𝚕𝚎𝚊𝚜𝚎 𝙴𝚗𝚝𝚎𝚛 𝙽𝚎𝚠 𝙵𝚒𝚕𝚎𝙽𝚊𝚖𝚎...__",    
    reply_to_message_id=update.message.reply_to_message.message_id,  
    reply_markup=ForceReply(True))

@Client.on_callback_query(filters.regex(r'^upload_'))
async def doc(bot, update):
    type = update.data.split("_")[1]
    
    # Extract filename from message text
    message_text = update.message.text
    if "File Name :-" in message_text:
        new_filename = message_text.split("File Name :-")[1].split("\n")[0].strip().replace("`", "")
    else:
        await update.message.edit("❌ **Error: Could not find filename**")
        return
        
    file_path = f"downloads/{new_filename}"
    file = update.message.reply_to_message
    
    if not file:
        await update.message.edit("❌ **Error: Original file not found**")
        return
        
    ms = await update.message.edit("⚠️__**Please wait...**__\n__Downloading file to my server...__")
    c_time = time.time()
    
    try:
        path = await bot.download_media(
            message=file, 
            progress=progress_for_pyrogram,
            progress_args=("⚠️__**Please wait...**__\n\n😈 **Download in progress...**", ms, c_time)
        )
    except Exception as e:
        await ms.edit(f"❌ **Download Error:** {e}")
        return 
        
    if not path:
        await ms.edit("❌ **Failed to download file**")
        return
        
    splitpath = path.split("/downloads/")
    dow_file_name = splitpath[1] if len(splitpath) > 1 else os.path.basename(path)
    old_file_name = f"downloads/{dow_file_name}"
    
    # Create downloads directory if not exists
    os.makedirs("downloads", exist_ok=True)
    
    # Rename file
    try:
        os.rename(old_file_name, file_path)
    except Exception as e:
        await ms.edit(f"❌ **Rename Error:** {e}")
        return
        
    duration = 0
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata and metadata.has("duration"):
            duration = metadata.get('duration').seconds
    except:
        pass
        
    user_id = update.message.chat.id 
    ph_path = None 
    media = getattr(file, file.media.value)
    
    # Get caption and thumbnail from database
    c_caption = await db.get_caption(user_id)
    c_thumb = await db.get_thumbnail(user_id)
    
    # Prepare caption
    if c_caption:
        try:
            caption = c_caption.format(
                filename=new_filename, 
                filesize=humanize.naturalsize(media.file_size), 
                duration=convert(duration)
            )
        except Exception as e:
            caption = f"**{new_filename}**\n\n📦 **Size:** {humanize.naturalsize(media.file_size)}\n⏰ **Duration:** {convert(duration)}"
    else:
        caption = f"**{new_filename}**\n\n📦 **Size:** {humanize.naturalsize(media.file_size)}\n⏰ **Duration:** {convert(duration)}"
    
    # Handle thumbnail
    if c_thumb:
        try:
            ph_path = await bot.download_media(c_thumb)
        except:
            ph_path = None
    elif media.thumbs:
        try:
            ph_path = await bot.download_media(media.thumbs[0].file_id)
        except:
            ph_path = None
    
    # Process thumbnail
    if ph_path and os.path.exists(ph_path):
        try:
            with Image.open(ph_path) as img:
                img = img.convert("RGB")
                img.thumbnail((320, 320))
                img.save(ph_path, "JPEG")
        except:
            ph_path = None
    
    await ms.edit("⚠️__**Please wait...**__\n__Uploading file...__")
    c_time = time.time() 
    
    try:
        if type == "document":
            await bot.send_document(
                chat_id=update.message.chat.id,
                document=file_path,
                thumb=ph_path, 
                caption=caption, 
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__\n__Uploading file...__", ms, c_time)
            )
        elif type == "video": 
            await bot.send_video(
                chat_id=update.message.chat.id,
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__\n__Uploading file...__", ms, c_time)
            )
        elif type == "audio": 
            await bot.send_audio(
                chat_id=update.message.chat.id,
                audio=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__\n__Uploading file...__", ms, c_time)
            ) 
    except Exception as e: 
        await ms.edit(f"❌ **Upload Error:** {e}") 
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)
    
    await ms.delete()
