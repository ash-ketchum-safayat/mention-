import random
import os, logging, asyncio
import telethon
from telethon import Button
from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights, PeerUser


logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

emojis = ["😀", "😍", "🤣", "👍", "🌟", "🎉", "👏", "🤔", "😎", "🥰", "🥳", "🙌", "🌺", "🎈", "🌞", "🌍", "🎶", "🍕", "🍦", "🚀"]
api_id = int(4226067)
api_hash = "2d01711f0566de2309b633f49542e7e2"
bot_token = "7990236138:AAFt1Y00cXK6gxyve84fp2J89b5hbjU5uJ0"
bot_owner_id = 7946913230
client = TelegramClient('client_mention', api_id, api_hash).start(bot_token=bot_token)
spam_chats = []

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
  await client.send_message(
    event.chat_id,
    "__**I'm @TagallxBot Bot**, I can mention almost all members in group or channel 👻\nClick **/help** for more information__\n\n**Join @Ash_Bots For Latest Updates**",
    link_preview=False,
    buttons=(
      [
        Button.url('📦 Owner', 'https://t.me/AshKetchum_001')
      ]
    )
  )

@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
  helptext = "**Help Menu of @TagAllxBot**\n\nCommand: /mention | /emoji\n__You can use this command with text what you want to mention others.__\n*Example:*\n*1.* `/mention Good Morning!`\n*2.* `/emoji Hello World!`\n*3.* `/promote Admin`\n*4.* `/fullpromote Boss`__You can you this command as a reply to any message. Bot will tag users to that replied messsage__.\n\n**Join @Ash_Bots For Latest Updates**"
  await event.reply(
    helptext,
    link_preview=False,
    buttons=(
      [
        Button.url('📦 Owner', 'https://t.me/AshKetchum_001')
      ]
    )
  )
  
