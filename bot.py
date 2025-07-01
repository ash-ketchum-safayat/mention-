import random
import os, logging, asyncio, time, datetime
from telethon import Button
from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest, EditAdminRequest
from telethon.errors import UserNotParticipantError
from telethon.tl.types import ChatAdminRights, PeerUser
from tinydb import TinyDB, Query
import openai
openai.api_key = "your_openai_api_key"

# === Logging ===
logging.basicConfig(level=logging.INFO, format='%(name)s - [%(levelname)s] - %(message)s')
LOGGER = logging.getLogger(__name__)

# === Config ===
api_id = 4226067
api_hash = "2d01711f0566de2309b633f49542e7e2"
bot_token = "8183522431:AAHDQy3xZj5kE37ew6qIQw0-Cy9h0AYw_7M"
bot_owner_id = 6279412066

# === Init ===
client = TelegramClient('client_mention', api_id, api_hash).start(bot_token=bot_token)
spam_chats = []
emojis = ["😀", "😍", "🤣", "👍", "🌟", "🎉", "👏", "🤔", "😎", "🥰", "🥳", "🙌", "🌺", "🎈", "🌞", "🌍", "🎶", "🍕", "🍦", "🚀"]
bot_start_time = time.time()

# === TinyDB ===
db = TinyDB("bot_data.json")
users_table = db.table("users")
groups_table = db.table("groups")
channels_table = db.table("channels")

# === Commands ===

warnings_table = db.table("warnings")

import qrcode
from io import BytesIO

blocked_keywords = [
    "porn", "scam", "grabify", "joinchat", "bit.ly", "adf.ly", "tinyurl", "adult", "virus", "trojan", "darkweb"
]

@client.on(events.NewMessage(pattern="^/qrcode (.+)"))
async def make_qrcode(event):
    text = event.pattern_match.group(1)

    if any(x in text.lower() for x in blocked_keywords):
        return await event.reply("🚫 Dangerous link detected. QR code blocked.")

    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    buffer.name = "qrcode.png"
    img.save(buffer, format="PNG")
    buffer.seek(0)

    await client.send_file(event.chat_id, buffer, caption="✅ QR Code Generated!")

from PIL import Image
from pyzbar.pyzbar import decode

@client.on(events.NewMessage(pattern="^/scanqr$"))
async def scan_qr_command(event):
    if not event.is_reply:
        return await event.reply("📸 Reply to a QR code image with `/scanqr`.")

    reply = await event.get_reply_message()
    if not reply.photo and not reply.document:
        return await event.reply("🖼 This isn't an image.")

    path = await reply.download_media()
    try:
        img = Image.open(path)
        decoded = decode(img)
        if not decoded:
            return await event.reply("❌ No QR code found in the image.")
        result = decoded[0].data.decode("utf-8")
        await event.reply(f"🔍 Decoded QR Content:\n`{result}`", parse_mode="md")
    except Exception as e:
        await event.reply(f"❌ Error scanning:\n`{e}`")

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

@client.on(events.MessageDeleted())
async def track_deletion(event):
    for msg in event.deleted_ids:
        last_deleted[event.chat_id] = msg

@client.on(events.NewMessage(pattern="^/snipe$"))
async def snipe(event):
    if event.chat_id in last_deleted:
        msg = await client.get_messages(event.chat_id, ids=last_deleted[event.chat_id])
        await event.reply(f"💀 Sniped:\n{msg.text}")
    else:
        await event.reply("❌ Nothing to snipe.")



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
    user_id = event.sender_id
    chat = await event.get_chat()

    # ⏱ Uptime Calculation
    uptime_seconds = int(time.time() - bot_start_time)
    uptime = str(datetime.timedelta(seconds=uptime_seconds))

    # 👤 Private Chat (DM)
    if event.is_private:
        if not users_table.contains(Query().id == user_id):
            users_table.insert({"id": user_id})

        welcome_text = (
            f"👋 **Welcome, [{event.sender.first_name}](tg://user?id={user_id})!**\n\n"
            "I'm **TagAllXBot**, your all-in-one group assistant 🤖\n\n"
            "**🔧 Main Features:**\n"
            "• 👥 Mention Everyone\n"
            "• 🤖 ChatGPT & AI Tools\n"
            "• 🔐 Lock + Anti-Spam System\n"
            "• 🛠 Admin Utilities\n"
            "• 🎉 Games, Polls & More!\n\n"
            "✨ Tap a button below to get started!"
        )

        await client.send_message(
            event.chat_id,
            welcome_text,
            file="https://telegra.ph/file/e9c688ff02597d6f8b9cb.jpg",  # Optional banner
            buttons=[
                [Button.inline("✨ Open Menu", b"main_menu")],
                [Button.url("➕ Add Me to Group", f"https://t.me/{(await client.get_me()).username}?startgroup=true")],
                [
                    Button.url("📢 Updates Channel", "https://t.me/AshxBots"),
                    Button.url("👤 Contact Owner", "https://t.me/AshKetchum_001")
                ]
            ],
            parse_mode="md",
            link_preview=False
        )

    # 👥 In a group or channel
    else:
        await event.reply(
            f"✅ **Bot is Online!**\n"
            f"⏱ **Uptime:** `{uptime}`\n"
            f"📦 **Name:** `{(await client.get_me()).first_name}`",
            parse_mode="md"
        )
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

