from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ChatPermissions, InputMediaPhoto
)
import random
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from pymongo import MongoClient
import logging
from telegram.ext import ApplicationBuilder
from telegram.ext import ChatMemberHandler
import asyncio
from telethon import TelegramClient, events
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

BOT_TOKEN = "8183522431:AAFqb8H5ZT5e-czF-bpCl12BEjVG9_cDW1g"
OWNER_ID = 6279412066
MONGO_URI = "mongodb+srv://wwwbangladeshiserverey:QLM2MQdEDFC4fsr2@miko.makogkx.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Miko"
LOG_GROUP_ID = -1002869505504  # Replace with your actual log group ID
api_id = int(8447214)
api_hash = "9ec5782ddd935f7e2763e5e49a590c0d"
client = TelegramClient('client61727', api_id, api_hash).start(bot_token=BOT_TOKEN)

client_db = MongoClient(MONGO_URI)
db = client_db["GroupBot"]
users_col = db["users"]
admins_col = db["admins"]
botdata = db["serena-bot"]
ratings_col = db["bot_ratings"]
ADMINS = [OWNER_ID]  # default
# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Test connection
menu_images = [
    "https://files.catbox.moe/eviz7e.jpg",
    "https://files.catbox.moe/tnjrqb.jpg",
    "https://files.catbox.moe/xycejx.jpg",
    "https://files.catbox.moe/jcjqhs.jpg",
    "https://files.catbox.moe/cidhop.jpg",
    "https://files.catbox.moe/qy1ti2.jpg",
    "https://files.catbox.moe/yriq4n.jpg"
]

spam_chats = []
group_members = {}  # {chat_id: set(user_ids)}

async def send_in_thread(update: Update, context: ContextTypes.DEFAULT_TYPE, text, **kwargs):
    """Forum-safe message sender"""
    kwargs.update({
        "chat_id": update.effective_chat.id,
        "text": text
    })
    if update.message and update.message.message_thread_id:
        kwargs["message_thread_id"] = update.message.message_thread_id

    await context.bot.send_message(**kwargs)

words = [
    "python", "chat", "bot", "quiz", 
    "code", "app", "web", "game", 
    "data", "user", "team", "test", 
    "help", "file", "edit", "save", 
    "send", "receive", "search", "link", 
    "page", "post", "like", "share", 
    "click", "play", "run", "stop", 
    "start", "stop", "install", "update",
    "error", "bug", "fix", "work",
    "learn", "build", "create", 
    "design", "style", "look",
    "fast", "easy", "simple",
    "show", "tell", "read", 
    "write", "draw",
]

truths = [
    "What’s your biggest fear?",
    "Have you ever lied to your best friend?",
    "What’s your weirdest habit?",
    "Have you ever cheated on a test?",
    "What’s the most embarrassing thing you’ve ever done?",
    "Who was your first crush?",
    "Have you ever stalked someone on social media?",
    "What’s one secret you’ve never told anyone?",
    "Do you sing in the shower?",
    "What’s your guilty pleasure song?",
    "Have you ever stolen anything?",
    "Have you ever had a crush on a teacher?",
    "What’s the worst date you’ve ever been on?",
    "What’s the most childish thing you still do?",
    "Have you ever told a big lie and gotten away with it?",
    "If you could swap lives with someone for a day, who would it be?",
    "Have you ever peed in a pool?",
    "What’s the last thing you searched for on Google?",
    "If you had to delete one app forever, which would it be?",
    "Who’s the last person you texted?",
    "What’s your biggest insecurity?",
    "Do you talk to yourself in the mirror?",
    "What’s something you wish you were better at?",
    "Have you ever blamed someone else for something you did?",
    "What’s your biggest regret?",
    "Have you ever had a crush on a friend's partner?",
    "What’s the dumbest thing you believed as a kid?",
    "If you were invisible, what’s the first thing you’d do?",
    "What’s your most useless talent?",
    "What’s the last lie you told?",
    "Who do you secretly envy and why?",
    "Have you ever broken something and not told anyone?",
    "Do you believe in ghosts?",
    "What’s something you’ve never told your parents?",
    "What’s your biggest relationship ick?",
    "Have you ever cried at a movie?",
    "What’s your most awkward moment?",
    "If you had to date a cartoon character, who would it be?",
    "What’s your worst habit?",
    "What’s your most irrational fear?",
    "Have you ever pretended to be sick to get out of something?",
    "If you had to delete all but three apps, which ones would you keep?",
    "What’s the worst gift you’ve ever received?",
    "What’s something illegal you’ve done?",
    "What’s the weirdest thing you’ve eaten?",
    "Have you ever farted and blamed someone else?",
    "What’s your most cringe memory?",
    "What would you do if you switched gender for a day?",
    "Have you ever ghosted someone?",
    "What’s something you wish people knew about you?",
    "Do you keep a secret diary or notes?",
    "What’s your biggest dealbreaker in a relationship?",
    "What do you pretend to know more about than you really do?",
    "Have you ever lied during a truth or dare game?",
    "Who do you think is the best-looking person in this group?",
    "What would you do if you won the lottery?",
    "What’s the most romantic thing someone has done for you?",
    "Do you have any weird phobias?",
    "What’s your wildest dream?",
    "What’s the worst trouble you’ve ever gotten into?",
    "What’s the most random fact you know?"
]

dares = [
    "Sing your favorite song",
    "Do 10 push-ups",
    "Send a funny sticker",
    "Dance for 30 seconds without music",
    "Talk in an accent for 5 minutes",
    "Post a silly selfie to your story",
    "Say the alphabet backwards",
    "Eat a spoonful of ketchup",
    "Imitate your favorite celebrity",
    "Send a voice note of you laughing like a villain",
    "Do your best chicken dance",
    "Pretend to be a dog for 1 minute",
    "Call someone and say you love pineapples",
    "Do 15 jumping jacks",
    "Draw a mustache on your face and keep it for 10 minutes",
    "Act like a monkey until your next turn",
    "Try to touch your nose with your tongue",
    "Text your crush 'I like you' (then delete if needed)",
    "Do a handstand or try",
    "Try to lick your elbow",
    "Speak without moving your lips for 2 minutes",
    "Show the last photo in your gallery",
    "Eat something spicy right now",
    "Talk in gibberish for the next round",
    "Draw a portrait of someone using your non-dominant hand",
    "Imitate someone in the group",
    "Try to juggle 3 things",
    "Balance something on your head for 1 minute",
    "Do your best robot dance",
    "Give yourself a weird nickname and use it for the next hour",
    "Write a poem on the spot and recite it",
    "Change your profile pic to something funny for 5 minutes",
    "Type with your toes and send the result",
    "Say a tongue twister 5 times fast",
    "Do 20 squats",
    "Pretend you’re underwater for 1 minute",
    "Make a funny face and keep it for 30 seconds",
    "Speak like Yoda for 3 minutes",
    "Try to do a magic trick",
    "Talk using only emojis for one round",
    "Post “I believe in aliens” on your status",
    "Do a cartwheel or roll on the floor",
    "Wrap yourself in a blanket and pretend to be a burrito",
    "Try to whistle with a mouthful of water",
    "Make a hat out of paper and wear it",
    "Put 5 ice cubes down your shirt",
    "Draw a tattoo on your arm with pen",
    "Pretend to cry like a baby for 1 minute",
    "Act like your phone is a baby and sing it a lullaby",
    "Speak like a robot for the next 5 minutes",
    "Do a silly walk across the room",
    "Try to breakdance for 10 seconds",
    "Try to moonwalk",
    "Hold your breath for 20 seconds",
    "Wear socks on your hands for 5 minutes",
    "Act like a zombie and scare someone",
    "Pretend you’re a famous actor giving a speech",
    "Spin around 10 times and try to walk straight",
    "Do the floss dance for 30 seconds"
]

