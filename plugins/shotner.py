#(©)CodeXBotz
#Shotner Settings Command - Only for Owner and Admins

from bot import Bot
from config import ADMINS, VERIFY_EXPIRE, VERIFY_EXPIRE_1, VERIFY_EXPIRE_2, VERIFY_GAP_TIME, VERIFY_IMAGE
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os


# Shotner Settings Command - Main Entry Point
@Bot.on_message(filters.private & filters.command('shotner') & filters.user(ADMINS))
async def shotner_settings(client: Bot, message: Message):
    """Display settings menu for owner/admins"""
    
    settings_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⏱️ Verify Expire", callback_data="settings_verify_expire")],
            [InlineKeyboardButton("⏳ Verify Gap Time", callback_data="settings_verify_gap_time")],
            [InlineKeyboardButton("🖼️ Verify Image", callback_data="settings_verify_image")]
        ]
    )
    
    settings_text = """
<b>⚙️ SHOTNER SETTINGS</b>

Configure bot verification settings:

<b>Current Settings:</b>
• <b>Verify Expire:</b> {}, {}, {} (seconds)
• <b>Verify Gap Time:</b> {} (seconds)
• <b>Verify Image:</b> Set

Choose an option to modify:
""".format(VERIFY_EXPIRE, VERIFY_EXPIRE_1, VERIFY_EXPIRE_2, VERIFY_GAP_TIME)
    
    await message.reply(settings_text, reply_markup=settings_keyboard)


# Handle Verify Expire Selection
@Bot.on_callback_query(filters.regex("^settings_verify_expire$"))
async def verify_expire_menu(client: Bot, query: CallbackQuery):
    """Show verify expire options"""
    
    expire_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"VERIFY_EXPIRE ({VERIFY_EXPIRE}s)", callback_data="set_verify_expire_0")],
            [InlineKeyboardButton(f"VERIFY_EXPIRE_1 ({VERIFY_EXPIRE_1}s)", callback_data="set_verify_expire_1")],
            [InlineKeyboardButton(f"VERIFY_EXPIRE_2 ({VERIFY_EXPIRE_2}s)", callback_data="set_verify_expire_2")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")]
        ]
    )
    
    expire_text = """
<b>⏱️ VERIFY EXPIRE SETTINGS</b>

Select which verification expire time to modify:

<b>Current Values:</b>
• <b>VERIFY_EXPIRE:</b> {} seconds
• <b>VERIFY_EXPIRE_1:</b> {} seconds
• <b>VERIFY_EXPIRE_2:</b> {} seconds

Send a number (in seconds) to update the selected option.
""".format(VERIFY_EXPIRE, VERIFY_EXPIRE_1, VERIFY_EXPIRE_2)
    
    await query.message.edit_text(expire_text, reply_markup=expire_keyboard)
    await query.answer()


# Handle Verify Gap Time Selection
@Bot.on_callback_query(filters.regex("^settings_verify_gap_time$"))
async def verify_gap_time_menu(client: Bot, query: CallbackQuery):
    """Show verify gap time option"""
    
    gap_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"VERIFY_GAP_TIME ({VERIFY_GAP_TIME}s)", callback_data="set_verify_gap_time")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")]
        ]
    )
    
    gap_text = """
<b>⏳ VERIFY GAP TIME SETTINGS</b>

Gap time between first and second verification:

<b>Current Value:</b>
• <b>VERIFY_GAP_TIME:</b> {} seconds

Send a number (in seconds) to update this value.
""".format(VERIFY_GAP_TIME)
    
    await query.message.edit_text(gap_text, reply_markup=gap_keyboard)
    await query.answer()


# Handle Verify Image Selection
@Bot.on_callback_query(filters.regex("^settings_verify_image$"))
async def verify_image_menu(client: Bot, query: CallbackQuery):
    """Show verify image option"""
    
    image_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"VERIFY_IMAGE", callback_data="set_verify_image")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")]
        ]
    )
    
    image_text = """
<b>🖼️ VERIFY IMAGE SETTINGS</b>

Verification image URL:

<b>Current Value:</b>
• <b>VERIFY_IMAGE:</b> {verify_image}

Send a URL to update the image link.
Example: https://example.com/image.jpg
""".format(verify_image=VERIFY_IMAGE)
    
    await query.message.edit_text(image_text, reply_markup=image_keyboard)
    await query.answer()


# Back to Settings Button
@Bot.on_callback_query(filters.regex("^back_to_settings$"))
async def back_to_settings(client: Bot, query: CallbackQuery):
    """Go back to main settings menu"""
    
    settings_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⏱️ Verify Expire", callback_data="settings_verify_expire")],
            [InlineKeyboardButton("⏳ Verify Gap Time", callback_data="settings_verify_gap_time")],
            [InlineKeyboardButton("🖼️ Verify Image", callback_data="settings_verify_image")]
        ]
    )
    
    settings_text = """
<b>⚙️ SHOTNER SETTINGS</b>

Configure bot verification settings:

<b>Current Settings:</b>
• <b>Verify Expire:</b> {}, {}, {} (seconds)
• <b>Verify Gap Time:</b> {} (seconds)
• <b>Verify Image:</b> Set

Choose an option to modify:
""".format(VERIFY_EXPIRE, VERIFY_EXPIRE_1, VERIFY_EXPIRE_2, VERIFY_GAP_TIME)
    
    await query.message.edit_text(settings_text, reply_markup=settings_keyboard)
    await query.answer()


