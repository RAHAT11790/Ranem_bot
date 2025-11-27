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
import asyncio

@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
    except:
        return

@Client.on_callback_query(filters.regex('rename'))
async def rename(bot, update):
    user_id = update.message.chat.id
    await update.message.delete()
    await update.message.reply_text("__𝙿𝚕𝚎𝚊𝚜𝚎 𝙴𝚗𝚝𝚎𝚛 𝙽𝚎𝚠 𝙵𝚒𝚕𝚎𝙽𝚊𝚖𝚎...__",    
    reply_to_message_id=update.message.reply_to_message.id,  
    reply_markup=ForceReply(True))

@Client.on_callback_query(filters.regex(r'^upload_'))
async def upload_file(bot, update):
    file_type = update.data.split("_")[1]  # document, video, audio
    
    # Get the filename from message text
    message_text = update.message.text
    if "File Name :-" in message_text:
        new_name = message_text.split("File Name :-")[1].split("\n")[0].strip().replace("`", "").strip()
    else:
        await update.message.edit("❌ **Error: Could not find filename**")
        return
    
    # Get the original file message
    original_message = update.message.reply_to_message
    if not original_message:
        await update.message.edit("❌ **Error: Original file not found**")
        return
    
    ms = await update.message.edit("⚠️__**Please wait...**__\n__Downloading file...__")
    
    # Download file
    c_time = time.time()
    try:
        file_path = await bot.download_media(
            message=original_message,
            file_name=f"downloads/{new_name}",
            progress=progress_for_pyrogram,
            progress_args=("⚠️__**Downloading...**__", ms, c_time)
        )
    except Exception as e:
        await ms.edit(f"❌ **Download failed:** {e}")
        return
    
    if not file_path:
        await ms.edit("❌ **Failed to download file**")
        return
    
    # Get file info
    duration = 0
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata and metadata.has("duration"):
            duration = metadata.get('duration').seconds
    except:
        pass
    
    # Get user settings from database
    user_id = update.from_user.id
    custom_caption = await db.get_caption(user_id)
    custom_thumb = await db.get_thumbnail(user_id)
    
    # Prepare caption
    file_size = os.path.getsize(file_path)
    if custom_caption:
        try:
            caption = custom_caption.format(
                filename=new_name,
                filesize=humanize.naturalsize(file_size),
                duration=convert(duration)
            )
        except:
            caption = f"**{new_name}**\n\n💾 Size: {humanize.naturalsize(file_size)}\n⏰ Duration: {convert(duration)}"
    else:
        caption = f"**{new_name}**\n\n💾 Size: {humanize.naturalsize(file_size)}\n⏰ Duration: {convert(duration)}"
    
    # Handle thumbnail
    thumb_path = None
    if custom_thumb:
        try:
            thumb_path = await bot.download_media(custom_thumb, file_name=f"thumb_{user_id}.jpg")
        except:
            thumb_path = None
    
    # Process thumbnail if exists
    if thumb_path and os.path.exists(thumb_path):
        try:
            with Image.open(thumb_path) as img:
                img = img.convert("RGB")
                img.thumbnail((320, 320))
                img.save(thumb_path, "JPEG")
        except Exception as e:
            print(f"Thumbnail error: {e}")
            thumb_path = None
    
    # Upload file
    await ms.edit("⚠️__**Please wait...**__\n__Uploading file...__")
    c_time = time.time()
    
    try:
        if file_type == "document":
            await bot.send_document(
                chat_id=update.message.chat.id,
                document=file_path,
                thumb=thumb_path,
                caption=caption,
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Uploading...**__", ms, c_time)
            )
        elif file_type == "video":
            await bot.send_video(
                chat_id=update.message.chat.id,
                video=file_path,
                caption=caption,
                thumb=thumb_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Uploading...**__", ms, c_time)
            )
        elif file_type == "audio":
            await bot.send_audio(
                chat_id=update.message.chat.id,
                audio=file_path,
                caption=caption,
                thumb=thumb_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Uploading...**__", ms, c_time)
            )
        
        await ms.delete()
        
    except Exception as e:
        await ms.edit(f"❌ **Upload failed:** {e}")
    
    finally:
        # Cleanup
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)
        except:
            pass