@client.on(events.NewMessage(pattern="^/(tagall|mention|mentionall|utag|loud) ?(.*)"))
async def mention_all(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond("__This command can only be used in groups and channels!__")

    # Check if sender is an admin
    is_admin = False
    try:
        partici_ = await client(GetParticipantRequest(chat_id, event.sender_id))
        if isinstance(partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            is_admin = True
    except UserNotParticipantError:
        pass

    if not is_admin:
        return await event.respond("__Only admins can mention all!__")

    if chat_id in spam_chats:
        return await event.respond("**There is already a process ongoing...**")

    msg = event.pattern_match.group(2) or "Hello everyone!"
    spam_chats.append(chat_id)

    usrnum = 0
    usrtxt = ''
    async for usr in client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        usrnum += 1
        usrtxt += f"<a href='tg://user?id={usr.id}'><b> {usr.first_name}</b></a>, "
        if usrnum == 7:
            await client.send_message(chat_id, f"{usrtxt}\n\n<b>{msg}</b>", parse_mode='HTML')
            await asyncio.sleep(1.5)
            usrnum = 0
            usrtxt = ''

    try:
        spam_chats.remove(chat_id)
        await client.send_message(chat_id, "<b>Mentioning All Users Done ✅</b>\nJoin Bot Updates : @Ash_Bots", parse_mode='HTML')
    except:
        pass
@client.on(events.NewMessage(pattern="^/emoji ?(.*)"))
async def mentionall(event):
  chat_id = event.chat_id
  if event.is_private:
    return await event.respond("__This command can be use in groups and channels!__")
  is_admin = False
  try:
    partici_ = await client(GetParticipantRequest(
      event.chat_id,
      event.sender_id
    ))
  except UserNotParticipantError:
    is_admin = False
  else:
    if (
      isinstance(
        partici_.participant,
        (
          ChannelParticipantAdmin,
          ChannelParticipantCreator
        )
      )
    ):
      is_admin = True
  if not is_admin:
    return await event.respond("__Only admins can mention all!__")

  if event.chat_id in spam_chats:
    return await event.respond('**There is already proccess on going...**')

  if event.is_reply:
    mode = "text_on_reply"
    msg = await event.get_reply_message()
    if msg == None:
        return await event.respond("__I can't mention members for older messages! (messages which are sent before I'm added to group)__")
  else:
    return await event.respond("__Reply to a message to mention others with emoji!__")

  spam_chats.append(chat_id)
  usrnum = 0
  usrtxt = ''
  async for usr in client.iter_participants(chat_id):
    if not chat_id in spam_chats:
      break
    usrnum += 1
    usrtxt += f"<a href ='tg://user?id={usr.id}'><b>  {random.choice(emojis)}</b></a>, "
    if usrnum == 30:
      if mode == "text_on_cmd":
        txt = f"{usrtxt}\n\n<b>{msg}</b>"
        await client.send_message(chat_id, txt,parse_mode='HTML')
      elif mode == "text_on_reply":
        await msg.reply(usrtxt,parse_mode='HTML')
      await asyncio.sleep(1.5)
      usrnum = 0
      usrtxt = ''
  try:
    spam_chats.remove(chat_id)
    await client.send_message(chat_id,'<b>Mentioning All Users Done ✅</b>',parse_mode='HTML')
  except:
    pass


@client.on(events.NewMessage(pattern="^/(stop|stopall|cancel|unmention|untagall)$"))
async def cancel_spam(event):
    chat_id = event.chat_id
    if chat_id not in spam_chats:
        return await event.respond("__There is no process ongoing...__")
    spam_chats.remove(chat_id)
    await event.respond("__Stopped mentioning users.__")

@client.on(events.NewMessage(pattern="^/botstats$"))
async def bot_stats(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ You are not authorized to use this command.")

    total_users = len(users_db)
    total_groups = len(groups_db)
    total_channels = len(channels_db)

    stats_message = (
        f"📊 **Bot Statistics** 📊\n\n"
        f"👤 **Total Users:** {total_users}\n"
        f"👥 **Total Groups:** {total_groups}\n"
        f"📢 **Total Channels:** {total_channels}"
    )
    await event.reply(stats_message)

@client.on(events.ChatAction)
async def track_chats(event):
    chat = await event.get_chat()
    if event.user_added or event.user_joined:
        if chat.broadcast:
            channels_db.add(chat.id)
        elif chat.megagroup:
            groups_db.add(chat.id)
        else:
            users_db.add(chat.id)

@client.on(events.NewMessage(pattern="^/broadcast$"))
async def broadcast(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ You are not authorized to use this command.")
    
    if not event.is_reply:
        return await event.reply("Reply to a message to broadcast it.")
    
    message = await event.get_reply_message()
    
    sent_users, sent_groups, sent_channels = 0, 0, 0
    failed_users, failed_groups, failed_channels = 0, 0, 0

    for user_id in users_db:
        try:
            await client.send_message(user_id, message)
            sent_users += 1
        except:
            failed_users += 1

    for group_id in groups_db:
        try:
            await client.send_message(group_id, message)
            sent_groups += 1
        except:
            failed_groups += 1

    for channel_id in channels_db:
        try:
            await client.send_message(channel_id, message)
            sent_channels += 1
        except:
            failed_channels += 1

    report_message = (
        "✅ **Broadcast Completed** ✅\n\n"
        f"📤 **Successfully Sent:**\n"
        f"👤 Users: {sent_users}\n"
        f"👥 Groups: {sent_groups}\n"
        f"📢 Channels: {sent_channels}\n\n"
        f"❌ **Failed To Send:**\n"
        f"👤 Users: {failed_users}\n"
        f"👥 Groups: {failed_groups}\n"
        f"📢 Channels: {failed_channels}"
    )
    await event.reply(report_message)


@client.on(events.NewMessage(pattern="^/promote$"))
async def promote(event):
    if not event.is_group:
        return await event.reply("❌ This command only works in groups.")
    
    if event.sender_id != bot_owner_id:
        # Check if sender is an admin
        try:
            participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
            if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                return await event.reply("❌ Only group admins can promote members!")
        except:
            return await event.reply("❌ Failed to check admin status.")

    # Check if bot has admin rights
    bot_participant = await client(GetParticipantRequest(event.chat_id, 'me'))
    if not isinstance(bot_participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
        return await event.reply("❌ I need to be an admin to promote users!")

    # Check if replied to a user
    if not event.is_reply:
        return await event.reply("⚠️ Reply to a user to promote them.")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id

    # Assign limited admin rights
    rights = ChatAdminRights(
        change_info=False,
        delete_messages=True,
        ban_users=False,
        invite_users=True,
        pin_messages=True,
        add_admins=False,
        anonymous=False,
        manage_call=True
    )

    try:
        await client(EditAdminRequest(event.chat_id, PeerUser(user_id), rights, "Group Admin"))
        await event.reply(f"✅ Successfully promoted [{reply_msg.sender.first_name}](tg://user?id={user_id}) with limited permissions.", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Failed to promote user.\n**Error:** `{str(e)}`")

@client.on(events.NewMessage(pattern="^/fullpromote$"))
async def full_promote(event):
    if not event.is_group:
        return await event.reply("❌ This command only works in groups.")
    
    if event.sender_id != bot_owner_id:
        # Check if sender is an admin
        try:
            participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
            if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                return await event.reply("❌ Only group admins can promote members!")
        except:
            return await event.reply("❌ Failed to check admin status.")

    # Check if bot has admin rights
    bot_participant = await client(GetParticipantRequest(event.chat_id, 'me'))
    if not isinstance(bot_participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
        return await event.reply("❌ I need to be an admin to promote users!")

    # Check if replied to a user
    if not event.is_reply:
        return await event.reply("⚠️ Reply to a user to fully promote them.")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id

    # Assign full admin rights
    full_rights = ChatAdminRights(
        change_info=True,
        delete_messages=True,
        ban_users=True,
        invite_users=True,
        pin_messages=True,
        add_admins=True,
        anonymous=True,
        manage_call=True
    )

    try:
        await client(EditAdminRequest(event.chat_id, PeerUser(user_id), full_rights, "Full Admin"))
        await event.reply(f"✅ Fully promoted [{reply_msg.sender.first_name}](tg://user?id={user_id}) with all permissions.", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Failed to fully promote user.\n**Error:** `{str(e)}`")



print(">> BOT STARTED <<")
client.run_until_disconnected()
