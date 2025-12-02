from bot import Bot
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from config import ADMINS
import base64

@Bot.on_message(filters.private & filters.command('shortner'))
async def shortner(bot: Bot, message: Message):
    """
    Generate a shareable link for the current chat/user
    Usage: /shortner
    """
    user_id = message.from_user.id
    
    # Create a unique identifier for this user session
    # Encode the user ID in base64 for a shortened link
    encoded_id = base64.urlsafe_b64encode(str(user_id).encode()).decode().strip('=')
    
    # Create the shareable link with "get-" prefix to match existing patterns
    shareable_link = f"https://telegram.me/{(await bot.get_me()).username}?start=get-{encoded_id}"
    
    # Create inline keyboard with share button
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Share URL", url=f"https://t.me/share/url?url={shareable_link}")]
        ]
    )
    
    # Send the link
    await message.reply_text(
        f"<b>Here is your link</b>\n\n{shareable_link}",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
