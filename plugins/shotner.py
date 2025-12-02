#(©)CodeXBotz
#Shotner Settings Command - Only for Owner and Admins

from bot import Bot
from config import ADMINS
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os
import config as config_module

# Track which user is editing which setting
editing_context = {}


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('shotner'))
async def shotner_settings(client: Bot, message: Message):
    """Display settings menu for owner/admins"""
    
    verify_expire = getattr(config_module, 'VERIFY_EXPIRE', 300)
    verify_expire_1 = getattr(config_module, 'VERIFY_EXPIRE_1', 300)
    verify_expire_2 = getattr(config_module, 'VERIFY_EXPIRE_2', 300)
    verify_gap_time = getattr(config_module, 'VERIFY_GAP_TIME', 60)
    verify_image = getattr(config_module, 'VERIFY_IMAGE', 'Not set')
    
    settings_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⏱️ Verify Expire", callback_data="settings_verify_expire")],
            [InlineKeyboardButton("⏳ Verify Gap Time", callback_data="settings_verify_gap_time")],
            [InlineKeyboardButton("🖼️ Verify Image", callback_data="settings_verify_image")]
        ]
    )
    
    settings_text = f"""
<b>⚙️ SHOTNER SETTINGS</b>

Configure bot verification settings:

<b>Current Settings:</b>
• <b>Verify Expire:</b> {verify_expire}, {verify_expire_1}, {verify_expire_2} (seconds)
• <b>Verify Gap Time:</b> {verify_gap_time} (seconds)
• <b>Verify Image:</b> {'Set' if verify_image and verify_image != 'Not set' else 'Not set'}

<b>Select an option to modify:</b>
"""
    
    await message.reply_text(settings_text, reply_markup=settings_keyboard)


@Bot.on_callback_query(filters.user(ADMINS) & filters.regex("^settings_verify_expire$"))
async def cb_verify_expire(client: Bot, query: CallbackQuery):
    """Show verify expire options"""
    verify_expire = getattr(config_module, 'VERIFY_EXPIRE', 300)
    verify_expire_1 = getattr(config_module, 'VERIFY_EXPIRE_1', 300)
    verify_expire_2 = getattr(config_module, 'VERIFY_EXPIRE_2', 300)
    
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"VERIFY_EXPIRE: {verify_expire}s", callback_data="set_verify_expire_0")],
            [InlineKeyboardButton(f"VERIFY_EXPIRE_1: {verify_expire_1}s", callback_data="set_verify_expire_1")],
            [InlineKeyboardButton(f"VERIFY_EXPIRE_2: {verify_expire_2}s", callback_data="set_verify_expire_2")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")]
        ]
    )
    
    await query.message.edit_text(
        "<b>⏱️ VERIFY EXPIRE SETTINGS</b>\n\nSelect which expire time to modify:",
        reply_markup=keyboard
    )
    await query.answer()


@Bot.on_callback_query(filters.user(ADMINS) & filters.regex("^set_verify_expire_"))
async def cb_set_verify_expire(client: Bot, query: CallbackQuery):
    """Handle verify expire selection"""
    expire_index = query.data.split("_")[-1]
    
    user_id = query.from_user.id
    editing_context[user_id] = {"type": "verify_expire", "expire_index": expire_index}
    
    expire_names = ["VERIFY_EXPIRE", "VERIFY_EXPIRE_1", "VERIFY_EXPIRE_2"]
    current_value = getattr(config_module, expire_names[int(expire_index)], 300)
    
    await query.message.edit_text(
        f"<b>Updating {expire_names[int(expire_index)]}</b>\n\n"
        f"Current value: <code>{current_value}</code> seconds\n\n"
        f"Send the new value (in seconds):"
    )
    await query.answer()


@Bot.on_callback_query(filters.user(ADMINS) & filters.regex("^settings_verify_gap_time$"))
async def cb_verify_gap_time(client: Bot, query: CallbackQuery):
    """Handle verify gap time setting"""
    verify_gap_time = getattr(config_module, 'VERIFY_GAP_TIME', 60)
    
    user_id = query.from_user.id
    editing_context[user_id] = {"type": "verify_gap_time"}
    
    await query.message.edit_text(
        f"<b>⏳ VERIFY GAP TIME</b>\n\n"
        f"Current value: <code>{verify_gap_time}</code> seconds\n\n"
        f"Send the new value (in seconds):"
    )
    await query.answer()


