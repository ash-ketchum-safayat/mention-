import random
import os, logging, asyncio
import telethon
from telethon import Button
from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

emojis = ["😀", "😍", "🤣", "👍", "🌟", "🎉", "👏", "🤔", "😎", "🥰", "🥳", "🙌", "🌺", "🎈", "🌞", "🌍", "🎶", "🍕", "🍦", "🚀"]
api_id = int(8447214)
api_hash = "9ec5782ddd935f7e2763e5e49a590c0d"
bot_token = "8183522431:AAHDQy3xZj5kE37ew6qIQw0-Cy9h0AYw_7M"
client = TelegramClient('client61727', api_id, api_hash).start(bot_token=bot_token)
spam_chats = []

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
  await client.send_message(
    event.chat_id,
    "__**I'm @SerenaProBot**, I can mention almost all members in group or channel 👻\nClick **/help** for more information__\n\n**Join @AshxBots For Latest Updates**",
    link_preview=False,
    buttons=(
      [
        Button.url('📦 Owner', 'https://t.me/Ashketchum_001')
      ]
    )
  )

@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
  helptext = "**Help Menu of @SerenaProBot**\n\nCommand: /mention | /emoji\n__You can use this command with text what you want to mention others.__\n*Example:*\n*1.* `/mention Good Morning!`\n*2.* `/emoji Hello World!`\n__You can you this command as a reply to any message. Bot will tag users to that replied messsage__.\n\n**Join @AshxBots For Latest Updates**"
  await event.reply(
    helptext,
    link_preview=False,
    buttons=(
      [
        Button.url('📦 Owner', 'https://t.me/Ashketchum_001')
      ]
    )
  )
  
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
import asyncio

# Keep track of active tag sessions
spam_chats = []

@client.on(events.NewMessage(pattern="^/(mention|tagall|utag|tagx|mentionall|chutiyo|bachhelog)(?:\s+(.*))?"))
async def mentionall(event):
    chat_id = event.chat_id

    if event.is_private:
        return await event.reply("🚫 This command can only be used in groups!")

    # Check admin status
    is_admin = False
    try:
        participant = await client(GetParticipantRequest(chat_id, event.sender_id))
        if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            is_admin = True
    except UserNotParticipantError:
        pass

    if not is_admin:
        return await event.reply("❌ Only admins can mention all members!")

    if chat_id in spam_chats:
        return await event.reply("⚠️ Tagging is already in progress...")

    # Determine mode
    mode = None
    message = None
    if event.pattern_match.group(2):  # Command with text
        mode = "text_on_cmd"
        message = event.pattern_match.group(2)
    elif event.is_reply:  # Reply mode
        mode = "text_on_reply"
        message = await event.get_reply_message()
        if not message:
            return await event.reply("⚠️ Cannot mention users for very old messages!")
    else:
        return await event.reply("❓ Provide some text or reply to a message to tag everyone.")

    spam_chats.append(chat_id)
    user_count = 0
    tag_text = ''

    async for user in client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break

        user_count += 1
        tag_text += f"<a href='tg://user?id={user.id}'> {user.first_name}</a> "

        if user_count == 7:
            try:
                if mode == "text_on_cmd":
                    await client.send_message(chat_id, f"{tag_text}\n\n<b>{message}</b>", parse_mode='HTML')
                elif mode == "text_on_reply":
                    await message.reply(tag_text, parse_mode='HTML')
            except Exception as e:
                print(f"Error sending message: {e}")
            await asyncio.sleep(1.5)
            user_count = 0
            tag_text = ''

    # Remove chat from spam_chats and confirm completion
    try:
        spam_chats.remove(chat_id)
        await client.send_message(chat_id, "✅ Finished mentioning everyone!\nJoin @AshxBots", parse_mode='HTML')
    except Exception as e:
        print(f"Error in cleanup: {e}")
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
    usrtxt += f"<a href ='tg://user?id={usr.id}'><b>  {random.choice(emojis)}</b></a>"
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

@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
  if not event.chat_id in spam_chats:
    return await event.respond('__There is no proccess on going...__')
  else:
    try:
      spam_chats.remove(event.chat_id)
    except:
      pass
    return await event.respond('__Stopped.__')

print(">> BOT STARTED <<")
client.run_until_disconnected()