# Dictionary to track which setting each user is editing
editing_context = {}


# Handle Verify Expire Selection
@Bot.on_callback_query(filters.regex("^set_verify_expire_"))
async def select_verify_expire(client: Bot, query: CallbackQuery):
    """User selected which expire time to edit"""
    
    expire_type = query.data.split("_")[-1]  # 0, 1, or 2
    
    # Store in context which setting user is editing
    editing_context[query.from_user.id] = {
        "type": "verify_expire",
        "expire_type": expire_type
    }
    
    expire_names = ["VERIFY_EXPIRE", "VERIFY_EXPIRE_1", "VERIFY_EXPIRE_2"]
    
    ask_text = f"""
<b>⏱️ UPDATE {expire_names[int(expire_type)]}</b>

Send a number (in seconds) for the new timeout value.

Example: 300 (for 5 minutes)
"""
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")]]
    )
    
    await query.message.edit_text(ask_text, reply_markup=keyboard)
    await query.answer()


# Handle Verify Gap Time Selection
@Bot.on_callback_query(filters.regex("^set_verify_gap_time$"))
async def select_verify_gap_time(client: Bot, query: CallbackQuery):
    """User selected gap time to edit"""
    
    editing_context[query.from_user.id] = {
        "type": "verify_gap_time"
    }
    
    ask_text = """
<b>⏳ UPDATE VERIFY_GAP_TIME</b>

Send a number (in seconds) for the gap time between first and second verification.

Example: 60 (for 1 minute)
"""
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")]]
    )
    
    await query.message.edit_text(ask_text, reply_markup=keyboard)
    await query.answer()


# Handle Verify Image Selection
@Bot.on_callback_query(filters.regex("^set_verify_image$"))
async def select_verify_image(client: Bot, query: CallbackQuery):
    """User selected image to edit"""
    
    editing_context[query.from_user.id] = {
        "type": "verify_image"
    }
    
    ask_text = """
<b>🖼️ UPDATE VERIFY_IMAGE</b>

Send an image URL for verification prompt.

Example: https://i.ibb.co/HTMRv8Wh/image.jpg
"""
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")]]
    )
    
    await query.message.edit_text(ask_text, reply_markup=keyboard)
    await query.answer()


# Cancel Edit
@Bot.on_callback_query(filters.regex("^cancel_edit$"))
async def cancel_edit(client: Bot, query: CallbackQuery):
    """Cancel current edit"""
    
    user_id = query.from_user.id
    if user_id in editing_context:
        del editing_context[user_id]
    
    await query.message.delete()
    await query.answer("Cancelled!", show_alert=False)


@Bot.on_message(filters.private & filters.text & filters.user(ADMINS))
async def handle_setting_input(client: Bot, message: Message):
    """Handle text input for settings updates"""
    
    user_id = message.from_user.id
    
    # Check if user is editing a setting
    if user_id not in editing_context:
        return
    
    context = editing_context[user_id]
    setting_type = context["type"]
    text = message.text.strip()
    
    try:
        if setting_type == "verify_expire":
            # Update environment variable and config
            expire_type = context["expire_type"]
            value = int(text)
            
            if value < 0:
                await message.reply("❌ Value must be positive!")
                return
            
            expire_names = ["VERIFY_EXPIRE", "VERIFY_EXPIRE_1", "VERIFY_EXPIRE_2"]
            env_var_name = expire_names[int(expire_type)]
            
            # Update environment variable
            os.environ[env_var_name] = str(value)
            
            # In production, you'd update this in a config file or database
            # For now, we'll just update the module-level variable
            import config
            setattr(config, env_var_name, value)
            
            success_msg = f"""
✅ <b>{env_var_name} Updated!</b>

<b>New Value:</b> {value} seconds

The bot will use this new value for future verifications.
"""
            
        elif setting_type == "verify_gap_time":
            value = int(text)
            
            if value < 0:
                await message.reply("❌ Value must be positive!")
                return
            
            os.environ["VERIFY_GAP_TIME"] = str(value)
            
            import config
            config.VERIFY_GAP_TIME = value
            
            success_msg = f"""
✅ <b>VERIFY_GAP_TIME Updated!</b>

<b>New Value:</b> {value} seconds

The bot will use this new value for future verifications.
"""
            
        elif setting_type == "verify_image":
            # Validate URL (basic check)
            if not text.startswith(("http://", "https://")):
                await message.reply("❌ Invalid URL! Must start with http:// or https://")
                return
            
            os.environ["VERIFY_IMAGE"] = text
            
            import config
            config.VERIFY_IMAGE = text
            
            success_msg = f"""
✅ <b>VERIFY_IMAGE Updated!</b>

<b>New URL:</b> {text}

The bot will use this new image for future verification prompts.
"""
        
        # Send success message
        await message.reply(success_msg)
        
        # Clear context
        del editing_context[user_id]
        
    except ValueError:
        if setting_type == "verify_image":
            await message.reply("❌ Invalid URL format!")
        else:
            await message.reply("❌ Please send a valid number!")
