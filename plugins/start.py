#(©)Codeflix_Bots

import logging
import base64
import random
import re
import string
import time
import asyncio

from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import (
    ADMINS,
    FORCE_MSG,
    START_MSG,
    CUSTOM_CAPTION,
    IS_VERIFY,
    VERIFY_EXPIRE,
    VERIFY_EXPIRE_1,
    VERIFY_EXPIRE_2,
    VERIFY_GAP_TIME,
    SHORTLINK_API,
    SHORTLINK_URL,
    SHORTLINK_API_1,
    SHORTLINK_URL_1,
    SHORTLINK_API_2,
    SHORTLINK_URL_2,
    DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT,
    TUT_VID,
    OWNER_ID,
    VERIFY_IMAGE,
)
from helper_func import subscribed, encode, decode, get_messages, get_shortlink, get_verify_status, update_verify_status, get_exp_time, get_verify_image
from database.database import add_user, del_user, full_userbase, present_user, db_get_link
from shortzy import Shortzy


def is_dual_verification_enabled():
    """Check if dual verification system is fully configured"""
    return bool(SHORTLINK_URL_2 and SHORTLINK_API_2)


async def send_verification_message(message, caption_text, verify_image, reply_markup, client, user_id):
    """Send verification message with or without image and store message ID"""
    sent_msg = None
    if verify_image and isinstance(verify_image, str) and verify_image.strip():
        try:
            print(f"[DEBUG] Attempting to send image: {verify_image}")
            sent_msg = await message.reply_photo(
                photo=verify_image,
                caption=caption_text,
                reply_markup=reply_markup,
                quote=True
            )
            print(f"[DEBUG] Image sent successfully!")
        except Exception as e:
            # If image fails, send text only
            print(f"[DEBUG] Failed to send image: {e}")
            sent_msg = await message.reply(caption_text, reply_markup=reply_markup, quote=True)
    else:
        print(f"[DEBUG] No valid image provided, sending text only. Image value: {verify_image}")
        sent_msg = await message.reply(caption_text, reply_markup=reply_markup, quote=True)
    
    if sent_msg:
        verify_status = await get_verify_status(user_id)
        verify_status['verification_message_id'] = sent_msg.id
        await update_verify_status(user_id, 
                                  verify_token=verify_status['verify_token'],
                                  is_verified=verify_status['is_verified'],
                                  verified_time=verify_status['verified_time'],
                                  link=verify_status['link'],
                                  current_step=verify_status['current_step'],
                                  verify1_expiry=verify_status['verify1_expiry'],
                                  verify2_expiry=verify_expiry['verify2_expiry'],
                                  gap_expiry=verify_status['gap_expiry'])
        # Store the verification message ID separately
        from database.database import user_data
        await user_data.update_one({'_id': user_id}, 
                                  {'$set': {'verify_status.verification_message_id': sent_msg.id}})