compliments = [
    "You have an incredible sense of humor!",
    "Your determination is inspiring.",
    "You have a talent for making people feel at ease.",
    "You are a beacon of hope and positivity.",
    "Your intelligence shines through in everything you do.",
    "You have a heart that understands others.",
    "Your presence is a gift to everyone around you.",
    "You are a wonderful friend.",
    "Your passion is contagious!",
    "You have a way of making people feel valued.",
    "You are a true original, and that's what makes you special.",
    "Your enthusiasm is refreshing.",
    "You handle challenges with such grace.",
    "You have an eye for beauty in the world.",
    "Your support means the world to me.",
    "You make every day brighter just by being you.",
    "Your insights are always so valuable.",
    "You bring joy to those around you.",
    "You have a great sense of style!",
    "Your courage is truly commendable.",
    "You radiate positivity.",
    "Your creativity knows no bounds.",
    "You have a unique perspective on life.",
    "Your kindness is a balm to everyone who encounters it.",
    "You inspire others to be their best selves.",
    "Your smile lights up the room.",
    "You are an amazing listener.",
    "Your enthusiasm is infectious.",
    "You have a beautiful soul.",
    "Your energy is uplifting.",
    "You make the world a better place just by being in it.",
    "You have a gift for bringing people together.",
    "Your laughter is music to my ears.",
    "You are so talented!",
    "Your ability to see the good in people is admirable.",
    "You have a wonderful way with words.",
    "Your strength is admirable.",
    "You are full of wisdom beyond your years.",
    "Your compassion is unmatched.",
    "You have a great sense of adventure!",
    "Your determination is inspiring to others.",
    "You are an invaluable part of this team.",
    "Your optimism is refreshing.",
    "You have a magnetic personality!",
    "Your attention to detail is impressive.",
    "You are so thoughtful and considerate.",
    "Your authenticity is refreshing.",
    "You have a way of making everything better.",
    "Your smile can brighten the darkest day.",
    "You are a ray of sunshine on a cloudy day.",
    "Your zest for life is contagious!",
    "You have such a warm and welcoming spirit.",
    "Your intelligence is truly impressive.",
    "You bring out the best in others.",
    "Your perspective is always enlightening.",
    "You have an incredible work ethic.",
    "You are so resourceful!",
    "Your laughter brings joy to those around you.",
    "You have such a positive influence on those around you.",
    "Your ability to connect with others is remarkable.",
    "You have an amazing ability to adapt to any situation.",
    "Your generosity knows no bounds.",
    "You are such a great problem solver!",
    "Your passion for your interests is inspiring.",
    "You make even the mundane seem exciting!",
    "Your insights always make me think deeper.",
    "You are incredibly empathetic.",
    "Your friendship is one of my greatest treasures.",
    "You are always willing to lend a hand.",
    "Your love for learning is admirable.",
    "You have a knack for making people feel special.",
    "Your resilience is truly inspiring.",
    "You have an extraordinary ability to make others laugh.",
    "Your presence brings peace to those around you.",
    "You are so dependable and trustworthy.",
    "Your curiosity about the world is refreshing.",
    "You possess such grace under pressure.",
    "Your ideas are always innovative and fresh!",
    "You have an amazing ability to uplift others' spirits.",
    "Your thoughtfulness is a rare quality.",
    "You're an incredible communicator!",
    "Your kindness leaves a lasting impression on everyone you meet.",
    "You have a beautiful way of expressing yourself.",
    "Your laughter can light up any room!",
    "You're an inspiration to everyone around you!",
    "You're so easy to talk to; I appreciate that about you!",
    "You're like a breath of fresh air!",
]

roasts = [
    "You're the reason the gene pool needs a lifeguard.",
    "You bring everyone so much joy… when you leave the room.",
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "I'd agree with you, but then we'd both be wrong.",
    "You're proof that even evolution makes mistakes.",
    "You're like a software update. Whenever I see you, I think, 'Not now.'",
    "You have the right to remain silent because whatever you say will probably be stupid anyway.",
    "If laughter is the best medicine, your face must be curing the world.",
    "You're as useless as the 'ueue' in 'queue.'",
    "I’d explain it to you, but I left my English-to-Dingbat dictionary at home.",
    "You’re not stupid; you just have bad luck when it comes to thinking.",
    "You're like a candle in the wind—useless and annoying.",
    "Your secrets are always safe with me. I never even listen when you tell me them.",
    "I’d call you a tool, but that implies you’re actually useful.",
    "You're about as useful as a screen door on a submarine.",
    "You have an entire life to be an idiot. Why not take today off?",
    "You're like a software license agreement. Everyone just ignores you.",
    "You're like a broken pencil—pointless.",
    "I'd explain it to you, but I don't have any crayons.",
    "You're so dense, light bends around you.",
    "I’d ask how old you are, but I know you can’t count that high.",
    "You're like a slinky; not really good for anything, but you bring a smile when you fall down the stairs.",
    "You’re like a light switch; even when you’re on, you’re still dim.",
    "You bring everyone so much joy… when you leave the room.",
    "You're like a software bug—nobody wants you around.",
    "If I had a dollar for every time I saw someone as dumb as you, I’d have one dollar.",
    "Your face makes onions cry.",
    "You're the reason God created the middle finger.",
    "You're like a dictionary—full of useless information.",
    "I'd call you a tool, but that implies you're actually useful.",
    "Your only chance of getting laid is by crawling up a chicken's butt and waiting.",
    "You're proof that even evolution makes mistakes.",
    "You're like a black hole; you suck all the fun out of the room.",
    "I would call you a joke, but that would imply you're funny.",
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "I'd explain it to you, but I don't have any crayons.",
    "You’re so full of it, even your shadow leaves you.",
    "You bring everyone so much joy... when you leave the room.",
    "You're about as useful as a chocolate teapot.",
    "I'd give you a nasty look, but you've already got one.",
    "You're like a software update. Whenever I see you, I think, 'Not now.'",
    "You’re like a broken pencil—pointless.",
    "If ignorance is bliss, you must be the happiest person on the planet.",
    "You're not stupid; you just have bad luck when it comes to thinking.",
    "You're like a candle in the wind—useless and annoying.",
    "You have an entire life to be an idiot. Why not take today off?",
    "If brains were dynamite, you wouldn't have enough to blow your nose.",
    "You're so dense, light bends around you.",
    "I’d ask how old you are, but I know you can’t count that high.",
    "You're about as useful as a screen door on a submarine.",
    "You're like a software bug—nobody wants you around.",
    "I'd call you a tool, but that implies you're actually useful.",
    "You bring everyone so much joy… when you leave the room.",
    "You’re like a slinky; not really good for anything, but you bring a smile when you fall down the stairs.",
    "Your face makes onions cry.",
    "You’re proof that even evolution makes mistakes.",
    "I'd explain it to you, but I left my English-to-Dingbat dictionary at home.",
    "You're like a black hole; you suck all the fun out of the room.",
    "I would call you a joke, but that would imply you're funny.",
    "You're so full of it, even your shadow leaves you.",
    "If laughter is the best medicine, your face must be curing the world.",
    "You’re as useless as the 'ueue' in 'queue.'",
    "I’d give you a nasty look, but you've already got one.",
    "You have an entire life to be an idiot. Why not take today off?",
]

jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my computer I needed a break, and it said 'No problem – I'll go to sleep.'",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why don't skeletons fight each other? They don't have the guts.",
    "What do you call fake spaghetti? An impasta!",
    "Why did the bicycle fall over? Because it was two-tired!",
    "What do you call cheese that isn't yours? Nacho cheese!",
    "Why did the math book look sad? Because it had too many problems.",
    "How does a penguin build its house? Igloos it together!",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why can't you give Elsa a balloon? Because she will let it go!",
    "What do you call a fish wearing a bowtie? Sofishticated.",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "How does a scientist freshen her breath? With experi-mints!",
    "What did one wall say to the other wall? 'I'll meet you at the corner!'",
    "Why did the coffee file a police report? It got mugged!",
    "What do you call an alligator in a vest? An investigator!",
    "What do you get when you cross a snowman and a vampire? Frostbite!",
    "Why did the cookie go to the hospital? Because it felt crummy.",
    "What did the ocean say to the beach? Nothing, it just waved.",
    "Why don’t oysters donate to charity? Because they are shellfish.",
    "What do you call a lazy kangaroo? A pouch potato!",
    "Why was the math book sad? Because it had too many problems.",
    "Why do cows have hooves instead of feet? Because they lactose.",
    "What do you call a pile of cats? A meowtain.",
    "Why did the picture go to jail? Because it was framed!",
    "How do you organize a space party? You planet!",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
    "What did the janitor say when he jumped out of the closet? 'Supplies!'",
    "Why don't some couples go to the gym? Because some relationships don't work out.",
    "What do you call a factory that makes good products? A satisfactory!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why can't your nose be 12 inches long? Because then it would be a foot!",
    "What did one hat say to the other hat? 'You stay here, I'll go on ahead!'",
    "Why did the computer go to therapy? It had too many bytes.",
    "How do you catch a squirrel? Climb a tree and act like a nut!",
    "Why did the stadium get hot after the game? All of the fans left!",
    "What do you call an alligator in a vest? An investigator!",
    "Why don’t scientists trust atoms? Because they make up everything!",
    "How does a penguin build its house? Igloos it together!",
    "What did one ocean say to the other ocean? Nothing, they just waved.",
    "Why did the banana go to the doctor? Because it wasn't peeling well.",
    "What do you call a snowman with a six-pack? An abdominal snowman.",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
    "How does a scientist freshen her breath? With experi-mints!",
    "Why don’t skeletons fight each other? They don’t have the guts.",
    "What do you call fake spaghetti? An impasta!",
    "What do you call cheese that isn't yours? Nacho cheese!",
    "How do you make a tissue dance? You put a little boogie in it!",
    "Why did the cookie cry? Because its mom was a wafer (away for) so long.",
    "What do you call an alligator in a vest? An investigator!",
    "Why don't eggs tell jokes? They'd crack each other up.",
    "What’s orange and sounds like a parrot? A carrot!",
    "Why did the mushroom go to the party alone? Because he’s a fungi!",
    "What do you get when you cross a snowman with a dog? Frostbite.",
    "Why was the computer cold? It left its Windows open!",
    "Why did the chicken join a band? Because it had the drumsticks!",
    "How does a scientist freshen her breath? With experi-mints!",
    "What do you call an elephant that doesn’t matter? An irrelephant.",
    "Why did the man put his money in the blender? Because he wanted to make some liquid assets!",
    "Why was the broom late? It swept in.",
    "What kind of shoes do ninjas wear? Sneakers.",
    "How does Moses make his coffee? Hebrews it.",
    "What’s brown and sticky? A stick.",
]

personalities = [
    "Kind", "Funny", "Rude", "Caring", "Introvert", "Extrovert", "Creative", 
    "Lazy", "Hardworking", "Bold", "Adventurous", "Thoughtful", "Optimistic", 
    "Pessimistic", "Charming", "Witty", "Empathetic", "Determined", "Laid-back", 
    "Spontaneous", "Analytical", "Curious", "Generous", "Skeptical", "Friendly", 
    "Serious", "Passionate", "Supportive", "Independent", "Sociable", 
    "Nurturing", "Pragmatic", "Artistic", "Intellectual", "Playful", 
    "Resourceful", "Patient", "Impatient", "Ambitious", "Realistic",
    "Sensitive", "Confident", "Humble", "Loyal", "Daring"
]

magic_responses = [
    "Yes, absolutely.",
    "No way.",
    "Maybe later.",
    "Definitely!",
    "Ask again.",
    "Looks promising!",
    "Highly unlikely.",
    "Not sure, try flipping a coin.",
    "It’s a strong possibility.",
    "I wouldn’t count on it.",
    "The stars say yes!",
    "Don’t hold your breath.",
    "Chances are slim.",
    "The answer is unclear, try again.",
    "You might want to reconsider.",
    "The future is bright!",
    "It's not looking good.",
    "Trust your instincts.",
    "Absolutely not.",
    "A resounding yes!",
    "Time will tell."
]

riddles = [
    {"q": "What has to be broken before you can use it?", "a": "egg"},
    {"q": "I’m tall when I’m young, and I’m short when I’m old. What am I?", "a": "candle"},
    {"q": "What month of the year has 28 days?", "a": "all"},
    {"q": "What is full of holes but still holds water?", "a": "sponge"},
    {"q": "What question can you never answer yes to?", "a": "are you asleep?"},
    {"q": "I have keys but open no locks. What am I?", "a": "piano"},
    {"q": "What can travel around the world while staying in a corner?", "a": "stamp"},
    {"q": "What gets wetter as it dries?", "a": "towel"},
    {"q": "What has a heart that doesn’t beat?", "a": "artichoke"},
    {"q": "What begins with T, ends with T, and has T in it?", "a": "teapot"},
    {"q": "What has one eye but cannot see?", "a": "needle"},
    {"q": "What has many teeth but cannot bite?", "a": "comb"},
    {"q": "What runs around the yard without moving?", "a": "fence"},
    {"q": "What can you catch but not throw?", "a": "cold"},
    {"q": "What has hands but can’t clap?", "a": "clock"},
    {"q": "I speak without a mouth and hear without ears. What am I?", "a": "echo"},
    {"q": "What has an eye but cannot see?", "a": "hurricane"},
    {"q": "What is so fragile that saying its name breaks it?", "a": "silence"},
    {"q": "I have branches, but no fruit, trunk or leaves. What am I?", "a": "bank"},
    {"q": "What is always in front of you but can’t be seen?", "a": "future"},
    {"q": "What goes up but never comes down?", "a": "age"},
    {"q": "The more you take, the more you leave behind. What am I?", "a": "footsteps"},
    {"q": "I can be cracked, made, told, and played. What am I?", "a": "joke"},
    {"q": "What has words but never speaks?", "a": "book"},
    {"q": "What can fill a room but takes up no space?", "a": "light"},
    {"q": "What has four wheels and flies?", "a": "garbage truck"},
    {"q": "I have lakes with no water, mountains with no stone, and cities with no buildings. What am I?", "a": "map"},
    {"q": "What begins with an E and only contains one letter?", "a": "envelope"},
    {"q": "What is easy to get into, but hard to get out of?", "a": "trouble"},
    {"q": "What comes once in a minute, twice in a moment, but never in a thousand years?", "a": "'m'"},
    {"q": "I’m light as a feather, yet the strongest person can’t hold me for five minutes. What am I?", "a": "breath"},
    {"q": "What has a neck but no head?", "a": "bottle"},
    {"q": "What can you keep after giving to someone?", "a": "your word"},
    {"q": "What has a thumb and four fingers but is not alive?", "a": "glove"},
    {"q": "What has cities, but no houses; forests, but no trees; and rivers, but no water?", "a": "map"},
    {"q": "If you drop me, I'm sure to crack, but if you smile at me, I'll smile back. What am I?", "a": "mirror"},
    {"q": "I have no life, but I can die. What am I?", "a": "battery"},
    {"q": "What can you hold in your left hand but not in your right?", "a": "your right hand"},
    {"q": "You see me once in June, twice in November, but not at all in May. What am I?", "a": "'e'"},
    {"q": "I am taken from a mine and shut up in a wooden case, from which I am never released. What am I?", "a": "pencil lead"},
    {"q": "What has legs but doesn't walk?", "a": "table"},
    {"q": "I have keys but open no locks. What am I?", "a": "keyboard"},
    {"q": "The more you take away from me, the larger I become. What am I?", "a": "hole"},
    {"q": "What is at the end of a rainbow?", "a": "'w'"},
    {"q": "I go in hard, come out soft, and am never the same. What am I?", "a": "'chewing gum'"},
    {"q": "I fly without wings, I cry without eyes. Whenever I go, darkness flies. What am I?", "a": "'cloud'"},
    {"q": "'I have a tail and a head, but no body. What am I?'", 'answer': 'coin'},
    {"q":"I have keys that open no locks. What am I?","answer":"piano"},
    {"q":"What begins with an E and only contains one letter?","answer":"envelope"},
    {"q":"I have branches yet I have no leaves, no trunk and no fruit. What am I?","answer":"bank"},
    {"q":"You see me once in June, twice in November, but not at all in May. What am I?","answer":"'e'"},
    {"q":"I have lakes with no water, mountains with no stone, and cities with no buildings. What am I?","answer":"map"},
    {"q":"The more you take away from me, the larger I become. What am I?","answer":"hole"},
    {"q":"I’m light as a feather yet the strongest person can’t hold me for five minutes. What am I?","answer":"breath"},
    {"q":"What comes down but never goes up?","answer":"rain"},
    {"q":"I have teeth but cannot bite. What am I?","answer":"comb"},
    {"q":"What begins with T, ends with T, and has T in it?","answer":"teapot"},
    {"q":"I have a bed but do not sleep. What am I?","answer":"river"},
    {"q":"The more there is, the less you see. What is it?","answer":"darkness"},
    {"q":"I go in hard, come out soft, and am never the same. What am I?","answer":"gum"},
    {"q":"What can be broken but never held?","answer":"promise"},
    {"q":"What has one eye but cannot see?","answer":"needle"},
    {"q":"I can be cracked made told and played. What am I?","answer":"joke"},
    {"q":"You can hold me in your hand yet I can fill an entire room. What am I?","answer":"light"},
    {"q":"I have four legs in the morning, two legs at noon, and three legs in the evening. What am I?","answer":"human (representing stages of life)"},
    {"q":"The more you take away from me the bigger I get. What am I?","answer":"hole"},
    {"q":"You see me once in June, twice in November, but not at all in May. What am I?","answer":"'e'"},
]

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat

        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status in ["administrator", "creator"]:
            return await func(update, context)
        else:
            await update.message.reply_text("❌ You must be an admin to use this command.")
    return wrapper


