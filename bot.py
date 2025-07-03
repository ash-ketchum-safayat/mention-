import random
import time
import datetime
import os, logging, asyncio, time, datetime
from telethon import Button
from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest, EditAdminRequest
from telethon.errors import UserNotParticipantError
from telethon.tl.types import ChatAdminRights, PeerUser
from tinydb import TinyDB, Query

# === Logging ===
logging.basicConfig(level=logging.INFO, format='%(name)s - [%(levelname)s] - %(message)s')
LOGGER = logging.getLogger(__name__)

# === Config ===
api_id = 4226067
api_hash = "2d01711f0566de2309b633f49542e7e2"
bot_token = "8183522431:AAHDQy3xZj5kE37ew6qIQw0-Cy9h0AYw_7M"
bot_owner_id = [6279412066, 7800979183]
log_chat_id = -10002662838  # Your log group

from telethon import TelegramClient, events



pic_urls = [
    "https://files.catbox.moe/eviz7e.jpg",
    "https://files.catbox.moe/tnjrqb.jpg",
    "https://files.catbox.moe/xycejx.jpg",
    "https://files.catbox.moe/jcjqhs.jpg",
    "https://files.catbox.moe/cidhop.jpg",
    "https://files.catbox.moe/qy1ti2.jpg",
    "https://files.catbox.moe/yriq4n.jpg"
]

menu_images = [
    "https://files.catbox.moe/eviz7e.jpg",
    "https://files.catbox.moe/tnjrqb.jpg",
    "https://files.catbox.moe/xycejx.jpg",
    "https://files.catbox.moe/jcjqhs.jpg",
    "https://files.catbox.moe/cidhop.jpg",
    "https://files.catbox.moe/qy1ti2.jpg",
    "https://files.catbox.moe/yriq4n.jpg"
]

# === Init ===

client = TelegramClient('session', api_id, api_hash).start(bot_token=bot_token)
bot_start_time = time.time()

emojis = ["😀", "😍", "🤣", "👍", "🌟", "🎉", "👏", "🤔", "😎", "🥰", "🥳", "🙌", "🌺", "🎈", "🌞", "🌍", "🎶", "🍕", "🍦", "🚀"]
bot_start_time = time.time()

# === TinyDB ===

import json, os

def fix_tinydb(file):
    if not os.path.exists(file):
        return
    with open(file) as f:
        try:
            data = json.load(f)
            if isinstance(data, list) or not isinstance(data.get("afk", {}), dict):
                raise Exception("Corrupted")
        except:
            print("⚠️ Resetting corrupted TinyDB file.")
            with open(file, "w") as f:
                json.dump({
                    "_default": {},
                    "users": {},
                    "groups": {},
                    "channels": {},
                    "afk": {}
                }, f, indent=4)

fix_tinydb("bot_data.json")
fix_tinydb("bot_data.json")
# === Commands ===
db = TinyDB("bot_data.json")
users_table = db.table("users")
groups_table = db.table("groups")
channels_table = db.table("channels")
gban_table = db.table("gbans")
gmute_table = db.table("gmutes")
afk_table = db.table("afk")  # ✅ Add this

warnings_table = db.table("warnings")



blocked_keywords = [
    "porn", "scam", "grabify", "joinchat", "bit.ly", "adf.ly", "tinyurl", "adult", "virus", "trojan", "darkweb"
]



import io
import traceback
import contextlib