@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    owner_id = ADMINS

    # Check if the user is the owner
    if id == owner_id:
        await message.reply("You are the owner! Additional actions can be added here.")

    else:
        # Check the start payload first
        is_verification_link = False
        if len(message.command) > 1:
            start_payload = message.command[1]
            if start_payload.startswith("verify_"):
                is_verification_link = True
        
        # Delete previous verification message only for non-verification links
        if not is_verification_link:
            verify_status = await get_verify_status(id)
            prev_msg_id = verify_status.get('verification_message_id', 0)
            if prev_msg_id > 0:
                try:
                    await client.delete_messages(chat_id=id, message_ids=prev_msg_id)
                    print(f"[DEBUG] Deleted previous verification message {prev_msg_id} for user {id}")
                except Exception as e:
                    print(f"[DEBUG] Could not delete previous verification message: {e}")

        if not await present_user(id):
            try:
                await add_user(id)
            except:
                pass

        verify_status = await get_verify_status(id)
        
        if 'current_step' not in verify_status:
            verify_status['current_step'] = 0
        if 'verify1_expiry' not in verify_status:
            verify_status['verify1_expiry'] = 0
        if 'verify2_expiry' not in verify_status:
            verify_status['verify2_expiry'] = 0
        if 'gap_expiry' not in verify_status:
            verify_status['gap_expiry'] = 0

        original_start_payload = ""
        try:
            if len(message.command) > 1:
                original_start_payload = message.command[1]
                # Store it for later use
                from database.database import user_data
                await user_data.update_one({'_id': id}, 
                                          {'$set': {'verify_status.last_entry_link': original_start_payload}})
        except:
            pass

        now = time.time()
        
        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            if verify_status['verify_token'] != token:
                return await message.reply("Your token is invalid or Expired. Try again by clicking /start")
            
            step = verify_status['current_step']
            
            # STEP 1 verification
            if step == 0 and token == verify_status['verify_token']:
                verify_status['current_step'] = 1
                verify_status['is_verified'] = True
                verify_status['verify1_expiry'] = now + VERIFY_EXPIRE_1
                verify_status['gap_expiry'] = now + VERIFY_GAP_TIME
                verify_status['verify_token'] = ""
                verify_status['verified_time'] = now
                await update_verify_status(id, is_verified=True, current_step=1, 
                                         verify1_expiry=verify_status['verify1_expiry'],
                                         gap_expiry=verify_status['gap_expiry'],
                                         verify_token="", verified_time=now)
                
                last_entry_link = verify_status.get('last_entry_link', '')
                reply_text = f"✅ First verification complete! You now have temporary access.\n\nAccess valid for: {get_exp_time(VERIFY_EXPIRE_1)}"
                
                if last_entry_link:
                    btn = [[InlineKeyboardButton("Get File 🗃️", url=f"https://telegram.me/{client.username}?start={last_entry_link}")]]
                    await message.reply(reply_text, quote=True, reply_markup=InlineKeyboardMarkup(btn))
                else:
                    await message.reply(reply_text, quote=True)
                return
            
            # STEP 2 verification
            elif step == 1 and token == verify_status['verify_token']:
                verify_status['current_step'] = 2
                verify_status['is_verified'] = True
                verify_status['verify2_expiry'] = now + VERIFY_EXPIRE_2
                verify_status['verify_token'] = ""
                verify_status['verified_time'] = now
                await update_verify_status(id, is_verified=True, current_step=2,
                                         verify2_expiry=verify_status['verify2_expiry'],
                                         verify_token="", verified_time=now)
                
                last_entry_link = verify_status.get('last_entry_link', '')
                reply_text = f"✅ Second verification complete! Full access unlocked.\n\nAccess valid for: {get_exp_time(VERIFY_EXPIRE_2)}"
                
                if last_entry_link:
                    btn = [[InlineKeyboardButton("Get File 🗃️", url=f"https://telegram.me/{client.username}?start={last_entry_link}")]]
                    await message.reply(reply_text, quote=True, reply_markup=InlineKeyboardMarkup(btn))
                else:
                    await message.reply(reply_text, quote=True)
                return

        verify_status = await get_verify_status(id)
        step = verify_status['current_step']
        
        if step == 2 and verify_status['verify2_expiry'] > 0 and now >= verify_status['verify2_expiry']:
            verify_status['is_verified'] = False
            verify_status['current_step'] = 1
            verify_status['verify2_expiry'] = 0
            verify_status['gap_expiry'] = 0
            await update_verify_status(id, is_verified=False, current_step=1, verify2_expiry=0, gap_expiry=0)
            step = 1

        if step == 1 and verify_status['verify1_expiry'] > 0 and now >= verify_status['verify1_expiry']:
            verify_status['is_verified'] = False
            verify_status['current_step'] = 0
            verify_status['verify1_expiry'] = 0
            verify_status['gap_expiry'] = 0
            await update_verify_status(id, is_verified=False, current_step=0, verify1_expiry=0, gap_expiry=0)
            step = 0

        elif len(message.text) > 7:
            verify_status = await get_verify_status(id)
            now = time.time()
            step = verify_status['current_step']
            access_allowed = False
            access_type = None
            
            file_id_for_image = ""
            try:
                base64_string = message.text.split(" ", 1)[1]
                _string = await decode(base64_string)
                argument = _string.split("-")
                print(f"[DEBUG] Decoded string: {_string}, argument: {argument}")
                
                if len(argument) == 3:
                    try:
                        f_msg_id_original = int(int(argument[1]) / abs(client.db_channel.id))
                        s_msg_id_original = int(int(argument[2]) / abs(client.db_channel.id))
                        file_id_for_image = f"batch-{f_msg_id_original}-{s_msg_id_original}"
                    except:
                        pass
                    
                    if step == 2 and verify_status['verify2_expiry'] > now:
                        access_allowed = True
                        access_type = "Full Access"
                    elif step == 1 and verify_status['verify1_expiry'] > now:
                        access_allowed = True
                        access_type = "Temporary Access"
                    
                    if access_allowed:
                        try:
                            messages = await get_messages(client, argument)
                            
                            if messages:
                                caption = CUSTOM_CAPTION.format(
                                    filename=messages[0].caption.split('\n')[0] if messages[0].caption else messages[0].document.file_name,
                                    filesize=messages[0].document.file_size,
                                    mimetype=messages[0].document.mime_type,
                                    access_type=access_type
                                ) if CUSTOM_CAPTION else None
                                
                                for msg in messages:
                                    await msg.copy(chat_id=message.from_user.id, caption=caption, protect_content=PROTECT_CONTENT)
                                return
                            else:
                                await message.reply("Something went wrong. Contact the owner.")
                                return
                        except Exception as e:
                            print(f"[ERROR] Failed to send file: {e}")
                            await message.reply("Something went wrong while sending the file. Contact the owner.")
                            return
                    
                    # Verification Logic
                    is_expired_or_not_verified = True
                    if step == 2 and verify_status['verify2_expiry'] > now:
                        is_expired_or_not_verified = False
                    elif step == 1 and verify_status['verify1_expiry'] > now:
                        is_expired_or_not_verified = False
                    
                    if is_expired_or_not_verified:
                        
                        # Check if gap time is active
                        if verify_status['gap_expiry'] > now:
                            gap_time_remaining = verify_status['gap_expiry'] - now
                            await message.reply(f"You must wait {int(gap_time_remaining)} seconds before attempting verification again.")
                            return
                        
                        # Generate new token
                        token = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
                        verify_status['verify_token'] = token
                        await update_verify_status(id, verify_token=token)
                        
                        # Determine next step and shortlink URL
                        if step == 0:
                            shortlink_url = SHORTLINK_URL
                            shortlink_api = SHORTLINK_API
                            shortlink_name = "Verification Link 1"
                            next_step = 1
                            expire_time = VERIFY_EXPIRE_1
                        elif step == 1 and is_dual_verification_enabled():
                            shortlink_url = SHORTLINK_URL_2
                            shortlink_api = SHORTLINK_API_2
                            shortlink_name = "Verification Link 2"
                            next_step = 2
                            expire_time = VERIFY_EXPIRE_2
                        else:
                            # Fallback to step 1 if dual verification is not enabled or step is 1
                            shortlink_url = SHORTLINK_URL
                            shortlink_api = SHORTLINK_API
                            shortlink_name = "Verification Link 1"
                            next_step = 1
                            expire_time = VERIFY_EXPIRE_1
                        
                        # Generate shortlink
                        verify_link = f"https://telegram.me/{client.username}?start=verify_{token}"
                        
                        shortzy = Shortzy(shortlink_url, shortlink_api)
                        short_link = await shortzy.get_shortlink(verify_link)
                        
                        if not short_link:
                            await message.reply("Failed to generate shortlink. Contact the owner.")
                            return
                        
                        # Save link to database
                        await db_get_link(id, short_link)
                        
                        # Prepare buttons
                        btn = [
                            [
                                InlineKeyboardButton(shortlink_name, url=short_link)
                            ]
                        ]
                        
                        # Add Done button if original payload exists
                        if original_start_payload:
                            btn.append([
                                InlineKeyboardButton("Done ✅", url=f"https://telegram.dog/{client.username}?start={original_start_payload}")
                            ])
                        
                        if TUT_VID and isinstance(TUT_VID, str) and TUT_VID.startswith(('http://', 'https://', 'tg://')):
                            btn.append([InlineKeyboardButton('How to use the bot', url=TUT_VID)])
                        
                        verify_image = await get_verify_image(file_id_for_image)
                        if is_expired_or_not_verified:
                            caption_text = (
                                "<blockquote>Your token is expired or not verified. Complete verification to access files.</blockquote>\n\n"
                                f"Token Timeout: {get_exp_time(VERIFY_EXPIRE_1)}"
                            )

                            await send_verification_message(
                                message,
                                caption_text,
                                verify_image,
                                InlineKeyboardMarkup(btn),
                                client,
                                id
                            )

                    else:
                        await message.reply(
                            "<blockquote>Your token is expired or not verified. Complete verification to access files.</blockquote>\n\n"
                            f"Token Timeout: {get_exp_time(VERIFY_EXPIRE_1)}"
                        )
                        return
            except Exception as e:
                print(f"[ERROR] Error in start command processing: {e}")
                await message.reply("Invalid link or something went wrong. Please try again.")
                return
        
        else:
            # Normal /start command without payload
            await message.reply(START_MSG.format(
                first=message.from_user.first_name,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                username=message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ), disable_web_page_preview=True)


@Bot.on_message(filters.command('status') & filters.private & filters.user(ADMINS))
async def status_command(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text="Processing...")
    users = await full_userbase()
    await msg.edit(f"Total users: {len(users)}")


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text="Processing...")
    users = await full_userbase()
    await msg.edit(f"{len(users)} ᴜꜱᴇʀꜱ ᴀʀᴇ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴛɪʟʟ ᴡᴀɪᴛ ʙʀᴏᴏ... </i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except Exception as e:
                unsuccessful += 1
                logging.error(f"Broadcast Error: {e}")
            total += 1
        
        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴍʏ sᴇɴᴘᴀɪ!!</u>

ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: <code>{total}</code>
ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ: <code>{successful}</code>
ʙʟᴏᴄᴋᴇᴅ ᴜꜱᴇʀꜱ: <code>{blocked}</code>
ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ: <code>{deleted}</code>
ᴜɴꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ: <code>{unsuccessful}</code></b></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply("Reply to a message to broadcast.")
        await asyncio.sleep(8)
        await msg.delete()