async def log_action(text: str, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,  # Set this value at the top of your file
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"[Log Error] {e}")

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from datetime import datetime
import asyncio

BOT_START_TIME = datetime.utcnow()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message or update.callback_query.message
    chat = update.effective_chat

    # Group or channel
    if chat.type in ["group", "supergroup", "channel"]:
        uptime = datetime.utcnow() - BOT_START_TIME
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        return await message.reply_text(f"✅ I am online!\n⏱ Uptime: `{uptime_str}`", parse_mode="Markdown")

    # Private chat animation
    try:
        anim_msg = await message.reply_text("𝗪𝗲𝗹𝗰𝗼𝗺𝗲..")
        await asyncio.sleep(0.5)
        await anim_msg.edit_text("𝗪𝗲𝗹𝗰𝗼𝗺𝗲....")
        await asyncio.sleep(0.8)
        await anim_msg.edit_text(
            f"[{user.first_name}](tg://user?id={user.id}) Nɪᴄᴇ ᴛᴏ Mᴇᴇᴛ Yᴏᴜ", parse_mode="Markdown"
        )
        await asyncio.sleep(1)
        await anim_msg.edit_text("I'ᴍ ʏᴏᴜʀ sᴍᴀʀᴛ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴀssɪsᴛᴀɴᴛ.")
        await asyncio.sleep(0.5)
        await anim_msg.edit_text(
            "Pᴏᴡᴇʀᴇᴅ ʙʏ : [Anime Asia Community](https://t.me/Anime_Asia_Community)",
            parse_mode="Markdown"
        )
        await asyncio.sleep(1)
        await anim_msg.delete()
    except Exception as e:
        print(f"❌ Animation failed: {e}")

    # Buttons
    keyboard = [
        [InlineKeyboardButton("➕ Add Me", url="https://t.me/SerenaProbot?startgroup=true")],
        [
            InlineKeyboardButton("📢 Updates", url="https://t.me/AshxBots"),
            InlineKeyboardButton("🆘 Support", url="https://t.me/AACBotSupport"),
            InlineKeyboardButton("🧠 Menu", callback_data="main_menu")
        ],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/AshKetchum_001")]
    ]

    await message.reply_video(
        video="https://envs.sh/e_B.mp4",
        caption=(
            "👋 *Welcome to Serena!*\n\n"
            "I'm your smart group management assistant.\n"
            "Click the buttons below to explore features or add me to your group!"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    

async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        if gban_col.find_one({"_id": user_id}):
            await update.message.reply_text("⚠️ User is already globally banned.")
            return

        gban_col.insert_one({"_id": user_id})
        await update.message.reply_text("🚫 User globally banned.")

        async for dialog in context.bot.get_my_chats():
            if dialog.type.name in ["GROUP", "SUPERGROUP"]:
                try:
                    await context.bot.ban_chat_member(dialog.id, user_id)
                except:
                    pass

        await log_action(context, f"🚫 *Globally Banned:* [{user_id}](tg://user?id={user_id})")

async def ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        if not gban_col.find_one({"_id": user_id}):
            return await update.message.reply_text("✅ User is not globally banned.")

        gban_col.delete_one({"_id": user_id})
        await update.message.reply_text("✅ User globally unbanned.")

        async for dialog in context.bot.get_my_chats():
            if dialog.type.name in ["GROUP", "SUPERGROUP"]:
                try:
                    await context.bot.unban_chat_member(dialog.id, user_id)
                except:
                    pass

        await log_action(context, f"✅ *Global Unban:* [{user_id}](tg://user?id={user_id})")

                                                        
# === /menu ===

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

# Random images for menu background
menu_images = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    # Add more URLs if you want
]

# Define command categories and descriptions
COMMAND_CATEGORIES = {
    "admin_menu": {
        "title": "👮 Admin Commands",
        "commands": [
            "/admin - Access admin functions",
            "/gban - Globally ban a user",
            "/ungban - Remove global ban",
            "/fullpromote - Full admin privileges",
            "/create - Create a group",
            "/broadcast - Send a message to all"
        ]
    },
    "mod_menu": {
        "title": "🛡️ Moderation",
        "commands": [
            "/warn - Warn a user",
            "/resetwarns - Reset user warnings",
            "/mute - Mute a user",
            "/unmute - Unmute a user",
            "/ban - Ban a user",
            "/unban - Unban a user",
            "/kick - Kick a user",
            "/kickme - Kick yourself",
            "/promote - Promote to admin",
            "/demote - Demote to member",
            "/pin - Pin a message",
            "/unpin - Unpin a message",
            "/purge - Delete multiple messages",
            "/tagall, /mentionall - Mention everyone",
            "/utag, /mentiona - Mention all (alternative)",
            "/cancel, /stop - Stop tagging",
            "/invite - Get group invite link",
            "/del - Delete a specific message",
            "/zombies - Remove deleted accounts",
            "/bword - Ban a word",
            "/ubword - Unban a word",
            "/setrules - Set group rules",
            "/rules - Show group rules",
            "/welcome - Set welcome message",
            "/translate - Translate text",
            "/report - Report a user"
        ]
    },
    "util_menu": {
        "title": "🧰 Utilities",
        "commands": [
            "/userinfo - Get user info",
            "/id - Get chat/user ID",
            "/remind - Set reminder",
            "/fix - Fix any Python code",
            "/time - Show current time"
        ]
    },
    "info_menu": {
        "title": "ℹ️ Info & Start",
        "commands": [
            "/start or /chaluhoja - Start bot",
            "/help - Show help menu",
            "/menu - Show all options"
        ]
    },
    "gban_menu": {
        "title": "🎮 Fun & Games",
        "commands": [
            "/ping - Check bot response",
            "/dice, /dart, /football, /basketball, /slot - Random games",
            "/roll - Roll a random number",
            "/flip, /coin - Flip a coin",
            "/magicball, /predict - Magic 8 ball",
            "/myluck - Check your luck",
            "/wish - Wish checker",
            "/truth - Truth question",
            "/dare - Dare challenge",
            "/guess - Guessing game",
            "/joke, /jokes - Tell a joke",
            "/roast - Roast a user",
            "/flirt, /compliment - Compliment/flirt",
            "/intelligent, /iq - Intelligence rating",
            "/myself - Your personality traits",
            "/riddle - Solve a riddle",
            "/quiz - Math quiz"
        ]
    },
    "stats_menu": {
        "title": "📊 Stats & Logs",
        "commands": [
            "/statics - Bot statistics and database info",
            "/ratebot - Rate the bot",
            "/groups - List groups using bot"
        ]
    }
}

# Callback handler function
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    img_url = random.choice(menu_images)
    back_btn = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]

    if query.data in COMMAND_CATEGORIES:
        section = COMMAND_CATEGORIES[query.data]
        caption = f"**{section['title']}**\n\n" + "\n".join(section["commands"]) + "\n\nUpdates: @AshxBots"

        await query.message.edit_media(
            media=InputMediaPhoto(media=img_url, caption=caption, parse_mode="Markdown"),
            reply_markup=InlineKeyboardMarkup(back_btn)
        )

    elif query.data == "main_menu":
        main_menu_keyboard = [
            [
                InlineKeyboardButton("👮 Admin Tools", callback_data="admin_menu"),
                InlineKeyboardButton("🛡️ Moderation", callback_data="mod_menu")
            ],
            [
                InlineKeyboardButton("🧰 Utilities", callback_data="util_menu"),
                InlineKeyboardButton("ℹ️ Info & Rules", callback_data="info_menu")
            ],
            [
                InlineKeyboardButton("🌐 Funs & Games", callback_data="gban_menu"),
                InlineKeyboardButton("📊 Stats & Logs", callback_data="stats_menu")
            ]
        ]

        await query.message.edit_media(
            media=InputMediaPhoto(
                media=img_url,
                caption="**🧠 Serena Menu**\n\nChoose a category below to explore available commands.",
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard)
        )

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message

    text = f"🆔 *ID Info:*\n"
    text += f"👤 User ID: `{user.id}`\n"
    text += f"💬 Chat ID: `{chat.id}`\n"
    text += f"📩 Message ID: `{msg.message_id}`"

    await msg.reply_text(text, parse_mode="Markdown")