@client.on(events.NewMessage(pattern="^/cmd(?:\s+)?([\s\S]*)"))
async def cmd_handler(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ You are not authorized to use this command.")

    code = event.pattern_match.group(1)
    if not code:
        return await event.reply("⚠️ Send some code after `/cmd`.")

    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            exec_env = {
                'client': client,
                'event': event,
                'asyncio': asyncio,
                '__name__': '__main__'
            }
            exec(f'async def __cmd_exec():\n    ' + '\n    '.join(code.split('\n')), exec_env)
            result = await exec_env['__cmd_exec']()
            output = stdout.getvalue()
            final_output = f"{output}\n{result}" if result is not None else output or "✅ Done!"
    except Exception as e:
        final_output = f"❌ Error:\n{traceback.format_exc()}"

    # Truncate if too long
    if len(final_output) > 4096:
        final_output = final_output[:4000] + "\n\n⚠️ Output too long, truncated."

    await event.reply(f"📤 Output:\n```{final_output.strip()}```", parse_mode="md")



import subprocess

@client.on(events.NewMessage(pattern="^/sh (.+)"))
async def run_shell(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ Not authorized.")

    cmd = event.pattern_match.group(1)
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
        if not output:
            output = "✅ Executed (no output)"
    except subprocess.CalledProcessError as e:
        output = f"❌ Shell Error:\n{e.output.decode()}"

    await event.reply(f"📟 Shell Output:\n`{output.strip()[:4000]}`", parse_mode='md')

@client.on(events.NewMessage(pattern="^/pyinspect (.+)"))
async def pyinspect(event):
    if event.sender_id != bot_owner_id:
        return

    target = event.pattern_match.group(1)
    try:
        obj = eval(target, {'client': client, 'event': event, 'asyncio': asyncio})
        info = str(dir(obj))
        await event.reply(f"🧬 Attributes of `{target}`:\n`{info}`", parse_mode="md")
    except Exception as e:
        await event.reply(f"❌ Eval error:\n`{str(e)}`", parse_mode="md")

@client.on(events.NewMessage(pattern="^/restart$"))
async def restart_bot(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ Not authorized.")
    await event.reply("♻️ Restarting bot...")
    await client.disconnect()
    os.execl(sys.executable, sys.executable, *sys.argv)

@client.on(events.NewMessage(pattern="^/logs$"))
async def send_logs(event):
    if event.sender_id != bot_owner_id:
        return
    if os.path.exists("bot.log"):
        await event.reply("📄 Here's your log file:", file="bot.log")
    else:
        await event.reply("⚠️ Log file not found.")

@client.on(events.NewMessage(pattern="^/backupdb$"))
async def backup_db(event):
    if event.sender_id != bot_owner_id:
        return
    if os.path.exists("bot_data.json"):
        await event.reply("🗂 Here's your DB backup:", file="bot_data.json")
    else:
        await event.reply("❌ Database not found.")

@client.on(events.NewMessage(pattern="^/chats$"))
async def list_chats(event):
    if event.sender_id != bot_owner_id:
        return

    text = "**📋 Chat List:**\n\n"

    for group in groups_table.all():
        text += f"👥 Group: `{group['id']}`\n"

    for chan in channels_table.all():
        text += f"📢 Channel: `{chan['id']}`\n"

    await event.reply(text or "No chats found.", parse_mode="md")

@client.on(events.NewMessage(pattern="^/pfp$"))
async def get_pfp(event):
    if not event.is_reply:
        return await event.reply("⚠️ Reply to a user to get their profile photo.")
    
    reply = await event.get_reply_message()
    user = await client.get_entity(reply.sender_id)
    photos = await client.get_profile_photos(user)
    if photos.total == 0:
        return await event.reply("🚫 No profile photo found.")
    
    await client.send_file(event.chat_id, photos[0])

@client.on(events.ChatAction)
async def detect_suspicious(event):
    user = await client.get_entity(event.user_id)
    reason = []
    if user.username and "bot" in user.username.lower():
        reason.append("🤖 Username contains 'bot'")
    if user.first_name.lower() in ["admin", "support"]:
        reason.append("⚠️ Fake-looking name")
    if len(user.username or "") < 5:
        reason.append("📛 Short username")
    if reason:
        await client.send_message(event.chat_id, f"🕵️ Suspicious user joined:\n👤 `{user.first_name}` ({user.id})\nReason(s): " + ", ".join(reason))

import importlib.util
import sys
import os

loaded_plugins = {}

@client.on(events.NewMessage(pattern="^/plugins$"))
async def list_plugins(event):
    if event.sender_id != bot_owner_id:
        return
    os.makedirs("plugins", exist_ok=True)
    plugin_files = [f for f in os.listdir("plugins") if f.endswith(".py")]
    
    loaded = []
    for name, module in loaded_plugins.items():
        meta = []
        if hasattr(module, "__version__"):
            meta.append(f"v{module.__version__}")
        if hasattr(module, "__author__"):
            meta.append(f"by {module.__author__}")
        loaded.append(f"✅ `{name}` {' '.join(meta)}")
    
    unloaded = [f"🪶 `{f}`" for f in plugin_files if f.replace(".py", "") not in loaded_plugins]

    result = "**📦 Plugins Status:**\n\n" + "\n".join(loaded + unloaded)
    await event.reply(result)

@client.on(events.NewMessage(pattern="^/reloadplugin (.+)$"))
async def reload_plugin(event):
    if event.sender_id != bot_owner_id:
        return
    filename = event.pattern_match.group(1)
    module_name = filename.replace(".py", "")
    filepath = f"plugins/{filename}"

    if module_name not in loaded_plugins:
        return await event.reply("⚠️ Plugin is not loaded.")

    try:
        # Unload
        del sys.modules[module_name]
        del loaded_plugins[module_name]

        # Load
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        loaded_plugins[module_name] = module

        if hasattr(module, "register"):
            module.register(client)

        await event.reply(f"♻️ Plugin `{filename}` reloaded.")
    except Exception as e:
        await event.reply(f"❌ Failed to reload plugin:\n`{str(e)}`")

last_deleted = {}
message_cache = {}  # chat_id -> {msg_id: message}

@client.on(events.NewMessage)
async def cache_messages(event):
    if not event.is_private:
        if event.chat_id not in message_cache:
            message_cache[event.chat_id] = {}
        message_cache[event.chat_id][event.id] = event.message
        # Optional: Limit cache size per group
        if len(message_cache[event.chat_id]) > 1000:
            message_cache[event.chat_id].pop(next(iter(message_cache[event.chat_id])))

@client.on(events.NewMessage(pattern="^/snipe$"))
async def snipe(event):
    msg = last_deleted.get(event.chat_id)
    if msg:
        content = msg.text or msg.message or "<no text>"
        await event.reply(f"💀 Sniped:\n{content}")
    else:
        await event.reply("❌ Nothing to snipe recently.")



@client.on(events.NewMessage(pattern="^/warn$"))
async def warn_user(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Reply to the user you want to warn.")

    user_id = (await event.get_reply_message()).sender_id
    chat_id = event.chat_id
    key = f"{chat_id}_{user_id}"
    record = warn_table.get(Query().key == key) or {"key": key, "count": 0}

    record["count"] += 1
    warn_table.upsert(record, Query().key == key)

    if record["count"] >= 3:
        await client.edit_permissions(chat_id, user_id, view_messages=False)
        warn_table.remove(Query().key == key)
        return await event.reply("🚫 User banned after 3 warnings.")
    
    await event.reply(f"⚠️ User warned ({record['count']}/3)")

@client.on(events.NewMessage(pattern="^/unwarn$"))
async def unwarn_user(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Reply to the user to remove a warning.")

    user_id = (await event.get_reply_message()).sender_id
    key = f"{event.chat_id}_{user_id}"
    record = warn_table.get(Query().key == key)
    if not record:
        return await event.reply("✅ No warnings found.")
    
    record["count"] = max(0, record["count"] - 1)
    warn_table.upsert(record, Query().key == key)
    await event.reply(f"✅ Warning removed ({record['count']}/3)")

@client.on(events.NewMessage(pattern="^/warnings$"))
async def check_warnings(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Reply to a user to check warnings.")
    
    user_id = (await event.get_reply_message()).sender_id
    key = f"{event.chat_id}_{user_id}"
    record = warn_table.get(Query().key == key)
    await event.reply(f"⚠️ Warnings: {record['count'] if record else 0}/3")

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
    from_user = await event.get_sender()
    user_id = from_user.id

    # Save user to DB (no duplicates)
    if not users_table.contains(Query().id == user_id):
        users_table.insert({"id": user_id})

    # 📥 In Private Chat
    if event.is_private:
        bot_user = await client.get_me()
        await client.send_message(
            event.chat_id,
            f"👋 Hello, [{from_user.first_name}](tg://user?id={user_id})!\n\n"
            "I'm **TagAllXBot**, your all-in-one group assistant.\n"
            "Click below to explore features or add me to your group.",
            buttons=[
                [Button.inline("📂 Open Menu", b"main_menu")],
                [Button.url("➕ Add Me to Group", f"https://t.me/{bot_user.username}?startgroup=true")],
                [Button.url("📢 Updates", "https://t.me/AshxBots"), Button.url("👤 Owner", "https://t.me/AshKetchum_001")]
            ],
            parse_mode="md"
        )

    # 👥 In Group or Channel
    else:
        await event.reply("✅ **Bot is online and working!**\nUse `/menu` to explore features.", parse_mode="md")
@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
    await event.reply(
        "**Help Menu of @TagAllxBot**\n\n"
        "Commands: /mention | /emoji\n"
        "__Use with any message or reply.__\n"
        "**Examples:**\n"
        "`/mention Good Morning!`\n"
        "`/emoji Hello World!`\n"
        "`/promote Admin` (reply)\n"
        "`/fullpromote Boss` (reply)\n\n"
        "Join @AshxBots for updates.",
        link_preview=False,
        buttons=[[Button.url('📦 Owner', 'https://t.me/AshKetchum_001')]]
    )

@client.on(events.NewMessage(pattern="^/(tagall|mention|mentionall|utag|loud) ?(.*)"))
async def mention_all(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.reply("__This command can only be used in groups and channels!__")

    try:
        participant = await client(GetParticipantRequest(chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("__Only admins can mention all!__")
    except UserNotParticipantError:
        return await event.reply("__Only admins can mention all!__")

    if chat_id in spam_chats:
        return await event.reply("**There is already a process ongoing...**")

    msg = event.pattern_match.group(2) or "Hello everyone!"
    spam_chats.append(chat_id)

    usrnum = 0
    usrtxt = ''
    async for usr in client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        usrnum += 1
        usrtxt += f"<a href='tg://user?id={usr.id}'><b>{usr.first_name}</b></a>, "
        if usrnum == 7:
            await client.send_message(chat_id, f"{usrtxt}\n\n<b>{msg}</b>", parse_mode='html')
            await asyncio.sleep(1.5)
            usrnum = 0
            usrtxt = ''

    spam_chats.remove(chat_id)
    await client.send_message(chat_id, "<b>✅ Mentioning All Users Done</b>\nJoin @AshxBots", parse_mode='html')

@client.on(events.NewMessage(pattern="^/emoji ?(.*)"))
async def mention_with_emoji(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.reply("__This command can only be used in groups and channels!__")

    try:
        participant = await client(GetParticipantRequest(chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("__Only admins can mention all!__")
    except UserNotParticipantError:
        return await event.reply("__Only admins can mention all!__")

    if chat_id in spam_chats:
        return await event.reply("**There is already a process ongoing...**")

    if not event.is_reply:
        return await event.reply("__Reply to a message to mention others with emoji!__")

    msg = await event.get_reply_message()
    spam_chats.append(chat_id)

    usrnum = 0
    usrtxt = ''
    async for usr in client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        usrnum += 1
        usrtxt += f"<a href='tg://user?id={usr.id}'><b>{random.choice(emojis)}</b></a>, "
        if usrnum == 30:
            await msg.reply(usrtxt, parse_mode='html')
            await asyncio.sleep(1.5)
            usrnum = 0
            usrtxt = ''

    spam_chats.remove(chat_id)
    await client.send_message(chat_id, "<b>✅ Mentioning All Users Done</b>", parse_mode='html')

@client.on(events.NewMessage(pattern="^/(stop|stopall|cancel|unmention|untagall)$"))
async def stop_tagging(event):
    chat_id = event.chat_id
    if chat_id in spam_chats:
        spam_chats.remove(chat_id)
        return await event.reply("__Stopped mentioning users.__")
    await event.reply("__There is no process ongoing...__")

@client.on(events.NewMessage(pattern="^/id$"))
async def get_id(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        await event.reply(f"🆔 User ID: `{reply.sender_id}`\n🗨 Message ID: `{reply.id}`")
    else:
        await event.reply(f"🆔 Your ID: `{event.sender_id}`\n📍Chat ID: `{event.chat_id}`")

@client.on(events.NewMessage(pattern="^/dice$"))
async def dice(event):
    await client.send_message(event.chat_id, file='🎲')

import random

@client.on(events.NewMessage(pattern="^/roll$"))
async def roll(event):
    dice_types = ['🎯', '🏀', '🎳', '🎰', '⚽']  # Telegram-supported types
    emoji = random.choice(dice_types)
    await client.send_message(event.chat_id, file=emoji)

@client.on(events.NewMessage(pattern="^/tagadmins$"))
async def tag_admins(event):
    if event.is_private:
        return await event.reply("❌ Only in groups.")
    msg = "⚠️ Calling All Admins:\n"
    async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantAdmin):
        msg += f"[{user.first_name}](tg://user?id={user.id}) "
    await event.reply(msg, parse_mode='md')

@client.on(events.NewMessage(pattern="^/ban$"))
async def ban_user(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Reply to a user in a group to ban.")
    reply = await event.get_reply_message()
    try:
        await client.edit_permissions(event.chat_id, reply.sender_id, view_messages=False)
        await event.reply(f"🚫 Banned [{reply.sender.first_name}](tg://user?id={reply.sender_id})", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Error:\n`{e}`")

@client.on(events.NewMessage(pattern="^/unban$"))
async def unban_user(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Reply to a user in a group to unban.")
    reply = await event.get_reply_message()
    try:
        await client.edit_permissions(event.chat_id, reply.sender_id, view_messages=True)
        await event.reply(f"✅ Unbanned [{reply.sender.first_name}](tg://user?id={reply.sender_id})", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Error:\n`{e}`")

@client.on(events.NewMessage(pattern="^/info$"))
async def userinfo(event):
    reply = await event.get_reply_message()
    user = await client.get_entity(reply.sender_id if reply else event.sender_id)
    await event.reply(
        f"**👤 User Info:**\n\n"
        f"📌 Name: `{user.first_name}`\n"
        f"🆔 User ID: `{user.id}`\n"
        f"👥 Username: `@{user.username}`\n"
        f"🌐 Data Center ID: `{user.photo.dc_id if user.photo else 'N/A'}`",
        parse_mode='md'
    )

@client.on(events.NewMessage(pattern="^/(who|whois)$"))
async def whois(event):
    if not event.is_reply:
        return await event.reply("Reply to a user to get info.")
    reply = await event.get_reply_message()
    user = await client.get_entity(reply.sender_id)
    await event.reply(
        f"**WHOIS:**\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"📝 Name: `{user.first_name}`\n"
        f"🏷 Username: @{user.username}" if user.username else "❌ No username",
        parse_mode='md'
    )

@client.on(events.NewMessage(pattern="^/clear (\d+)$"))
async def clear_messages(event):
    if not event.is_group:
        return await event.reply("⚠️ Use in groups.")
    try:
        participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("Only admins can use this.")
    except:
        return await event.reply("Only admins can use this.")
    
    count = int(event.pattern_match.group(1))
    msgs = [m async for m in client.iter_messages(event.chat_id, limit=count + 1)]
    await client.delete_messages(event.chat_id, [m.id for m in msgs])
    await event.respond(f"✅ Deleted `{count}` messages.", parse_mode='md')



@client.on(events.NewMessage(pattern="^/groupinfo$"))
async def groupinfo(event):
    if not event.is_group:
        return await event.reply("⚠️ Use in group only.")
    entity = await event.get_chat()
    members = await client.get_participants(event.chat_id)
    admins = [m async for m in client.iter_participants(event.chat_id, filter=ChannelParticipantAdmin)]
    await event.reply(
        f"**📊 Group Info:**\n\n"
        f"🧷 Title: `{entity.title}`\n"
        f"🆔 ID: `{event.chat_id}`\n"
        f"👤 Members: `{len(members)}`\n"
        f"🛡 Admins: `{len(admins)}`"
    )

@client.on(events.NewMessage(pattern="^/tagbots$"))
async def tag_bots(event):
    if not event.is_group:
        return await event.reply("Use this in group only.")
    msg = "**🤖 Bots in Group:**\n"
    count = 0
    async for user in client.iter_participants(event.chat_id):
        if user.bot:
            count += 1
            msg += f"• [{user.first_name}](tg://user?id={user.id})\n"
    await event.reply(msg if count else "❌ No bots found!", parse_mode='md')

@client.on(events.NewMessage(pattern="^/inactive$"))
async def tag_inactive(event):
    inactive = []
    async for user in client.iter_participants(event.chat_id):
        if user.status and hasattr(user.status, "was_online"):
            last_seen = user.status.was_online
            if (datetime.datetime.now(datetime.timezone.utc) - last_seen).days > 30:
                inactive.append(user)
    if not inactive:
        return await event.reply("✅ No inactive users.")
    text = "😴 Inactive users:\n"
    text += "\n".join(f"• [{u.first_name}](tg://user?id={u.id})" for u in inactive[:30])
    await event.reply(text, parse_mode='md')

@client.on(events.NewMessage(pattern="^/broadcast$"))
async def broadcast(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ You are not authorized to use this command.")
    if not event.is_reply:
        return await event.reply("❌ Reply to the message you want to broadcast.")

    message = await event.get_reply_message()
    sent_users = sent_groups = sent_channels = 0
    failed_users = failed_groups = failed_channels = 0

    for user in users_table.all():
        user_id = user.get("id")
        if not user_id: continue
        try:
            await client.send_message(int(user_id), message)
            sent_users += 1
        except Exception as e:
            LOGGER.warning(f"Failed to send to user {user_id}: {e}")
            failed_users += 1

    for group in groups_table.all():
        group_id = group.get("id")
        if not group_id: continue
        try:
            await client.send_message(int(group_id), message)
            sent_groups += 1
        except Exception as e:
            LOGGER.warning(f"Failed to send to group {group_id}: {e}")
            failed_groups += 1

    for channel in channels_table.all():
        channel_id = channel.get("id")
        if not channel_id: continue
        try:
            await client.send_message(int(channel_id), message)
            sent_channels += 1
        except Exception as e:
            LOGGER.warning(f"Failed to send to channel {channel_id}: {e}")
            failed_channels += 1

    report = (
        "**🔶 Broadcast Summary **\n\n"
        f"👤 Users: `{sent_users}` / `{failed_users}`\n"
        f"👥 Groups: `{sent_groups}` / `{failed_groups}`\n"
        f"📢 Channels: `{sent_channels}` / `{failed_channels}`"
    )
    await event.reply(report)

import psutil
from pathlib import Path

@client.on(events.NewMessage(pattern="^/botstats$"))
async def bot_stats(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ You are not authorized to use this command.")

    uptime = str(datetime.timedelta(seconds=int(time.time() - bot_start_time)))

    total_users = len(users_table)
    total_groups = len(groups_table)
    total_channels = len(channels_table)

    db_file = Path("bot_data.json")
    db_size = db_file.stat().st_size / 1024 if db_file.exists() else 0

    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_used = f"{memory.used // (1024 ** 2)}MB / {memory.total // (1024 ** 2)}MB"

    await event.reply(
        f"**🤖 Bot Statistics**\n\n"
        f"🟢 **Status:** Online\n"
        f"⏱ **Uptime:** `{uptime}`\n\n"
        f"📦 **Database Size:** `{db_size:.2f} KB`\n"
        f"📊 **CPU Usage:** `{cpu_percent}%`\n"
        f"💾 **RAM Usage:** `{memory_used}`\n\n"
        f"👤 **Users:** `{total_users}`\n"
        f"👥 **Groups:** `{total_groups}`\n"
        f"📢 **Channels:** `{total_channels}`\n\n"
        f"💡 **Commands Loaded:** `~{len(client._event_builders)}`"
    )

@client.on(events.ChatAction)
async def track_chats(event):
    chat = await event.get_chat()
    chat_id = chat.id
    if event.user_added or event.user_joined:
        if chat.broadcast:
            if not channels_table.contains(Query().id == chat_id):
                channels_table.insert({"id": chat_id})
        elif chat.megagroup:
            if not groups_table.contains(Query().id == chat_id):
                groups_table.insert({"id": chat_id})
        else:
            if not users_table.contains(Query().id == chat_id):
                users_table.insert({"id": chat_id})

@client.on(events.NewMessage(pattern="^/promote$"))
async def promote(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Use in group and reply to user.")
    reply = await event.get_reply_message()
    rights = ChatAdminRights(delete_messages=True, invite_users=True, pin_messages=True, manage_call=True)
    try:
        await client(EditAdminRequest(event.chat_id, PeerUser(reply.sender_id), rights, "Group Admin"))
        await event.reply(f"✅ Promoted [{reply.sender.first_name}](tg://user?id={reply.sender_id})", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Error:\n`{str(e)}`")

@client.on(events.NewMessage(pattern="^/fullpromote$"))
async def full_promote(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Use in group and reply to user.")
    reply = await event.get_reply_message()
    rights = ChatAdminRights(
        change_info=True, delete_messages=True, ban_users=True, invite_users=True,
        pin_messages=True, add_admins=True, anonymous=True, manage_call=True
    )
    try:
        await client(EditAdminRequest(event.chat_id, PeerUser(reply.sender_id), rights, "Full Admin"))
        await event.reply(f"✅ Fully Promoted [{reply.sender.first_name}](tg://user?id={reply.sender_id})", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Error:\n`{str(e)}`")

@client.on(events.NewMessage(pattern="^/(contact|owner|about|support)$"))
async def contact_info(event):
    await event.reply(
        file="https://files.catbox.moe/4xwtlr.jpg",
        message="📞 **Contact Information**\n\n🔹 **Updates**: @AshxBots\n🔹 Developer: @AshKetchum_001",
        buttons=[[Button.url("❤️ Developer", "https://t.me/AshKetchum_001")]],
        link_preview=False
    )

@client.on(events.NewMessage(pattern="^/tagrecent$"))
async def tag_recent(event):
    if event.is_private:
        return
    recent = []
    async for user in client.iter_participants(event.chat_id):
        if user.status and hasattr(user.status, "was_online"):
            last_seen = user.status.was_online
            if (datetime.datetime.now(datetime.timezone.utc) - last_seen).days < 2:
                recent.append(user)
    
    msg = "🔔 Active Users:\n" + ", ".join([f"<a href='tg://user?id={u.id}'>{u.first_name}</a>" for u in recent[:20]])
    await event.reply(msg, parse_mode="html")

lock_table = db.table("locks")

@client.on(events.NewMessage(pattern="^/lock (.+)"))
async def lock_type(event):
    if not event.is_group:
        return await event.reply("⚠️ Use this command in a group.")
    try:
        participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("❌ Only admins can lock content.")
    except:
        return await event.reply("❌ Only admins can lock content.")

    lock_type = event.pattern_match.group(1).lower()
    valid_locks = ["link", "sticker", "photo", "video", "gif", "document", "forward", "all"]
    if lock_type not in valid_locks:
        return await event.reply(f"⚠️ Invalid lock type.\nValid types: {', '.join(valid_locks)}")

    if lock_type == "all":
        for lt in valid_locks[:-1]:
            key = f"{event.chat_id}:{lt}"
            if not lock_table.contains(Query().key == key):
                lock_table.insert({"key": key})
        return await event.reply("🔒 Locked everything!")

    key = f"{event.chat_id}:{lock_type}"
    if not lock_table.contains(Query().key == key):
        lock_table.insert({"key": key})
        await event.reply(f"🔒 Locked `{lock_type}` messages.")
    else:
        await event.reply(f"✅ `{lock_type}` is already locked.")


@client.on(events.NewMessage(pattern="^/unlock (.+)"))
async def unlock_type(event):
    if not event.is_group:
        return await event.reply("⚠️ Use this command in a group.")
    try:
        participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("❌ Only admins can unlock content.")
    except:
        return await event.reply("❌ Only admins can unlock content.")

    lock_type = event.pattern_match.group(1).lower()
    valid_locks = ["link", "sticker", "photo", "video", "gif", "document", "forward", "all"]
    if lock_type not in valid_locks:
        return await event.reply(f"⚠️ Invalid unlock type.\nValid types: {', '.join(valid_locks)}")

    if lock_type == "all":
        count = 0
        for lt in valid_locks[:-1]:
            key = f"{event.chat_id}:{lt}"
            if lock_table.contains(Query().key == key):
                lock_table.remove(Query().key == key)
                count += 1
        return await event.reply(f"🔓 Unlocked `{count}` types.")

    key = f"{event.chat_id}:{lock_type}"
    if lock_table.contains(Query().key == key):
        lock_table.remove(Query().key == key)
        await event.reply(f"🔓 Unlocked `{lock_type}` messages.")
    else:
        await event.reply(f"✅ `{lock_type}` is not locked.")

@client.on(events.NewMessage(pattern="^/locks$"))
async def show_locks(event):
    if not event.is_group:
        return await event.reply("⚠️ Use in groups only.")
    types = ["link", "sticker", "photo", "video", "gif", "document", "forward"]
    locked = []
    for t in types:
        if lock_table.contains(Query().key == f"{event.chat_id}:{t}"):
            locked.append(t)
    if locked:
        await event.reply(f"🔐 **Locked types in this group:** `{', '.join(locked)}`")
    else:
        await event.reply("✅ No locks are active in this group.")


@client.on(events.NewMessage(incoming=True))
async def filter_locked_content(event):
    if event.is_private or event.sender_id == (await client.get_me()).id:
        return

    try:
        participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
        if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return  # Admins bypass lock
    except:
        pass

    msg = event.message
    cid = event.chat_id

    if msg.web_preview and lock_table.contains(Query().key == f"{cid}:link"):
        return await msg.delete()

    if msg.sticker and lock_table.contains(Query().key == f"{cid}:sticker"):
        return await msg.delete()

    if msg.photo and lock_table.contains(Query().key == f"{cid}:photo"):
        return await msg.delete()

    if msg.video and lock_table.contains(Query().key == f"{cid}:video"):
        return await msg.delete()

    if msg.gif and lock_table.contains(Query().key == f"{cid}:gif"):
        return await msg.delete()

    if msg.document and not msg.gif and lock_table.contains(Query().key == f"{cid}:document"):
        return await msg.delete()

    if msg.fwd_from and lock_table.contains(Query().key == f"{cid}:forward"):
        return await msg.delete()

welcome_table = db.table("welcome_msgs")
welcome_status = db.table("welcome_status")

@client.on(events.NewMessage(pattern="^/setwelcome (.+)", func=lambda e: e.is_group))
async def set_welcome(event):
    msg = event.pattern_match.group(1)
    welcome_table.upsert({'chat_id': event.chat_id, 'msg': msg}, Query().chat_id == event.chat_id)
    welcome_status.upsert({'chat_id': event.chat_id, 'enabled': True}, Query().chat_id == event.chat_id)
    await event.reply("✅ Welcome message has been set and enabled.\nUse `/welcome off` to disable.")

@client.on(events.NewMessage(pattern="^/welcome ?(on|off)?$", func=lambda e: e.is_group))
async def toggle_welcome(event):
    mode = event.pattern_match.group(1)
    if not mode:
        entry = welcome_table.get(Query().chat_id == event.chat_id)
        if entry:
            await event.reply(f"📩 Current welcome message:\n\n`{entry['msg']}`", parse_mode="md")
        else:
            await event.reply("❌ No welcome message is set.")
    elif mode == "on":
        welcome_status.upsert({'chat_id': event.chat_id, 'enabled': True}, Query().chat_id == event.chat_id)
        await event.reply("✅ Welcome message has been enabled.")
    elif mode == "off":
        welcome_status.upsert({'chat_id': event.chat_id, 'enabled': False}, Query().chat_id == event.chat_id)
        await event.reply("🛑 Welcome message has been disabled.")

@client.on(events.NewMessage(pattern="^/delwelcome$", func=lambda e: e.is_group))
async def del_welcome(event):
    welcome_table.remove(Query().chat_id == event.chat_id)
    welcome_status.remove(Query().chat_id == event.chat_id)
    await event.reply("🗑️ Welcome message deleted and disabled.")

@client.on(events.ChatAction)
async def welcome_user(event):
    if event.user_joined or event.user_added:
        if not welcome_status.contains((Query().chat_id == event.chat_id) & (Query().enabled == True)):
            return

        entry = welcome_table.get(Query().chat_id == event.chat_id)
        if not entry: return

        user = event.user
        name = f"[{user.first_name}](tg://user?id={user.id})"
        msg = entry["msg"]
        group_title = (await event.get_chat()).title

        # Dynamic replacements
        formatted = msg.replace("{name}", name)\
                       .replace("{first}", user.first_name)\
                       .replace("{id}", str(user.id))\
                       .replace("{group}", group_title)

        try:
            await client.send_message(event.chat_id, formatted, parse_mode='md')
        except Exception:
            await client.send_message(event.chat_id, formatted)

@client.on(events.ChatAction)
async def welcome_user(event):
    if event.user_joined or event.user_added:
        entry = welcome_table.get(Query().chat_id == event.chat_id)
        if entry:
            welcome = entry["msg"]
            name = f"[{event.user.first_name}](tg://user?id={event.user.id})"
            await client.send_message(event.chat_id, welcome.replace("{name}", name), parse_mode='md')

from googletrans import Translator
translator = Translator()

@client.on(events.NewMessage(pattern="^/translate (\w+); (.+)"))
async def translate(event):
    lang, text = event.pattern_match.group(1), event.pattern_match.group(2)
    try:
        translated = translator.translate(text, dest=lang)
        await event.reply(f"🌍 Translated:\n**{translated.text}**")
    except Exception as e:
        await event.reply("❌ Could not translate.")

from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

ban_rights = ChatBannedRights(until_date=None, view_messages=True)
mute_rights = ChatBannedRights(until_date=None, send_messages=True)

@client.on(events.NewMessage(pattern="^/(ban|kick|mute)$"))
async def mod_tools(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Admins only.")
    if not event.is_reply:
        return await event.reply("Reply to user.")

    user_id = (await event.get_reply_message()).sender_id
    cmd = event.pattern_match.group(1)

    try:
        if cmd == "ban":
            await client(EditBannedRequest(event.chat_id, user_id, ban_rights))
            await event.reply("🚫 User banned.")
        elif cmd == "mute":
            await client(EditBannedRequest(event.chat_id, user_id, mute_rights))
            await event.reply("🔇 User muted.")
        elif cmd == "kick":
            await client.kick_participant(event.chat_id, user_id)
            await event.reply("👢 User kicked.")
    except Exception as e:
        await event.reply(f"❌ Error:\n{e}")

from telethon import events, Button

# --- /menu command ---
@client.on(events.NewMessage(pattern="^/menu$"))
async def show_menu(event):
    await event.delete()
    img = random.choice(menu_images)

    await client.send_file(
        event.chat_id,
        file=img,
        caption="**🧠 TagAllXBot Menu**\n\nClick buttons below to explore features.",
        buttons=[
            [Button.inline("👥 Mention Tools", b"mention_menu")],
            [Button.inline("🤖 AI & GPT", b"ai_menu")],
            [Button.inline("🔐 Lock & Spam", b"lock_menu")],
            [Button.inline("🛠 Utilities", b"util_menu")],
            [Button.inline("🎉 Fun & Games", b"fun_menu")],
            [Button.inline("📊 Stats & Admin", b"stats_menu")]
        ]
    )

# --- Callback Menu Handler ---
@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode("utf-8")
    img = random.choice(menu_images)
    await event.delete()

    if data == "mention_menu":
        await client.send_file(
            event.chat_id,
            file=img,
            caption=(
                "**👥 Mention Menu**\n\n"
                "`/mention <msg>` – Tag all users\n"
                "`/emoji <msg>` – Tag with emojis\n"
                "`/tagrecent <N> <msg>` – Tag last N users\n"
                "`/stop` – Stop ongoing tag process"
            ),
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "ai_menu":
        await client.send_file(
            event.chat_id,
            file=img,
            caption=(
                "**🤖 AI & GPT Tools**\n\n"
                "`/ask <query>` – Ask ChatGPT\n"
                "`/aichat on|off` – AI chat in group\n"
                "`/stylize <text>` – Fancy fonts\n"
                "`/vc <text>` – Text-to-voice\n"
                "`/say <text>` – Bot says text"
            ),
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "lock_menu":
        await client.send_file(
            event.chat_id,
            file=img,
            caption=(
                "**🔐 Lock System**\n\n"
                "`/lock <type>` – Lock content\n"
                "`/unlock <type>` – Unlock content\n"
                "`/lockall`, `/unlockall`\n"
                "`/banword <word>` – Ban word\n"
                "`/unbanword <word>` – Remove ban\n"
                "`/zombies` – Remove deleted users\n"
                "`/flood` – Anti-spam filter"
            ),
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "util_menu":
        await client.send_file(
            event.chat_id,
            file=img,
            caption=(
                "**🛠 Utilities**\n\n"
                "`/userinfo` – Info of replied user\n"
                "`/purge` – Delete from reply\n"
                "`/pinall <N>` – Pin last N messages\n"
                "`/id` – Show ID info\n"
                "`/admins` – List admins\n"
                "`/invite` – Group link\n"
                "`/setwelcome Welcome {name}` – Custom welcome"
            ),
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "fun_menu":
        await client.send_file(
            event.chat_id,
            file=img,
            caption=(
                "**🎉 Fun & Game Commands**\n\n"
                "`/truth`, `/dare` – Fun questions\n"
                "`/gift 100` – Fake coin gift\n"
                "`/poll What?;Yes;No` – Quick poll\n"
                "`/reverse`, `/funify` – Text play\n"
                "`/dice`, `/roll 100` – Randomizer"
            ),
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "stats_menu":
        await client.send_file(
            event.chat_id,
            file=img,
            caption=(
                "**📊 Bot Stats & Admin Tools**\n\n"
                "`/botstats` – Total stats\n"
                "`/broadcast` – Send to all users/groups\n"
                "`/promote`, `/fullpromote` (reply)\n"
                "`/ban`, `/kick`, `/mute`, `/unmute`\n"
                "`/report` – Report message to admins"
            ),
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "main_menu":
        # Reuse the main menu
        await show_menu(event)

vault_table = db.table("vault")

@client.on(events.NewMessage(pattern="^/save (.+)"))
async def save_message(event):
    msg = event.pattern_match.group(1)
    msg_id = str(random.randint(10000, 99999))
    vault_table.insert({"id": msg_id, "uid": event.sender_id, "msg": msg})
    await event.reply(f"💾 Saved! Use `/get {msg_id}` to retrieve.")

@client.on(events.NewMessage(pattern="^/get (\d+)$"))
async def get_saved(event):
    code = event.pattern_match.group(1)
    entry = vault_table.get((Query().id == code) & (Query().uid == event.sender_id))
    if entry:
        await event.reply(f"📥 Saved Message:\n{entry['msg']}")
    else:
        await event.reply("❌ Not found.")

@client.on(events.NewMessage(pattern="^/pinall (\d+)$"))
async def pin_all(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Admins only.")

    count = int(event.pattern_match.group(1))
    msgs = [m async for m in client.iter_messages(event.chat_id, limit=count)]
    for m in msgs:
        try:
            await m.pin()
        except:
            continue
    await event.reply(f"✅ Pinned last {count} messages.")


@client.on(events.NewMessage(pattern="^/invite$"))
async def get_invite(event):
    try:
        link = await client.export_chat_invite_link(event.chat_id)
        await event.reply(f"🔗 Invite Link:\n{link}")
    except Exception as e:
        await event.reply("❌ Unable to get invite link.\nMake sure I'm admin.")

@client.on(events.NewMessage(pattern="^/funify (.+)"))
async def funify(event):
    msg = event.pattern_match.group(1)
    fun_msg = ''.join(c + random.choice(emojis) for c in msg)
    await event.reply(fun_msg)

banned_words_table = db.table("banned_words")

@client.on(events.NewMessage(pattern="^/banword (.+)"))
async def ban_word(event):
    word = event.pattern_match.group(1).lower()
    banned_words_table.upsert({"chat_id": event.chat_id, "word": word}, 
                              (Query().chat_id == event.chat_id) & (Query().word == word))
    await event.reply(f"🚫 Word `{word}` banned.")

@client.on(events.NewMessage(pattern="^/unbanword (.+)"))
async def unban_word(event):
    word = event.pattern_match.group(1).lower()
    banned_words_table.remove((Query().chat_id == event.chat_id) & (Query().word == word))
    await event.reply(f"✅ Word `{word}` unbanned.")

@client.on(events.NewMessage)
async def delete_banned(event):
    if event.is_private or event.sender_id == (await client.get_me()).id:
        return
    all_words = banned_words_table.search(Query().chat_id == event.chat_id)
    text = event.raw_text.lower()
    for entry in all_words:
        if entry["word"] in text:
            await event.delete()
            break

@client.on(events.NewMessage(pattern="^/reverse (.+)"))
async def reverse_text(event):
    txt = event.pattern_match.group(1)
    await event.reply(txt[::-1])

@client.on(events.NewMessage(pattern="^/remindme (\d+);(.+)"))
async def remind(event):
    mins = int(event.pattern_match.group(1))
    msg = event.pattern_match.group(2)
    await event.reply(f"⏰ Reminder set! I’ll remind you in {mins} minutes.")
    await asyncio.sleep(mins * 60)
    await client.send_message(event.sender_id, f"🔔 Reminder: {msg}")

@client.on(events.NewMessage(pattern="^/poll (.+)"))
async def poll(event):
    parts = event.pattern_match.group(1).split(";")
    if len(parts) < 3:
        return await event.reply("⚠️ Format:\n/poll Question;Option1;Option2")
    
    question = parts[0]
    options = parts[1:]
    buttons = [[Button.inline(opt, data=f"poll:{opt}")] for opt in options]

    await event.reply(f"🗳 **{question}**", buttons=buttons, parse_mode='md')

poll_votes = {}

@client.on(events.CallbackQuery(data=lambda d: d.startswith("poll:")))
async def handle_vote(event):
    option = event.data.decode().split(":", 1)[1]
    uid = event.sender_id
    key = f"{event.chat_id}:{option}"
    poll_votes.setdefault(key, set()).add(uid)
    await event.answer(f"✅ Voted: {option}", alert=True)



@client.on(events.NewMessage(pattern="^/say (.+)"))
async def say_msg(event):
    text = event.pattern_match.group(1)
    await event.delete()
    await client.send_message(event.chat_id, text)

AUTO_MEDIA_DIR = "group_media"
os.makedirs(AUTO_MEDIA_DIR, exist_ok=True)

@client.on(events.NewMessage(func=lambda e: e.media))
async def auto_save_media(event):
    if not event.is_group:
        return
    file = await event.download_media(file=AUTO_MEDIA_DIR)
    print(f"📥 Saved media: {file}")

truths = ["What’s your darkest secret?", "Who was your first crush?", "Have you ever lied to your best friend?"]
dares = ["Text your ex 'I miss you'", "Send a voice note saying a tongue twister", "Ping the whole group with ❤️"]

@client.on(events.NewMessage(pattern="^/truth$"))
async def truth(event):
    await event.reply(f"🧠 Truth: {random.choice(truths)}")

@client.on(events.NewMessage(pattern="^/dare$"))
async def dare(event):
    await event.reply(f"🔥 Dare: {random.choice(dares)}")

@client.on(events.NewMessage(pattern="^/report$"))
async def report(event):
    if not event.is_reply:
        return await event.reply("⚠️ Reply to a message to report.")
    admins = []
    async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantAdmin):
        admins.append(f"[{user.first_name}](tg://user?id={user.id})")
    reported = event.reply_to_msg_id
    await event.reply(f"🚨 Reported message {reported} to: " + ", ".join(admins), parse_mode="md")


@client.on(events.NewMessage(pattern="^/zombies$"))
async def clean_zombies(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return
    count = 0
    async for user in client.iter_participants(event.chat_id):
        if user.deleted:
            try:
                await client.kick_participant(event.chat_id, user.id)
                count += 1
            except:
                pass
    await event.reply(f"🧟‍♂️ Removed {count} deleted accounts.")



@client.on(events.NewMessage(pattern="^/lockall$"))
async def lock_all(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return
    rights = ChatBannedRights(
        until_date=None, send_messages=True, send_media=True,
        send_stickers=True, send_gifs=True, send_games=True, send_inline=True
    )
    await client.edit_permissions(event.chat_id, rights=rights)
    await event.reply("🔒 All features locked.")

@client.on(events.NewMessage(pattern="^/unlockall$"))
async def unlock_all(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return
    rights = ChatBannedRights(until_date=None)
    await client.edit_permissions(event.chat_id, rights=rights)
    await event.reply("🔓 All features unlocked.")



from collections import defaultdict
from time import time

flood_tracker = defaultdict(list)
FLOOD_LIMIT = 5  # max messages
FLOOD_WINDOW = 10  # seconds

@client.on(events.NewMessage)
async def flood_control(event):
    if event.is_private or event.sender_id == (await client.get_me()).id:
        return

    user_id = event.sender_id
    now = time()
    flood_tracker[user_id] = [t for t in flood_tracker[user_id] if now - t < FLOOD_WINDOW]
    flood_tracker[user_id].append(now)

    if len(flood_tracker[user_id]) > FLOOD_LIMIT:
        await event.delete()
        await event.respond(f"⚠️ {event.sender.first_name} is spamming!", reply_to=event.id)

@client.on(events.NewMessage(pattern="^/admins$"))
async def list_admins(event):
    admins = []
    async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantAdmin):
        admins.append(f"• [{user.first_name}](tg://user?id={user.id})")
    await event.reply("👮‍♂️ Admins:\n" + "\n".join(admins), parse_mode="md")

fancy_fonts = ["𝖘𝖙𝖞𝖑𝖊", "ѕтуℓє", "𝓈𝓉𝓎𝓁𝑒", "ꜱᴛʏʟᴇ", "🆂🆃🆈🅻🅴"]

@client.on(events.NewMessage(pattern="^/stylize (.+)"))
async def stylize_text(event):
    text = event.pattern_match.group(1)
    styled = "\n".join([f"{font}" for font in fancy_fonts])
    await event.reply(f"✨ Stylized:\n{styled.replace('style', text)}")


import gtts

@client.on(events.NewMessage(pattern="^/vc (.+)"))
async def voice_convert(event):
    text = event.pattern_match.group(1)
    tts = gtts.gTTS(text)
    tts.save("vc.mp3")
    await client.send_file(event.chat_id, "vc.mp3", voice_note=True) 

@client.on(events.NewMessage(pattern=r"^/calc (.+)"))
async def calc(event):
    expr = event.pattern_match.group(1)
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        await event.reply(f"`{expr} = {result}`")
    except Exception:
        await event.reply("❌ Invalid expression.")

@client.on(events.NewMessage(pattern="^/countdown (\d+)$"))
async def countdown(event):
    seconds = int(event.pattern_match.group(1))
    msg = await event.reply(f"⏳ Countdown: {seconds}s")
    while seconds > 0:
        await asyncio.sleep(1)
        seconds -= 1
        await msg.edit(f"⏳ Countdown: {seconds}s")
    await msg.edit("✅ Time's up!")

import requests

@client.on(events.NewMessage(pattern="^/anime (.+)"))
async def anime_info(event):
    query = event.pattern_match.group(1)
    try:
        # Search anime using Jikan API
        url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"
        res = requests.get(url).json()

        if not res["data"]:
            return await event.reply("❌ No results found.")

        anime = res["data"][0]
        title = anime.get("title", "N/A")
        url = anime.get("url", "")
        image = anime["images"]["jpg"]["image_url"]
        type_ = anime.get("type", "Unknown")
        status = anime.get("status", "Unknown")
        score = anime.get("score", "N/A")
        episodes = anime.get("episodes", "N/A")
        synopsis = anime.get("synopsis", "No synopsis available.")[:500] + "..."

        caption = (
            f"🎌 **{title}**\n\n"
            f"📺 Type: `{type_}`\n"
            f"📶 Status: `{status}`\n"
            f"⭐ Score: `{score}`\n"
            f"🎞 Episodes: `{episodes}`\n\n"
            f"📝 Synopsis:\n`{synopsis}`\n\n"
            f"[🌐 MyAnimeList Link]({url})"
        )

        await client.send_file(event.chat_id, image, caption=caption, parse_mode="md", link_preview=False)

    except Exception as e:
        await event.reply(f"❌ Error:\n`{str(e)}`")

@client.on(events.NewMessage(pattern="^/manga (.+)"))
async def manga_info(event):
    query = event.pattern_match.group(1)
    try:
        url = f"https://api.jikan.moe/v4/manga?q={query}&limit=1"
        res = requests.get(url).json()
        if not res["data"]:
            return await event.reply("❌ No manga found.")

        manga = res["data"][0]
        title = manga["title"]
        image = manga["images"]["jpg"]["image_url"]
        synopsis = manga["synopsis"][:500] + "..."
        mal_url = manga["url"]
        score = manga["score"]
        status = manga["status"]

        caption = (
            f"📚 **{title}**\n"
            f"⭐ Score: `{score}`\n"
            f"📶 Status: `{status}`\n\n"
            f"📝 {synopsis}\n\n"
            f"[🔗 Read on MAL]({mal_url})"
        )

        await client.send_file(event.chat_id, image, caption=caption, parse_mode="md", link_preview=False)

    except Exception as e:
        await event.reply(f"❌ Error: `{e}`")

@client.on(events.NewMessage(pattern="^/animequote$"))
async def anime_quote(event):
    res = requests.get("https://animechan.xyz/api/random").json()
    await event.reply(
        f"🎌 *{res['character']}* from **{res['anime']}**:\n\n`{res['quote']}`",
        parse_mode="md"
    )

@client.on(events.NewMessage(pattern="^/quote$"))
async def quote(event):
    try:
        res = requests.get("https://api.quotable.io/random").json()
        await event.reply(f"💬 \"{res['content']}\"\n\n— *{res['author']}*")
    except:
        await event.reply("❌ Couldn’t fetch quote.")

@client.on(events.NewMessage(pattern="^/afk ?(.*)"))
async def set_afk(event):
    reason = event.pattern_match.group(1) or "No reason provided"
    user_id = event.sender_id
    if not afk_table.contains(Query().user_id == user_id):
        afk_table.insert({"user_id": user_id, "reason": reason})
    else:
        afk_table.update({"reason": reason}, Query().user_id == user_id)
    await event.reply(f"💤 You are now AFK!\nReason: `{reason}`")

@client.on(events.NewMessage())
async def remove_afk_and_check_mentions(event):
    user_id = event.sender_id

    # ⛔ Remove AFK if the sender was AFK
    if afk_table.contains(Query().user_id == user_id):
        afk_table.remove(Query().user_id == user_id)
        await event.reply("✅ Welcome back! AFK removed automatically.")

    # ✅ Check for AFK users being replied to
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg:
            afk_user = afk_table.get(Query().user_id == reply_msg.sender_id)
            if afk_user:
                reason = afk_user['reason']
                return await event.reply(f"💤 This user is AFK!\nReason: `{reason}`")

    # ✅ Check mentions in the message
    if event.message.mentioned:
        for entity in event.message.entities or []:
            if hasattr(entity, 'user_id'):
                afk_user = afk_table.get(Query().user_id == entity.user_id)
                if afk_user:
                    reason = afk_user['reason']
                    return await event.reply(f"💤 This user is AFK!\nReason: `{reason}`")

pic_table = db.table("pics")

@client.on(events.NewMessage(pattern="^/addpic (https?://\S+)$"))
async def add_pic(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ Not authorized.")
    url = event.pattern_match.group(1)
    pic_table.insert({"url": url})
    await event.reply("✅ Picture link added!")

@client.on(events.NewMessage(pattern="^/pic$"))
async def random_pic(event):
    pics = [p['url'] for p in pic_table.all()]
    if not pics:
        return await event.reply("⚠️ No pictures added yet.")
    await client.send_file(event.chat_id, random.choice(pics), caption="📸")

def is_gbanned(user_id):
    return gban_table.contains(Query().id == user_id)

def is_gmuted(user_id):
    return gmute_table.contains(Query().id == user_id)



@client.on(events.NewMessage(pattern="^/gban$"))
async def gban(event):
    if event.sender_id != bot_owner_id or not event.is_reply:
        return await event.reply("❌ Only the bot owner can use this command and reply to a user.")

    reply = await event.get_reply_message()
    user_id = reply.sender_id

    if is_gbanned(user_id):
        return await event.reply("🚫 User is already globally banned.")
    
    gban_table.insert({"id": user_id})

    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            try:
                await client.edit_permissions(dialog.id, user_id, view_messages=False)
            except:
                continue  # Ignore if not admin in the chat

    await event.reply(f"✅ Globally banned user [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")
    await client.send_message(log_chat_id, f"🚫 GBanned: [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")


@client.on(events.NewMessage(pattern="^/gunban$"))
async def gunban(event):
    if event.sender_id != bot_owner_id or not event.is_reply:
        return await event.reply("❌ Only the bot owner can use this command and reply to a user.")

    reply = await event.get_reply_message()
    user_id = reply.sender_id

    if not is_gbanned(user_id):
        return await event.reply("✅ User is not banned.")

    gban_table.remove(Query().id == user_id)

    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            try:
                await client.edit_permissions(dialog.id, user_id, view_messages=True)
            except:
                continue

    await event.reply(f"✅ Unbanned [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")
    await client.send_message(log_chat_id, f"✅ GUnbanned: [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")


@client.on(events.NewMessage(pattern="^/gmute$"))
async def gmute(event):
    if event.sender_id != bot_owner_id or not event.is_reply:
        return await event.reply("❌ Only the bot owner can use this command and reply to a user.")

    reply = await event.get_reply_message()
    user_id = reply.sender_id

    if is_gmuted(user_id):
        return await event.reply("🔇 User is already globally muted.")

    gmute_table.insert({"id": user_id})
    await event.reply(f"🔇 Globally muted [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")
    await client.send_message(log_chat_id, f"🔇 GMute: [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")


@client.on(events.NewMessage(pattern="^/gunmute$"))
async def gunmute(event):
    if event.sender_id != bot_owner_id or not event.is_reply:
        return await event.reply("❌ Only the bot owner can use this command and reply to a user.")

    reply = await event.get_reply_message()
    user_id = reply.sender_id

    if not is_gmuted(user_id):
        return await event.reply("✅ User is not muted.")

    gmute_table.remove(Query().id == user_id)
    await event.reply(f"✅ Unmuted [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")
    await client.send_message(log_chat_id, f"✅ GUnmute: [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")

@client.on(events.NewMessage())
async def auto_delete_muted(event):
    if event.is_private or not event.sender_id:
        return
    if is_gmuted(event.sender_id):
        try:
            await event.delete()
        except:
            pass

@client.on(events.NewMessage(pattern="^/gkick$"))
async def gkick(event):
    if event.sender_id != bot_owner_id or not event.is_reply:
        return await event.reply("❌ Only the bot owner can use this command and reply to a user.")

    reply = await event.get_reply_message()
    user_id = reply.sender_id

    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            try:
                await client.kick_participant(dialog.id, user_id)
                await client.edit_permissions(dialog.id, user_id, view_messages=True)  # Allow rejoin
            except:
                continue

    await event.reply(f"✅ Globally kicked [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")
    await client.send_message(log_chat_id, f"👢 GKicked: [{reply.sender.first_name}](tg://user?id={user_id})", parse_mode="md")

@client.on(events.NewMessage(pattern="^/gpin$"))
async def gpin(event):
    if event.sender_id != bot_owner_id or not event.is_reply:
        return await event.reply("❌ Reply to a message to pin it globally.")

    reply = await event.get_reply_message()

    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                sent = await client.send_message(dialog.id, reply.message)
                await client.pin_message(dialog.id, sent.id, notify=False)
            except:
                continue

    await event.reply("📌 Message pinned in all groups.")

@client.on(events.NewMessage(pattern="^/banall$"))
async def ban_all_groups(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ Only the bot owner can use this command.")

    if not event.is_reply:
        return await event.reply("⚠️ You must reply to a user to ban them from all groups.")

    reply = await event.get_reply_message()
    user_id = reply.sender_id
    user_name = reply.sender.first_name

    success, failed = 0, 0

    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            try:
                await client.edit_permissions(dialog.id, user_id, view_messages=False)
                success += 1
            except:
                failed += 1

    await event.reply(
        f"🚫 **User [{user_name}](tg://user?id={user_id}) banned from all groups.**\n"
        f"✅ Success: `{success}` | ❌ Failed: `{failed}`", parse_mode="md"
    )

    # Optional: log the action
    await client.send_message(
        log_chat_id,  # Your log group ID
        f"🚫 **BANALL Issued**\n"
        f"👤 User: [{user_name}](tg://user?id={user_id}) (`{user_id}`)\n"
        f"🔨 Action: Banned from all groups\n"
        f"✅ Success: `{success}` | ❌ Failed: `{failed}`",
        parse_mode="md"
    )


print(">> BOT STARTED <<")
client.run_until_disconnected()
# === Start Bot =