@client.on(events.NewMessage(pattern="^/(dice|roll)$"))
async def roll_dice(event):
    result = random.randint(1, 6)
    await event.reply(f"🎲 You rolled a `{result}`!")

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

@client.on(events.NewMessage(pattern="^/botstats$"))
async def bot_stats(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ You are not authorized to use this command.")
    uptime = str(datetime.timedelta(seconds=int(time.time() - bot_start_time)))
    await event.reply(
        f"**🤖 Bot Statistics**\n\n"
        f"🟢 **Online**\n"
        f"⏱ **Uptime:** `{uptime}`\n"
        f"👤 **Users:** `{len(users_table)}`\n"
        f"👥 **Groups:** `{len(groups_table)}`\n"
        f"📢 **Channels:** `{len(channels_table)}`"
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

@client.on(events.NewMessage(pattern="^/menu$"))
async def show_menu(event):
    await event.respond(
        "**🧠 TagAllXBot Menu**\n\nClick buttons below to explore features.",
        buttons=[
            [Button.inline("👥 Mention Tools", b"mention_menu")],
            [Button.inline("🤖 AI & GPT", b"ai_menu")],
            [Button.inline("🔐 Lock & Spam", b"lock_menu")],
            [Button.inline("🛠 Utilities", b"util_menu")],
            [Button.inline("🎉 Fun & Games", b"fun_menu")],
            [Button.inline("📊 Stats & Admin", b"stats_menu")]
        ]
    )

@@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode("utf-8")

    if data == "mention_menu":
        await event.edit(
            "**👥 Mention Menu**\n\n"
            "`/mention <msg>` – Tag all users\n"
            "`/emoji <msg>` – Tag with emojis\n"
            "`/tagrecent <N> <msg>` – Tag last N users\n"
            "`/stop` – Stop ongoing tag process",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "ai_menu":
        await event.edit(
            "**🤖 AI & GPT Tools**\n\n"
            "`/ask <query>` – Ask ChatGPT\n"
            "`/aichat on|off` – AI chat in group\n"
            "`/stylize <text>` – Fancy fonts\n"
            "`/vc <text>` – Text-to-voice\n"
            "`/say <text>` – Bot says text",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "lock_menu":
        await event.edit(
            "**🔐 Lock System**\n\n"
            "`/lock <type>` – Lock content\n"
            "`/unlock <type>` – Unlock content\n"
            "`/lockall`, `/unlockall`\n"
            "`/banword <word>` – Ban word\n"
            "`/unbanword <word>` – Remove ban\n"
            "`/zombies` – Remove deleted users\n"
            "`/flood` – Anti-spam filter",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "util_menu":
        await event.edit(
            "**🛠 Utilities**\n\n"
            "`/userinfo` – Info of replied user\n"
            "`/purge` – Delete from reply\n"
            "`/pinall <N>` – Pin last N messages\n"
            "`/id` – Show ID info\n"
            "`/admins` – List admins\n"
            "`/invite` – Group link\n"
            "`/setwelcome Welcome {name}` – Custom welcome",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "fun_menu":
        await event.edit(
            "**🎉 Fun & Game Commands**\n\n"
            "`/truth`, `/dare` – Fun questions\n"
            "`/gift 100` – Fake coin gift\n"
            "`/poll What?;Yes;No` – Quick poll\n"
            "`/reverse`, `/funify` – Text play\n"
            "`/dice`, `/roll 100` – Randomizer",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "stats_menu":
        await event.edit(
            "**📊 Bot Stats & Admin Tools**\n\n"
            "`/botstats` – Total stats\n"
            "`/broadcast` – Send to all users/groups\n"
            "`/promote`, `/fullpromote` (reply)\n"
            "`/ban`, `/kick`, `/mute`, `/unmute`\n"
            "`/report` – Report message to admins",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "main_menu":
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

ai_enabled_table = db.table("ai_groups")

@client.on(events.NewMessage(pattern="^/aichat (on|off)$"))
async def toggle_ai(event):
    if not event.is_group:
        return
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Admins only.")

    mode = event.pattern_match.group(1)
    if mode == "on":
        ai_enabled_table.upsert({"id": event.chat_id}, Query().id == event.chat_id)
        await event.reply("✅ AI Chat enabled.")
    else:
        ai_enabled_table.remove(Query().id == event.chat_id)
        await event.reply("🛑 AI Chat disabled.")

@

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

import requests

UNSPLASH_ACCESS_KEY = "YOUR_ACCESS_KEY"

@client.on(events.NewMessage(pattern="^/pic (.+)"))
async def get_image(event):
    query = event.pattern_match.group(1)
    r = requests.get(f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}")
    if r.status_code == 200:
        img_url = r.json()["urls"]["regular"]
        await client.send_file(event.chat_id, img_url, caption=f"📸 {query.title()} from Unsplash")
    else:
        await event.reply("❌ Could not fetch image.")

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




# === Start Bot ===
print(">> BOT STARTED <<")
client.run_until_disconnected()