async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    total_users = users_col.count_documents({})
    total_admins = admins_col.count_documents({})
    await update.callback_query.message.reply_text(
        f"📊 *Bot Stats:*\n\n👥 Total Users: `{total_users}`\n👮 Admins: `{total_admins}`",
        parse_mode="Markdown"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    img_url = random.choice(menu_images)

    main_menu_keyboard = [
        [
            InlineKeyboardButton("👮 Admin Tools", callback_data="admin_menu"),
            InlineKeyboardButton("🛡️ Moderation", callback_data="mod_menu")
        ],
        [
            InlineKeyboardButton("🧰 Utilities", callback_data="util_menu"),
            InlineKeyboardButton("ℹ️ Info & Rules", callback_data="info_menu")
        ],
        [
            InlineKeyboardButton("🌐 Funs & Games", callback_data="gban_menu"),
            InlineKeyboardButton("📊 Stats & Logs", callback_data="stats_menu")
        ]
    ]

    await update.message.reply_photo(
        photo=img_url,
        caption="**🧠 Serena Menu**\n\nChoose a category below to explore available commands.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard)
    )

# === Admin Management ===
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        if not admins_col.find_one({"_id": user_id}):
            admins_col.insert_one({"_id": user_id})
            ADMINS.append(user_id)
            await update.message.reply_text(f"✅ Added {user_id} as an admin.")


# === Group Commands ===
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        return
    if update.message.reply_to_message:
        await context.bot.restrict_chat_member(
            update.message.chat.id,
            update.message.reply_to_message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text("🔇 User muted.")


async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        return
    if update.message.reply_to_message:
        await context.bot.restrict_chat_member(
            update.message.chat.id,
            update.message.reply_to_message.from_user.id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text("🔊 User unmuted.")


async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        return
    if update.message.reply_to_message:
        await context.bot.ban_chat_member(update.message.chat.id, update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🚫 User banned.")


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        return
    if update.message.reply_to_message:
        await context.bot.unban_chat_member(update.message.chat.id, update.message.reply_to_message.from_user.id)
        await update.message.reply_text("✅ User unbanned.")


async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to the user to promote.")

    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=update.message.reply_to_message.from_user.id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_chat=True
        )
        await update.message.reply_text("✅ User promoted.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")

from telegram import ChatAdministratorRights

async def fullpromote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user to fully promote them.")

    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id

    try:
        await context.bot.promote_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,  # Change to True if you want them to promote others
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_post_messages=True,
            can_edit_messages=True,
        )
        await update.message.reply_text("✅ User fully promoted with all admin rights!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error promoting user:\n`{e}`", parse_mode="Markdown")

async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to the user to demote.")

    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=update.message.reply_to_message.from_user.id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_manage_chat=False,
            can_promote_members=False,
        )
        await update.message.reply_text("✅ User demoted.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")


async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        return
    if update.message.reply_to_message:
        await context.bot.pin_chat_message(update.message.chat.id, update.message.reply_to_message.message_id)
        await update.message.reply_text("📌 Message pinned.")


async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        return
    await context.bot.unpin_chat_message(update.message.chat.id)
    await update.message.reply_text("📍 Message unpinned.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a message to broadcast it.")

    # Message text to broadcast
    msg = update.message.reply_to_message

    # Pull all group IDs from MongoDB
    groups = list(db.groups.find({}, {"chat_id": 1}))
    success, failed = 0, 0

    for group in groups:
        gid = group["chat_id"]
        try:
            await context.bot.forward_message(chat_id=gid, from_chat_id=msg.chat.id, message_id=msg.message_id)
            success += 1
        except Exception as e:
            logger.warning(f"❌ Failed to send to {gid}: {e}")
            failed += 1
        await asyncio.sleep(0.35)

    await update.message.reply_text(f"✅ Broadcast complete.\nSent: {success}\nFailed: {failed}")
# Warn system using MongoDB
# Mongo: warnings { _id: {chat_id}:{user_id}, count: int }

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user to warn them.")
    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id
    key = f"{chat_id}:{user_id}"
    current = await db.warnings.find_one({"_id": key}) or {"count": 0}
    current["count"] += 1
    await db.warnings.update_one({"_id": key}, {"$set": {"count": current["count"]}}, upsert=True)
    await update.message.reply_text(f"⚠️ Warned! Total warnings: {current['count']}")

async def resetwarns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to user to reset their warnings.")
    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id
    key = f"{chat_id}:{user_id}"
    await db.warnings.delete_one({"_id": key})
    await update.message.reply_text("✅ Warnings reset.")
        
        # /setrules
async def setrules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        return
    text = ' '.join(context.args)
    if not text:
        return await update.message.reply_text("Usage: /setrules Your rules here...")
    db["rules"].update_one({"_id": update.message.chat_id}, {"$set": {"text": text}}, upsert=True)
    await update.message.reply_text("✅ Rules updated.")
# /rules
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = db["rules"].find_one({"_id": update.message.chat_id})
    if data:
        await update.message.reply_text(f"📜 *Group Rules:*\n{data['text']}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No rules set.")

# ✅ Only ONE welcome() function
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        # Global ban check
        if gban_col.find_one({"_id": member.id}):
            await context.bot.ban_chat_member(update.message.chat.id, member.id)
            await log_action(context, f"🚫 *Auto-Enforced GBan:* [{member.id}](tg://user?id={member.id})")
            continue

        # Send welcome message
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Updates", url="https://t.me/AshxUpdates")]
        ])
        await update.message.reply_photo(
            photo="https://telegra.ph/file/5877f05d250f7d1fbe34f.jpg",
            caption=f"👋 Welcome, [{member.first_name}](tg://user?id={member.id})!\nEnjoy your stay!",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
async def userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"👤 User Info:\n"
        f"• ID: `{user.id}`\n"
        f"• First Name: `{user.first_name}`\n"
        f"• Username: @{user.username if user.username else 'None'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

        
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await update.message.reply_text(f"🆔 User ID: `{user.id}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"🆔 Your ID: `{update.message.from_user.id}`", parse_mode="Markdown")
        
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        return
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.ban_chat_member(update.message.chat.id, user_id)
        await context.bot.unban_chat_member(update.message.chat.id, user_id)
        await update.message.reply_text("👢 User kicked from the group.")
async def kickme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.ban_chat_member(update.message.chat.id, update.message.from_user.id)
    await context.bot.unban_chat_member(update.message.chat.id, update.message.from_user.id)
    
# Required imports
from telegram import Update, ChatMemberAdministrator, ChatMemberOwner
from telegram.constants import ParseMode, ChatType
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import asyncio

# Keep track of active tag sessions
spam_chats = []

# Tag-All Command Handler
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



from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from pymongo import MongoClient

# Your MongoDB client


# Track start time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import platform  # Replace with your actual owner ID
BOT_START_TIME = datetime.utcnow()

async def botstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Only the owner can use this command.")
        return

    uptime = datetime.utcnow() - BOT_START_TIME
    days, remainder = divmod(int(uptime.total_seconds()), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    # Replace with your MongoDB document counts
    total_users = await users_col.count_documents({})
    total_admins = await admins_col.count_documents({})

    python_ver = platform.python_version()

    text = (
        f"📊 <b>Bot Statistics</b>\n\n"
        f"👤 Total Users: <code>{total_users}</code>\n"
        f"👮 Admins: <code>{total_admins}</code>\n"
        f"⏱ Uptime: <code>{uptime_str}</code>\n\n"
        f"⚙️ Python: <code>{python_ver}</code>"
    )

    buttons = [
        [InlineKeyboardButton("👤 Owner", url="https://t.me/AshKetchum_001")]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
                          
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a message to report it.")

    chat_id = update.effective_chat.id
    admins = await context.bot.get_chat_administrators(chat_id)
    mentions = "\n".join([f"• [{admin.user.first_name}](tg://user?id={admin.user.id})" for admin in admins])

    await update.message.reply_text(
        f"🚨 Report submitted to admins:\n\n{mentions}",
        parse_mode="Markdown"
    )

async def truth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔥 Truth:\n\n{random.choice(truths)}")

async def dare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎯 Dare:\n\n{random.choice(dares)}")
        
async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a message to start purging.")

    from_msg = update.message.reply_to_message.message_id
    to_msg = update.message.message_id

    for msg_id in range(from_msg, to_msg + 1):
        try:
            await context.bot.delete_message(update.effective_chat.id, msg_id)
        except:
            pass

    await update.message.reply_text("🧹 Purge completed.")                                                                    
import time

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end = time.time()
    latency = int((end - start) * 1000)
    await msg.edit_text(f"🏓 Pong! `{latency}ms`", parse_mode="Markdown")
    
async def invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        link = await context.bot.export_chat_invite_link(update.effective_chat.id)
        await update.message.reply_text(f"🔗 Invite Link:\n{link}")
    except:
        await update.message.reply_text("⚠️ I need permission to manage group invites.")
            
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = int(context.args[0]) if context.args else 100
    result = random.randint(1, num)
    await update.message.reply_text(f"You rolled: {result}")
    
from telegram import Update
from telegram.ext import ContextTypes

# 🎲 Standard Dice
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice(emoji="🎲")

# 🏀 Basketball
async def basketball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice(emoji="🏀")

# 🎳 Bowling
async def bowling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice(emoji="🎳")

# 🎯 Dart
async def dart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice(emoji="🎯")

# ⚽ Football / Soccer
async def football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice(emoji="⚽")

# 🎰 Slot Machine
async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice(emoji="🎰")
        
async def zombies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    count = 0
    async for member in context.bot.get_chat_administrators(chat_id):
        pass  # Just preload admin cache to avoid missing admin check later
    async for user in context.bot.get_chat_members(chat_id):
        if user.user.is_deleted:
            try:
                await context.bot.ban_chat_member(chat_id, user.user.id)
                await context.bot.unban_chat_member(chat_id, user.user.id)
                count += 1
            except:
                continue
    await update.message.reply_text(f"🧟 Removed {count} deleted accounts.")
    

async def create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("🚫 You are not authorized to use this command.")

    title = "New Group"
    if context.args:
        title = " ".join(context.args).strip()

    try:
        # Create group with the bot and owner
        result = await context.bot.create_chat(title=title, user_ids=[OWNER_ID])
        group_chat = result.id

        # Promote the owner to admin
        await context.bot.promote_chat_member(
            chat_id=group_chat,
            user_id=OWNER_ID,
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
        )

        await update.message.reply_text(
            f"✅ Group **{title}** created successfully!\n"
            f"Group ID: `{group_chat}`",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")  
        
async def coin_flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = random.choice(["Heads", "Tails"])
    await update.message.reply_text(f"🪙 The coin landed on: *{result}*", parse_mode="Markdown")
    
async def luckrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    rate = random.randint(0, 100)
    await update.message.reply_text(f"⭐️ {user} is *{rate}%* Lucky today!", parse_mode="Markdown")               
    
async def wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("✨ Usage: `/wish <your wish>`", parse_mode="Markdown")

    wish_text = " ".join(context.args)
    rate = random.randint(0, 100)
    await update.message.reply_text(
        f"🔮 *Wish:* `{wish_text}`\n\n✅ Success chance: *{rate}%*",
        parse_mode="Markdown"
    )  


async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 10)
    await update.message.reply_text("🎯 I'm thinking of a number between 1 and 10. Try to guess!")

    def check_reply(reply: Update):
        return reply.message.reply_to_message and reply.message.reply_to_message.message_id == update.message.message_id

    try:
        guess_msg = await context.bot.wait_for_message(timeout=15, filters=filters.TEXT & filters.REPLY, check=check_reply)
        if guess_msg and int(guess_msg.text.strip()) == number:
            await update.message.reply_text("✅ Correct! You're good at this!")
        else:
            await update.message.reply_text(f"❌ Nope! I was thinking of `{number}`.", parse_mode="Markdown")
    except:
        await update.message.reply_text(f"⏰ Time's up! The number was `{number}`.", parse_mode="Markdown")

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_in_thread(update, context, f"😂 {random.choice(jokes)}")

async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_in_thread(update, context, f"🔥 {random.choice(roasts)}")

async def compliment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_in_thread(update, context, f"😊 {random.choice(compliments)}")

async def intelligencerate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    rate = random.randint(10, 160)
    await send_in_thread(update, context, f"🧠 {user}'s IQ is approximately *{rate}*.", parse_mode="Markdown")

async def magic8ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await send_in_thread(update, context, "🎱 Ask something like: `/magicball Will I be rich?`", parse_mode="Markdown")
    
    response = random.choice(magic_responses)
    await send_in_thread(update, context, f"🎱 {response}")

async def personality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trait = random.choice(personalities)
    await send_in_thread(update, context, f"🧬 Your personality today is: *{trait}*", parse_mode="Markdown")

async def riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = random.choice(riddles)
    await send_in_thread(update, context, f"🧩 Riddle: {r['q']}\n_You have 15 seconds to answer!_", parse_mode="Markdown")

    def answer_filter(msg):
        return msg.chat.id == update.effective_chat.id and msg.text

    try:
        answer_msg = await context.application.bot.wait_for_message(timeout=15, filters=filters.TEXT)
        if answer_msg and r["a"].lower() in answer_msg.text.lower():
            await send_in_thread(update, context, "✅ Correct! You’re a genius.")
        else:
            await send_in_thread(update, context, f"❌ Wrong! Answer was: *{r['a']}*", parse_mode="Markdown")
    except:
        await send_in_thread(update, context, f"⏰ Time’s up! Correct answer was: *{r['a']}*", parse_mode="Markdown")
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)
import random

import random
import asyncio
from telethon import events

@client.on(events.NewMessage(pattern=r"^/quiz$"))
async def math_quiz(event):
    a, b = random.randint(1, 50), random.randint(1, 20)
    operator = random.choice(["+", "-", "*"])
    question = f"{a} {operator} {b}"
    answer = str(eval(question))

    await event.reply(f"Solve: `{question}` (⏳ 30 seconds)", parse_mode="markdown")

    # Event filter for the correct user
    def check_answer(ans_event):
        return ans_event.sender_id == event.sender_id

    try:
        # Wait for user's answer (up to 30 seconds)
        ans_event = await client.wait_for(events.NewMessage(func=check_answer), timeout=30)

        if ans_event.text.strip() == answer:
            await ans_event.reply("🎉 Correct!")
        else:
            await ans_event.reply(f"❌ Wrong! Correct answer was `{answer}`", parse_mode="markdown")

    except asyncio.TimeoutError:
        # If user doesn't answer in 30s
        await event.reply(f"⏰ Time's up! The correct answer was `{answer}`", parse_mode="markdown")

@client.on(events.NewMessage(pattern=r"^/scramble$"))
async def word_scramble(event):
    word = random.choice(words)
    scrambled = ''.join(random.sample(word, len(word)))
    
    await event.reply(f"Unscramble this word: `{scrambled}`", parse_mode="markdown")

    @client.on(events.NewMessage(from_users=event.sender_id))
    async def check_word(ans_event):
        if ans_event.text.strip().lower() == word:
            await ans_event.reply("✅ Correct!")
        else:
            await ans_event.reply("❌ Try again.")
        client.remove_event_handler(check_word)

#Main
@admin_only
async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❗Reply to a message to delete it.")
    
    try:
        await context.bot.delete_message(update.effective_chat.id, update.message.reply_to_message.message_id)
        await update.message.delete()
    except:
        await update.message.reply_text("❌ Can't delete the message.")
@admin_only
async def banword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /banword <word>")
    word = context.args[0].lower()
    banwords_col.update_one(
        {"word": word}, {"$set": {"word": word}}, upsert=True
    )
    await update.message.reply_text(f"🚫 Word `{word}` has been banned.", parse_mode="Markdown")

@admin_only
async def unbanword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /unbanword <word>")
    word = context.args[0].lower()
    result = banwords_col.delete_one({"word": word})
    if result.deleted_count:
        await update.message.reply_text(f"✅ Word `{word}` has been unbanned.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Word not found.")

async def check_banned_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    words = [w['word'] for w in banwords_col.find()]
    for word in words:
        if word in update.message.text.lower():
            try:
                await update.message.delete()
                await update.message.reply_text("⚠️ Banned word detected!", quote=False)
            except:
                pass
            break
from telegram import Update
from telegram.ext import ContextTypes
from deep_translator import GoogleTranslator
from indic_transliteration.sanscript import transliterate, HK, DEVANAGARI

def is_roman_hindi(text: str) -> bool:
    # Very simple heuristic: mostly alphabet characters without native script
    return all(c.isalpha() or c.isspace() for c in text)

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    # Get the original message text to translate
    text_to_translate = None
    target_lang = None

    if update.message.reply_to_message and args:
        # Reply mode
        text_to_translate = update.message.reply_to_message.text
        target_lang = args[0]

    elif len(args) >= 2:
        # Direct command
        target_lang = args[0]
        text_to_translate = " ".join(args[1:])

    else:
        # Not enough arguments
        await update.message.reply_text(
            "❓ Usage:\n"
            "`/translate <lang_code> <text>`\n"
            "Or reply to a message with:\n"
            "`/translate <lang_code>`",
            parse_mode="Markdown"
        )
        return

    try:
        # Try Romanized Hindi transliteration if applicable
        if is_roman_hindi(text_to_translate.lower()):
            devanagari_text = transliterate(text_to_translate, HK, DEVANAGARI)
        else:
            devanagari_text = text_to_translate

        # Translate to target language
        translated = GoogleTranslator(source='auto', target=target_lang).translate(devanagari_text)

        result_text = (
            f"**🔤 Input:** `{text_to_translate}`\n"
            f"**📝 Detected:** `{devanagari_text}`\n"
            f"**🌐 Translation [{target_lang}]:** `{translated}`"
        )

        # Reply to the original message if available
        if update.message.reply_to_message:
            await update.message.reply_to_message.reply_text(result_text, parse_mode="Markdown")
        else:
            await update.message.reply_text(result_text, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{str(e)}`", parse_mode="Markdown")

from datetime import datetime
import pytz

async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now_utc = datetime.now(pytz.utc).strftime("%H:%M:%S UTC")
    await update.message.reply_text(f"🕰️ Current Time:\n`{now_utc}`", parse_mode="Markdown")

import asyncio

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⏰ Use: /remind <seconds> <message>")
    try:
        seconds = int(context.args[0])
        reminder_text = " ".join(context.args[1:])
        await update.message.reply_text(f"🕐 Reminder set in {seconds} sec.")
        await asyncio.sleep(seconds)
        await update.message.reply_text(f"🔔 Reminder: {reminder_text}")
    except ValueError:
        await update.message.reply_text("❌ Invalid time! Use numbers.")
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

# --- Rating System Command ---
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def ratebot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id

        # Check if user already rated
        if ratings_col.find_one({"user_id": user_id}):
            return await update.message.reply_text("⭐ You already rated the bot. Thank you!")

        # Show star buttons
        buttons = [[
            InlineKeyboardButton("⭐", callback_data="rate_1"),
            InlineKeyboardButton("⭐⭐", callback_data="rate_2"),
            InlineKeyboardButton("⭐⭐⭐", callback_data="rate_3"),
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_5"),
        ]]

        await update.message.reply_text(
            "**How would you rate this bot?**",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")


# --- Callback Handler for Ratings ---
async def ratebot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        user_id = query.from_user.id

        # Already rated?
        if ratings_col.find_one({"user_id": user_id}):
            return await query.answer("You've already rated.", show_alert=True)

        # Extract rating number from callback_data
        rating = int(query.data.split("_")[1])

        # Save rating
        ratings_col.insert_one({"user_id": user_id, "rating": rating})

        # Calculate new average
        ratings = list(ratings_col.find())
        total = len(ratings)
        avg = round(sum(r["rating"] for r in ratings) / total, 2)

        await query.edit_message_text(
            f"✅ Thank you for rating!\n\n"
            f"📊 *Average Rating:* {avg} ⭐\n"
            f"🧑‍💻 *Total Ratings:* {total}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await query.edit_message_text(f"❌ Error: `{e}`", parse_mode="Markdown")


import os
import re
import ast
import traceback
from telegram import Update
from telegram.ext import ContextTypes

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', name)

def clean_python_code(code: str) -> str:
    code = code.replace('\t', '    ')
    lines = code.splitlines()

    cleaned_lines = []
    for line in lines:
        stripped = line.rstrip()
        if re.match(r'^\s*(print|debug|logger\.debug)\b', stripped):
            stripped = "# " + stripped
        cleaned_lines.append(stripped)

    if cleaned_lines and cleaned_lines[-1].strip() != "":
        cleaned_lines.append("")

    return "\n".join(cleaned_lines)

async def fixit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user

        if not update.message.reply_to_message or not update.message.reply_to_message.document:
            return await update.message.reply_text("❗ Please reply to a `.py` file to fix.")

        if len(context.args) != 1:
            return await update.message.reply_text("❗ Usage: `/fix <new_filename.py>`", parse_mode="Markdown")

        new_filename = sanitize_filename(context.args[0])
        if not new_filename.endswith(".py"):
            return await update.message.reply_text("❗ Output file must have `.py` extension.")

        doc = update.message.reply_to_message.document
        original_name = sanitize_filename(doc.file_name)

        if not original_name.endswith(".py"):
            return await update.message.reply_text("❌ Only Python (.py) files are supported.")

        os.makedirs("downloads", exist_ok=True)
        original_path = f"downloads/{original_name}"
        fixed_path = f"downloads/{new_filename}"
        log_path = "downloads/fixit_log.txt"

        # Download original file safely
        try:
            file = await doc.get_file()
            await file.download_to_drive(original_path)
        except Exception as e:
            return await update.message.reply_text(f"❌ Failed to download file: `{e}`", parse_mode="Markdown")

        # Read and clean
        with open(original_path, "r", encoding="utf-8-sig") as f:
            code = f.read()
        fixed_code = clean_python_code(code)

        # Save fixed version
        with open(fixed_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        # Syntax check
        log = ""
        try:
            ast.parse(fixed_code)
        except SyntaxError as e:
            log = f"⚠️ SyntaxError: {e}\n\n{traceback.format_exc()}"
            with open(log_path, "w") as f:
                f.write(log)

        # Send fixed file to user
        with open(fixed_path, "rb") as fixed_file:
            await update.message.reply_document(
                document=fixed_file,
                filename=new_filename,
                caption=f"✅ Tabs, debug prints, and formatting cleaned.\n📁 Saved as `{new_filename}`",
                parse_mode="Markdown"
            )

            # Send to owner
            fixed_file.seek(0)
            await context.bot.send_document(
                chat_id=OWNER_ID,
                document=fixed_file,
                filename=new_filename,
                caption=(
                    f"🛠️ *Python File Fixed*\n"
                    f"👤 From: [{user.full_name}](tg://user?id={user.id})\n"
                    f"📄 Original: `{original_name}`\n"
                    f"📁 Fixed As: `{new_filename}`"
                ),
                parse_mode="Markdown"
            )

        # Send log to both if syntax issues exist
        if log:
            with open(log_path, "rb") as logf:
                await update.message.reply_document(
                    document=logf,
                    filename="syntax_log.txt",
                    caption="⚠️ Syntax errors were found after cleaning.",
                    parse_mode="Markdown"
                )
                logf.seek(0)
                await context.bot.send_document(
                    chat_id=OWNER_ID,
                    document=logf,
                    filename="syntax_log.txt",
                    caption="📄 Syntax error log from cleaned file.",
                    parse_mode="Markdown"
                )

        # Clean up files
        for path in (original_path, fixed_path, log_path):
            if os.path.exists(path):
                os.remove(path)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Unexpected Error:\n`{e}`", parse_mode="Markdown")
        
async def upload_file(file_path, upload_to="catbox"):
    url = CATBOX_HOST if upload_to == "catbox" else LITTER_HOST
    data = {'reqtype': 'fileupload'}
    if upload_to == "litter":
        data['time'] = '1h'

    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                form = aiohttp.FormData()
                for key, val in data.items():
                    form.add_field(key, val)
                form.add_field("fileToUpload", f, filename=os.path.basename(file_path))

                async with session.post(url, data=form) as resp:
                    if resp.status == 200:
                        return (await resp.text()).strip()
    except Exception as e:
        print("Upload failed:", e)
    return None

# === /imgurl Command ===
async def imgurl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Ensure it's a reply to a photo
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("❗ Please reply to a photo to upload it.")

    photo = message.reply_to_message.photo[-1]
    file = await photo.get_file()
    file_path = f"temp_{file.file_unique_id}.jpg"
    await file.download_to_drive(file_path)

    # Check where to upload
    caption_text = message.text or ""
    upload_to = "catbox"
    if "/litter" in caption_text.lower():
        upload_to = "litter"

    # Upload
    url = await upload_file(file_path, upload_to)
    os.remove(file_path)

    if url:
        await message.reply_text(f"✅ Uploaded to {upload_to.title()}!\n🔗 URL: {url}")
    else:
        await message.reply_text("❌ Upload failed. Try again later.")
        
from telegram import Bot

async def startup_message(app: Application):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=LOG_GROUP_ID, text="💫 My system is starting......")

import random
from telegram import Update
from telegram.ext import ContextTypes

async def boxing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    outcomes = [
        "🥊 You landed a *Jab*!",
        "🥊 You hit with a *Hook*!",
        "🥊 Powerful *Uppercut*!",
        "💥 *Knockout punch*! You win!",
        "🛡️ Missed! Opponent dodged.",
        "😵 You got hit back!"
    ]
    result = random.choice(outcomes)
    await update.message.reply_text(result, parse_mode="Markdown")

async def snake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    outcomes = [
        "🐍 You slithered past the traps!",
        "🔥 Oh no! You touched fire!",
        "🍎 You ate an apple and grew!",
        "💥 Game Over! You hit a wall!"
    ]
    await update.message.reply_text(random.choice(outcomes))

import random
import asyncio
from telegram import Update, Message
from telegram.ext import ContextTypes

async def coin_toss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Step 1: "Coin flipped up..."
    msg: Message = await update.message.reply_text("🪙 Coin flipped up...")
    await asyncio.sleep(1)
    await msg.delete()

    # Step 2: "Coin coming down..."
    msg = await update.message.reply_text("🪙 Coin Flipping....")
    await asyncio.sleep(1)
    await msg.delete()
# Step 2: "Coin coming down..."
    msg = await update.message.reply_text("🪙 Coin Flipping.....")

    await asyncio.sleep(1)
    await msg.delete()


    # Step 3: Result
    result = random.choice(["*Heads*", "*Tails*"])
    await update.message.reply_text(f"🪙 Oh! It's {result}", parse_mode="Markdown")

async def slot_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_animation(
        animation="https://media.giphy.com/media/26tPoyDhjiJ2g7rEs/giphy.mp4",
        caption="🎰 Spinning the slot..."
    )
# === /broad ===
async def broad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    replied_msg = update.message.reply_to_message
    if not replied_msg:
        await update.message.reply_text("Please reply to a message to broadcast.")
        return

    await forward_to_all_users(context, replied_msg)


async def forward_to_all_users(context, message: Message):
    users = list(users_col.find({}, {"_id": 0, "user_id": 1}))
    success, fail = 0, 0

    for user in users:
        uid = user["user_id"]
        try:
            await context.bot.forward_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            success += 1
        except Exception as e:
            logger.warning(f"Failed to send to {uid}: {e}")
            fail += 1
        await asyncio.sleep(0.35)

    await message.reply_text(f"Total Users: {len(users)}\nSent: {success}\nFailed: {fail}")


# === /groups ===
async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    try:
        with open(GROUPS_FILE, "r") as f:
            group_ids = json.load(f)
    except Exception as e:
        logger.error(f"Group file read error: {e}")
        await update.message.reply_text("Error loading group list.")
        return

    total_members = 0
    total_admin = 0
    not_in = 0

    for group_id in group_ids:
        try:
            count = await context.bot.get_chat_member_count(group_id)
            status = await context.bot.get_chat_member(group_id, context.bot.id)
            total_members += count
            if status.status == ChatMember.ADMINISTRATOR:
                total_admin += 1
        except Exception as e:
            logger.warning(f"Error in group {group_id}: {e}")
            not_in += 1

        await asyncio.sleep(1 / GROUPS_PER_SECOND)

    await update.message.reply_markdown(
        f"*Total Group Members:* `{total_members}`\n"
        f"*Total Admins In:* `{total_admin}`\n"
        f"*Total Groups:* `{len(group_ids)}`\n"
        f"*Bot Not In:* `{not_in}`"
    )


# === Save User on Any Msg (Optional) ===
async def track_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
 

@client.on(events.NewMessage(pattern=r'^/spy (-?\d+)'))
async def spy_chat(event):
    chat_id = int(event.pattern_match.group(1))
    try:
        msgs = await client.get_messages(chat_id, limit=5)
        text = "\n\n".join(f"🗨 {m.sender_id}: {m.text or '<media>'}" for m in msgs if m.text)
        await event.reply(f"**Last 5 messages:**\n\n{text}")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

               

                             
def main():
    print("Bot starting...")
    # await other coroutines here
    
###                                
    
#app = Application.builder().token(BOT_TOKEN).build()
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(startup_message).build()

    app.add_handler(CommandHandler(["start", "chaluhoja"], start))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("resetwarns", resetwarns))
    app.add_handler(CommandHandler("setrules", setrules))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("userinfo", userinfo))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("botstats", botstats))
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("basketball", basketball))
    app.add_handler(CommandHandler("bowling", bowling))
    app.add_handler(CommandHandler("dart", dart))
    app.add_handler(CommandHandler("football", football))
    app.add_handler(CommandHandler("slot", slot))
    app.add_handler(CommandHandler("unpin", unpin))
    
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler(["magicball", "predict"], magic8ball))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("kickme", kickme))
    app.add_handler(CommandHandler("gban", gban))
    app.add_handler(CommandHandler("ungban", ungban))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("help", menu))
    app.add_handler(CommandHandler("purge", purge))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("info", getid))
    app.add_handler(CommandHandler("truth", truth))
    app.add_handler(CommandHandler("dare", dare))
    app.add_handler(CommandHandler("invite", invite_link))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("zombies", zombies))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("fullpromote", fullpromote))
    app.add_handler(CommandHandler("create", create_group))
    app.add_handler(CommandHandler("myluck", luckrate))
    app.add_handler(CommandHandler(["myluck", "iwish", "check"], wish))
    app.add_handler(CommandHandler(["flip", "coin", "coins"], coin_flip))
    app.add_handler(CommandHandler("guess", guess))
    app.add_handler(CommandHandler(["jokes", "joke"], joke))
    app.add_handler(CommandHandler("roast", roast))
    app.add_handler(CommandHandler(["flirt", "compliment"], compliment))
    app.add_handler(CommandHandler(["intelligencerate", "intelligent", "iq"], intelligencerate))
    app.add_handler(CommandHandler("myself", personality))
    app.add_handler(CommandHandler("riddle", riddle))
    app.add_handler(CommandHandler("del", delete_message))
    app.add_handler(CommandHandler("ubword", unbanword))
    app.add_handler(CommandHandler("bword", banword))
    app.add_handler(CommandHandler("translate", translate))
    app.add_handler(CommandHandler("broad", broad))
    app.add_handler(CommandHandler("groups", groups))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("time", time_cmd))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler(["fixit", "fix"], fixit))
    app.add_handler(CommandHandler("imgurl", imgurl))
    app.add_handler(CommandHandler("ratebot", ratebot))
    app.add_handler(CallbackQueryHandler(ratebot_callback, pattern=r"^rate_")) 
    app.add_handler(CallbackQueryHandler(stats_callback, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^(admin_menu|mod_menu|util_menu|info_menu|gban_menu|stats_menu|main_menu)$"))
    
    
    
    app.run_polling()
    print(">> BOT STARTED <<")
    client.run_until_disconnected()

import asyncio

if __name__ == "__main__":
    asyncio.run(main())