@Bot.on_callback_query(filters.user(ADMINS) & filters.regex("^settings_verify_image$"))
async def cb_verify_image(client: Bot, query: CallbackQuery):
    """Handle verify image setting"""
    verify_image = getattr(config_module, 'VERIFY_IMAGE', 'Not set')
    
    user_id = query.from_user.id
    editing_context[user_id] = {"type": "verify_image"}
    
    current_display = verify_image if verify_image else "Not set"
    await query.message.edit_text(
        f"<b>🖼️ VERIFY IMAGE</b>\n\n"
        f"Current value: <code>{current_display}</code>\n\n"
        f"Send the new image URL:"
    )
    await query.answer()


@Bot.on_callback_query(filters.user(ADMINS) & filters.regex("^back_to_settings$"))
async def cb_back_to_settings(client: Bot, query: CallbackQuery):
    """Go back to main settings menu"""
    user_id = query.from_user.id
    if user_id in editing_context:
        del editing_context[user_id]
    
    verify_expire = getattr(config_module, 'VERIFY_EXPIRE', 300)
    verify_expire_1 = getattr(config_module, 'VERIFY_EXPIRE_1', 300)
    verify_expire_2 = getattr(config_module, 'VERIFY_EXPIRE_2', 300)
    verify_gap_time = getattr(config_module, 'VERIFY_GAP_TIME', 60)
    verify_image = getattr(config_module, 'VERIFY_IMAGE', 'Not set')
    
    settings_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⏱️ Verify Expire", callback_data="settings_verify_expire")],
            [InlineKeyboardButton("⏳ Verify Gap Time", callback_data="settings_verify_gap_time")],
            [InlineKeyboardButton("🖼️ Verify Image", callback_data="settings_verify_image")]
        ]
    )
    
    settings_text = f"""
<b>⚙️ SHOTNER SETTINGS</b>

Configure bot verification settings:

<b>Current Settings:</b>
• <b>Verify Expire:</b> {verify_expire}, {verify_expire_1}, {verify_expire_2} (seconds)
• <b>Verify Gap Time:</b> {verify_gap_time} (seconds)
• <b>Verify Image:</b> {'Set' if verify_image and verify_image != 'Not set' else 'Not set'}

<b>Select an option to modify:</b>
"""
    
    await query.message.edit_text(settings_text, reply_markup=settings_keyboard)
    await query.answer()


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.text & ~filters.command(["start", "batch", "genlink", "users", "broadcast", "stats", "shotner", "id"]))
async def handle_setting_input(client: Bot, message: Message):
    """Handle text input for settings updates"""
    
    user_id = message.from_user.id
    
    if user_id not in editing_context:
        return
    
    context = editing_context[user_id]
    setting_type = context["type"]
    text = message.text.strip()
    
    try:
        if setting_type == "verify_expire":
            expire_index = int(context["expire_index"])
            value = int(text)
            
            if value < 0:
                await message.reply("❌ Value must be positive!")
                return
            
            expire_names = ["VERIFY_EXPIRE", "VERIFY_EXPIRE_1", "VERIFY_EXPIRE_2"]
            env_var_name = expire_names[expire_index]
            
            os.environ[env_var_name] = str(value)
            setattr(config_module, env_var_name, value)
            
            del editing_context[user_id]
            
            await message.reply(
                f"✅ <b>{env_var_name} Updated!</b>\n\n"
                f"<b>New Value:</b> {value} seconds\n\n"
                f"The bot will use this new value for future verifications."
            )
            
        elif setting_type == "verify_gap_time":
            value = int(text)
            
            if value < 0:
                await message.reply("❌ Value must be positive!")
                return
            
            os.environ['VERIFY_GAP_TIME'] = str(value)
            setattr(config_module, 'VERIFY_GAP_TIME', value)
            
            del editing_context[user_id]
            
            await message.reply(
                f"✅ <b>VERIFY_GAP_TIME Updated!</b>\n\n"
                f"<b>New Value:</b> {value} seconds\n\n"
                f"The bot will use this new value for future verifications."
            )
            
        elif setting_type == "verify_image":
            if not text.startswith(('http://', 'https://')):
                await message.reply("❌ Invalid URL! Please send a valid image URL starting with http:// or https://")
                return
            
            os.environ['VERIFY_IMAGE'] = text
            setattr(config_module, 'VERIFY_IMAGE', text)
            
            del editing_context[user_id]
            
            await message.reply(
                f"✅ <b>VERIFY_IMAGE Updated!</b>\n\n"
                f"<b>New Value:</b> <code>{text}</code>\n\n"
                f"The bot will use this new image for future verifications."
            )
    
    except ValueError:
        await message.reply("❌ Invalid input! Please send a valid number or URL.")
    except Exception as e:
        await message.reply(f"❌ Error updating setting: {str(e)}")
