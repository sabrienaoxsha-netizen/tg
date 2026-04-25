
# Multi-bot GC / Slide / Swipe tool (updated TOKENS & OWNER)
# - Spawns one Application per token and registers command handlers on each.
# - Commands available: /gcnc, /ncemo, /stopgcnc, /stopall, /delay, /status,
#   /targetslide, /stopslide, /slidespam, /stopslidespam, /swipe, /stopswipe,
#   /spamloop, /stopspam, /emospam, /stopemospam, /replytext, /stopreplytext,
#   /voice, /stopvoice, /addsudo, /delsudo, /listsudo, /myid, /ping, /help
#
# NOTE: These tokens are sensitive. If they are real, revoke/rotate them after testing.

import asyncio
import json
import os
import random
import time
import logging
import sys
from typing import Dict, Set, List
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import error as telegram_error
from telegram.error import RetryAfter, Forbidden, InvalidToken
from gtts import gTTS
import io

# ============================================
# WINDOWS ASYNCIO FIX (Required for Windows RDP)
# ============================================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
    logging.info("⚙️ Windows event loop policy set (Selector)")

# ---------------------------
# CONFIG (UPDATED)
# ---------------------------
TOKENS = [
 "8267265471:AAEBQrBQh62dj_a9DWoeWZT4tF9TBPeKbYA",
"8267265471:AAE66wHQeLMvFN5voyKOVrwbi9vFg3q2TO4",
"8451886725:AAGAjfFl7Kl_GP9xQ6W0BviVkxvGzPEHieY",
"8293884732:AAECkS-tviB7ZlM8weXV39lL7putITvngfg",
"8359614490:AAGWp5R3B2KTwSziSOv5yT5pxcaRh5FeVYg",
"8383716273:AAG7UfINwv9z3e-KQ1U8erM3HkGCM-lPocQ",
"8313155600:AAHZxlwP-xDX1xDytw1ij62N_iNyk5PQCG8",
"8267265471:AAEgEj-BlOkw5zJ1-KkyX8pZJKgLZmomqjA",
"8363738741:AAEyQOQPL-RU-k4ct6euIS0RnYZ94hpz8Ts",
"8583115776:AAHLHY094OyfBo4bPhNSHNf2RazkwJ7xVCY",
"8593326828:AAHn7AIJqXY6ANb1_89-6dPNjypxwLXPMv4",
"7991859049:AAG49TrVshj8wzQipytBDTQ7yEnphRZeZwI",
]

# Owner / initial sudo (you provided "Chat id 6416341860")
OWNER_ID = 6416341860
SUDO_FILE = "sudo.json"

# ---------------------------
# RAID TEXT FORMATTING LISTS
# ---------------------------
EMOJI_LIST = [
  "🫶","🫳","🫴","🫱","🫲","🫰","🫵","🫷","🫸","🫹",
"🪬","🪫","🪩","🪭","🪮","🪢","🪤","🪞","🪟","🪐",
"🧿","🔮","🕳️","🌀","🌫️","🌘","🌑","🌒","🌌","🌪️",
"☄️","⚡","💫","✨","🖤","💎","🔱","🧬","🧠","🕸️",
"🦂","🐺","🦇","🪶","🗝️","🛸","🎧","🕶️","🎭","🧊",
"🔥","💥","🚀","🌙","🌚","🌝","🌠","🪐","🧿","🔮",
"⚔️","🛡️","🗡️","🪓","🧨","🪦","🕯️","🧱","🪨","🪵",
"🪙","🪜","🪝","🧲","🪛","🪚","🪠","🪣","🪥","🪒",
"🪪","🪫","🪬","🪩","🪞","🪟","🪢","🪤","🪐","🪶"
]

EWW_LANGUAGES = [
    "eww",      # English
    "yuck",     # English (alt)
    "blech",    # English (alt)
    "ugh",      # English (alt)
    "छी",       # Hindi
    "ओह",       # Hindi (alt)
    "اف",       # Urdu
    "ہاں",      # Urdu (alt)
    "مقرف",      # Arabic
    "بشع",      # Arabic (alt)
    "يا إلهي",   # Arabic (alt2)
    "beurk",    # French
    "bah",      # French (alt)
    "pouah",    # French (alt2)
    "asco",     # Spanish
    "guácala",  # Spanish (alt)
    "asqueroso",# Spanish (alt2)
    "igitt",    # German
    "pfui",     # German (alt)
    "ekelhaft", # German (alt2)
    "фу",       # Russian
    "гадость",  # Russian (alt)
    "фыва",     # Russian (alt2)
    "きも",      # Japanese
    "ぎゃあ",    # Japanese (alt)
    "アー",     # Japanese (alt2)
    "으",       # Korean
    "역겨워",    # Korean (alt)
    "징그럽다",  # Korean (alt2)
    "恶心",      # Chinese
    "呸",       # Chinese (alt)
    "讨厌",     # Chinese (alt2)
    "nojo",     # Portuguese
    "eca",      # Portuguese (alt)
    "asqueroso",# Portuguese (alt2)
    "iğrenç",   # Turkish
    "tiksinti",  # Turkish (alt)
    "bölük",    # Turkish (alt2)
    "ih",       # Indonesian
    "menjijikkan",# Indonesian (alt)
    "nista",    # Indonesian (alt2)
    "ยี้",       # Thai
    "สยอม",     # Thai (alt)
    "เวียน",    # Thai (alt2)
    "bleah",    # Italian
    "bah",      # Italian (alt)
    "schifo",   # Italian (alt2)
    "fuj",      # Polish
    "obrzydliwe",# Polish (alt)
    "nuda",     # Polish (alt2)
    "pfuj",     # Czech
    "hnusný",   # Czech (alt)
    "odporný",  # Czech (alt2)
    "fuj",      # Slovak
    "odporný",  # Slovak (alt)
    "hnusný",   # Slovak (alt2)
    "pfuj",     # Hungarian
    "undorító", # Hungarian (alt)
    "szomorú",  # Hungarian (alt2)
    "scârbos",  # Romanian
    "dezgust",  # Romanian (alt)
    "murdar",   # Romanian (alt2)
    "фу",       # Bulgarian
    "гадост",   # Bulgarian (alt)
    "отвратен", # Bulgarian (alt2)
    "μπλιαχ",    # Greek
    "αποκρουστικό",# Greek (alt)
    "βρωμιά",   # Greek (alt2)
    "איכס",      # Hebrew
    "זוועה",    # Hebrew (alt)
    "שנוא",     # Hebrew (alt2)
    "چندش",     # Persian
    "نفرت",     # Persian (alt)
    "وحشتناک",   # Persian (alt2)
    "ইসস",      # Bengali
    "ঘৃণা",     # Bengali (alt)
    "বিতৃষ্ণা",  # Bengali (alt2)
    "ச்சே",      # Tamil
    "அருவருப்பு",# Tamil (alt)
    "வெள்ளை",  # Tamil (alt2)
    "ఛీ",       # Telugu
    "అసహ్యం",   # Telugu (alt)
    "దೃಷ್ಟಿ",    # Telugu (alt2)
    "छी",       # Marathi
    "घृणा",     # Marathi (alt)
    "संतापजनक", # Marathi (alt2)
    "છી",       # Gujarati
    "નફરત",     # Gujarati (alt)
    "ગમે નહીં",  # Gujarati (alt2)
    "ਛੀ",       # Punjabi
    "ਨਫ਼ਰਤ",    # Punjabi (alt)
    "ਮਤਲਬ",    # Punjabi (alt2)
    "චී",       # Sinhala
    "අකමැතිය",  # Sinhala (alt)
    "ඌනවිලාසි", # Sinhala (alt2)
    "छी",       # Nepali
    "घृणा",     # Nepali (alt)
    "विरक्त",   # Nepali (alt2)
    "usch",     # Swedish
    "äckligt",  # Swedish (alt)
    "motbjudande",# Swedish (alt2)
    "æsj",      # Norwegian
    "ekkelt",   # Norwegian (alt)
    "vemmelig", # Norwegian (alt2)
    "yök",      # Finnish
    "inhottava",# Finnish (alt)
    "ilkeä",    # Finnish (alt2)
    "adr",      # Danish
    "væmmelig", # Danish (alt)
    "fæl",      # Danish (alt2)
    "úff",      # Icelandic
    "hræðilegt",# Icelandic (alt)
    "alls",     # Icelandic (alt2)
    "öäkk",     # Estonian
    "jäme",     # Estonian (alt)
    "vastik",   # Estonian (alt2)
    "fū",       # Latvian
    "riebīgs",  # Latvian (alt)
    "negantīgs",# Latvian (alt2)
    "fu",       # Lithuanian
    "negražus", # Lithuanian (alt)
    "nuobodnus",# Lithuanian (alt2)
    "fuj",      # Croatian
    "gadan",    # Croatian (alt)
    "odvratan", # Croatian (alt2)
    "fuj",      # Serbian
    "гадно",    # Serbian (alt)
    "одвратно", # Serbian (alt2)
    "fuj",      # Slovenian
    "gnjusno",  # Slovenian (alt)
    "odpornal", # Slovenian (alt2)
    "ih",       # Malay
    "jijik",    # Malay (alt)
    "kotor",    # Malay (alt2)
    "yuck",     # Filipino
    "kabastos", # Filipino (alt)
    "marumi",   # Filipino (alt2)
    "eww",      # Vietnamese
    "ghét",     # Vietnamese (alt)
    "kinh tởm", # Vietnamese (alt2)
    "ugh",      # Afrikaans
    "walglik",  # Afrikaans (alt)
    "smerig",   # Afrikaans (alt2)
    "bah",      # Catalan
    "fastigós", # Catalan (alt)
    "repugnant",# Catalan (alt2)
]

# ---------------------------
# RAID TEXTS & EMOJIS
# ---------------------------
RAID_TEXTS = [  
 "×~🌺1🌺×~",
"~×🍥2🍥×~",
"××🐦‍🔥3🐦‍🔥××",
"~~💫4💫~~",
"~×🌙5🌙×~",
"×~🌑6🌑×~",
"~×🌌7🌌×~",
"××🖤8🖤××",
"~~💎9💎~~",
"~×🔱10🔱×~",
"×~🌀11🌀×~",
"~×🌪️12🌪️×~",
"××☄️13☄️××",
"~~🪐14🪐~~",
"~×🧿15🧿×~",
"×~🔮16🔮×~",
"~×⚔️17⚔️×~",
"××🛡️18🛡️××",
"~~💥19💥~~",
"~×🚀20🚀×~",
"×~🎧21🎧×~",
"~×🎭22🎭×~",
"××🕶️23🕶️××",
"~~🧠24🧠~~",
"~×🧬25🧬×~",
"×~🧊26🧊×~",
"~×🌫️27🌫️×~",
"××🕸️28🕸️××",
"~~🦂29🦂~~",
"~×🐺30🐺×~",
"×~🦇31🦇×~",
"~×🪶32🪶×~",
"××🗝️33🗝️××",
"~~🛸34🛸~~",
"~×🔥35🔥×~",
"×~⚡36⚡×~",
"~×💫37💫×~",
"××✨38✨××",
"~~🌙39🌙~~",
"~×🌌40🌌×~",
"×~🖤41🖤×~",
"~×💎42💎×~",
"××🔱43🔱××",
"~~🌀44🌀~~",
"~×☄️45☄️×~",
"×~🪐46🪐×~",
"~×🧿47🧿×~",
"××🔮48🔮××",
"~~⚔️49⚔️~~",
"~×🚀50🚀×~",
"×~🎧51🎧×~",
"~×🎭52🎭×~",
"××🕶️53🕶️××",
"~~🧠54🧠~~",
"~×🧬55🧬×~",
"×~🧊56🧊×~",
"~×🌫️57🌫️×~",
"××🕸️58🕸️××",
"~~🦂59🦂~~",
"~×🐺60🐺×~"
]

NCEMO_EMOJIS = [
    "🌷1🌷",
    "🌼2🌼",
    "🌻3🌻",
    "🌺4🌺",
    "🌹5🌹",
    "🏵️6🏵️",
    "🪷7🪷",
    "💮8💮",
    "🌸9🌸",
    "🌷10🌷",
    "🌼11🌼",
    "🌻12🌻",
    "🌺13🌺",
    "🌹14🌹",
    "🏵️15🏵️",
    "🪷16🪷",
    "💮17💮",
    "🌸18🌸",
    "🌷19🌷",
    "🌼20🌼",
    "🌻21🌻",
    "🌺22🌺",
    "🌹23🌹",
    "🏵️24🏵️",
    "🪷25🪷",
    "💮26💮",
    "🌸27🌸",
    "🌷28🌷",
    "🌼29🌼",
    "🌻30🌻",
    "🌺31🌺",
    "🌹32🌹",
    "🏵️33🏵️",
    "🪷34🪷",
    "💮35💮",
    "🌸36🌸",
    "🌷37🌷",
    "🌼38🌼",
    "🌻39🌻",
    "🌺40🌺",
    "🌹41🌹"
]

EMOSPAM_PATTERNS = [
    "[ any text ] 1-//--🩷🥀" * 40,
    "[ any text ] l --🦋🕷️" * 40,
    "[ any text ]k-//--💗🀄" * 40,
    "[ any text ] l - 🤍🍥" * 40
]

SPAM_PATTERNS = EMOSPAM_PATTERNS  # For spamloop

# Voice cache: {(chat_id, text): audio_bytes} - prevents regeneration
voice_cache: Dict[tuple, bytes] = {}

# Picture cache: {chat_id: file_bytes} - photo file for group picture loop
pic_cache: Dict[int, bytes] = {}

# Picture loop running flags: {chat_id: bool}
pic_running: Dict[int, bool] = {}

# Picture tasks: {chat_id: [list of asyncio.Task]} - one per bot
pic_tasks: Dict[int, list] = {}

# Spam loop pin flag: {chat_id: bool} - whether to auto-pin spam messages
pin_on_spam: Dict[int, bool] = {}

emospam_tasks: Dict[int, asyncio.Task] = {}

# Voice tasks: {chat_id: asyncio.Task}
voice_tasks: Dict[int, asyncio.Task] = {}

# Graceful shutdown event
shutdown_event: asyncio.Event | None = None


# ---------------------------
# GLOBAL STATE
# ---------------------------
# load or initialize SUDO users
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r", encoding="utf-8") as f:
            _loaded = json.load(f)
            SUDO_USERS = set(int(x) for x in _loaded)
    except Exception:
        SUDO_USERS = {OWNER_ID}
else:
    SUDO_USERS = {OWNER_ID}
with open(SUDO_FILE, "w", encoding="utf-8") as f:
    json.dump(list(SUDO_USERS), f)

def save_sudo():
    with open(SUDO_FILE, "w", encoding="utf-8") as f:
        json.dump(list(SUDO_USERS), f)

# ============================================
# CENTRALIZED PERMISSION CHECKING
# ============================================

def is_authorized(user_id: int) -> bool:
    """
    CRITICAL SECURITY: Check if user is authorized to run admin commands.
    Returns True ONLY if user is OWNER or in SUDO_USERS.
    """
    return user_id == OWNER_ID or user_id in SUDO_USERS

# Per-chat group tasks: chat_id -> dict[token_key -> task]
group_tasks: Dict[int, Dict[str, asyncio.Task]] = {}

# NC System - Concurrent All-Bots Model (NO POOLS)
nc_tasks: Dict[int, List[asyncio.Task]] = {}  # All NC tasks per chat (one per bot)
nc_counters: Dict[int, int] = {}  # Text counter per chat (unused in random mode, kept for compat)
nc_modes: Dict[int, str] = {}  # Mode (raid/emoji) per chat
nc_enabled_by: Dict[int, int] = {}  # Track who enabled NC: {chat_id: user_id}

spam_tasks: Dict[int, asyncio.Task] = {}
spam_enabled_by: Dict[int, int] = {}  # Track who enabled spam: {chat_id: user_id}
slide_targets = set()
slidespam_targets = set()

swipe_mode = {}
swipe_target_name = {}  # Swipe target name: {chat_id: target_name_string} (deprecated, kept for compat)
swipe_target_user_id: Dict[int, int] = {}  # Reply-based target: {chat_id: user_id}
swipe_base_text: Dict[int, str] = {}  # Reply-based target base text: {chat_id: base_text}
swipe_enabled_by: Dict[int, int] = {}  # Track who enabled swipe: {chat_id: user_id}

replytext_mode = {}
replytext_counter = {}
replytext_tasks: Dict[int, set] = {}  # Per-chat set of running raid tasks
replytext_enabled_by: Dict[int, int] = {}  # Track who enabled replytext: {chat_id: user_id}
userreply_targets: Dict[int, dict] = {}  # userreply target state: {chat_id: {'target_id': id, 'base': text}}
userreply_tasks: Dict[int, asyncio.Task] = {}
userreply_enabled_by: Dict[int, int] = {}

rect_groups: Set[int] = set()  # Groups where reaction mode is enabled
rect_enabled_by: Dict[int, int] = {}  # Track who enabled rect: {chat_id: user_id}
delete_targets: Dict[int, Set[int]] = {}
delete_target_names: Dict[int, Dict[int, str]] = {}
apps, bots = [], []
delay = 0.3

# Telegram API rate limit safeguards
# NC loop uses internal randomized scheduling (4-6 changes/sec per bot)
# These bounds apply to other loops (spam, voice, emospam)
MIN_DELAY = 0.05  # 50ms minimum (safe for API)
MAX_DELAY = 60.0  # 60 seconds maximum

logging.basicConfig(level=logging.INFO)

# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid not in SUDO_USERS:
            return await update.message.reply_text("❌𝐒ᴏʀʀʏ 🇧 🇧 🇾  𝐀ᴘ 𝐆ᴀʀʀᴇʙ 𝐇ᴏ.")
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid != OWNER_ID:
            return await update.message.reply_text("❌ LOFI KO ABBU BOL.")
        return await func(update, context)
    return wrapper

# ---------------------------
# NC SYSTEM - ALL BOTS CONCURRENT (NO POOLS)
# ---------------------------

async def _format_nc_title(base_text: str, mode: str) -> str:
    if mode == "emoji":
        return f"{base_text} {random.choice(NCEMO_EMOJIS)}"
    emoji = random.choice(EMOJI_LIST)
    raid = random.choice(RAID_TEXTS)
    return f"{emoji} {base_text} {raid} {emoji}"

async def _safe_set_chat_title(bot, chat_id: int, title: str) -> None:
    try:
        await bot.set_chat_title(chat_id, title)
    except RetryAfter as e:
        retry_delay = min(max(float(getattr(e, 'retry_after', 1.0)), 0.5), 10.0)
        logging.warning(
            f"NC rate limit hit for bot {getattr(bot, 'username', 'unknown')} in chat {chat_id}: sleeping {retry_delay}s"
        )
        await asyncio.sleep(retry_delay)
    except Forbidden:
        logging.warning(
            f"NC title update forbidden for bot {getattr(bot, 'username', 'unknown')} in chat {chat_id}"
        )
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logging.debug(f"NC title update error: {e}")

async def _bot_nc_loop(bot, chat_id: int, base_text: str, mode: str):
    global shutdown_event
    while not (shutdown_event and shutdown_event.is_set()):
        title = await _format_nc_title(base_text, mode)
        await _safe_set_chat_title(bot, chat_id, title)


async def spam_loop(update, text):
    """
    Continuously spam text patterns in chat.
    Respects shutdown_event and configurable delays.
    Auto-pins messages if /spamloop is running (if pin_on_spam flag set).
    """
    global shutdown_event, pin_on_spam
    chat_id = update.message.chat_id
    i = 0
    bot = update.get_bot()
    
    try:
        while not shutdown_event.is_set():
            try:
                spam_pattern = SPAM_PATTERNS[i % len(SPAM_PATTERNS)]
                spam_text = spam_pattern.replace("[ text ]", text).replace("[ Text ]", text).replace("[ any text ]", text)
                msg = await update.message.reply_text(spam_text)
                
                # Auto-pin if flag is set for this chat
                if pin_on_spam.get(chat_id, False) and msg:
                    try:
                        await bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id, disable_notification=True)
                    except Exception as pin_error:
                        # Ignore pin errors (permission, already pinned, etc.)
                        logging.debug(f"Pin message skipped in {chat_id}: {pin_error}")
                
                i += 1
                # Enforce configurable delay with safety bounds
                safe_delay = max(MIN_DELAY, min(delay, MAX_DELAY))
                await asyncio.sleep(safe_delay)
            except telegram_error.RetryAfter as e:
                # Respect Telegram's floodwait
                await asyncio.sleep(min(e.retry_after + 0.5, 5.0))
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Avoid tight loop on error
                logging.error(f"Spam loop error: {e}")
                await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass

async def voice_loop(bot, chat_id: int, text: str):
    """
    Continuously send voice messages to chat.
    
    Features:
    - Voice text is EXACTLY what user provided (NO RAID_TEXT appended)
    - Voice is generated ONCE and cached (reused, not regenerated)
    - Sends standalone messages (NOT replies to command)
    - Proper error handling with try/except
    - Respects shutdown_event
    - Respects Telegram rate limits (RetryAfter)
    """
    global shutdown_event, voice_cache
    
    cache_key = (chat_id, text)
    
    try:
        # Generate voice ONCE and cache it
        if cache_key not in voice_cache:
            try:
                tts = gTTS(text=text, lang='en')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                voice_cache[cache_key] = audio_bytes.getvalue()
                logging.info(f"Generated voice for chat {chat_id}: '{text}' ({len(voice_cache[cache_key])} bytes)")
            except Exception as e:
                logging.error(f"Failed to generate voice for chat {chat_id}: {e}")
                return
        
        # Get cached voice
        cached_voice = voice_cache[cache_key]
        
        # Send cached voice in infinite loop until stopped
        while not shutdown_event.is_set():
            try:
                # Create fresh BytesIO from cached bytes (required by Telegram API)
                voice_io = io.BytesIO(cached_voice)
                
                # Send standalone message (not reply)
                await bot.send_voice(chat_id=chat_id, voice=voice_io)
                
                # Enforce configurable delay
                safe_delay = max(MIN_DELAY, min(delay, MAX_DELAY))
                await asyncio.sleep(safe_delay)
                
            except telegram_error.RetryAfter as e:
                # Respect Telegram's floodwait
                wait_time = min(e.retry_after + 0.5, 5.0)
                logging.warning(f"Voice throttled by Telegram, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
                
            except asyncio.CancelledError:
                # Proper shutdown signal
                break
                
            except Exception as e:
                # Log error but continue (don't die silently)
                logging.error(f"Error sending voice in chat {chat_id}: {e}")
                await asyncio.sleep(0.1)
                
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.error(f"Voice loop crashed for chat {chat_id}: {e}")
    finally:
        # Cleanup: Remove from cache if this was the only task using it
        if cache_key in voice_cache:
            # Keep cache for potential reuse
            pass

# ---------------------------
# COMMANDS
# ---------------------------
@only_owner
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💗 Welcome to lofi Bot!\nUse ~help to see all commands.")

@only_sudo
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    HELP_TEXT = (
        "⸸⸸⸸  L O F I   V O I D   C O R E  ⸸⸸⸸\n"
        "⸸⸸⸸  M U L T I   B O T   S Y S T E M  ⸸⸸⸸\n"
        "⸸⸸⸸  S T A T U S  ::  O N L I N E  ⸸⸸⸸\n\n"

        "⌁⌁⌁  S Y S T E M   S T A T U S  ⌁⌁⌁\n"
        "│ start       ⟶ welcome message\n"
        "│ help        ⟶ show this menu\n"
        "│ ping        ⟶ measure response latency\n"
        "│ myid        ⟶ display your identity\n"
        "│ status      ⟶ active bots & running loops\n"
        "│ delay <sec> ⟶ set loop delay (0.05-60s)\n\n"

        "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n\n"

        "⌁⌁⌁  N A M E   C H A O S   ( N C )  ⌁⌁⌁\n"
        "│ ncloop <text>   ⟶ rapid randomized rename cycle ⚡\n"
        "│ ncemo <text>    ⟶ symbolic / emoji rename ritual\n"
        "│ stopgcnc        ⟶ terminate name chaos\n"
        "│ stopall         ⟶ force stop all active loops\n\n"

        "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n\n"

        "⌁⌁⌁  S P A M   C Y C L E   E N G I N E  ⌁⌁⌁\n"
        "│ spamloop <text> ⟶ continuous text flood\n"
        "│ emospam <text>  ⟶ symbol-based spam cycle\n"
        "│ stopspam        ⟶ halt spam operations\n"
        "│ replytext <txt> ⟶ auto-reply raid text system\n"
        "│ stopreplytext   ⟶ disable auto-reply\n\n"

        "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n\n"

        "⌁⌁⌁  G R O U P   P R O F I L E   M O D U L E  ⌁⌁⌁\n"
        "│ pic (reply)     ⟶ loop group profile picture\n"
        "│ stoppic         ⟶ terminate picture cycle\n\n"

        "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n\n"

        "⌁⌁⌁  V O I C E   F L O O D   M O D U L E  ⌁⌁⌁\n"
        "│ voice <text>    ⟶ infinite voice dispatch\n"
        "│ stopvoice       ⟶ silence voice transmission\n"
        "│ targetslide     ⟶ voice target (reply to user)\n"
        "│ stopslide       ⟶ stop targeted voice\n"
        "│ slidespam       ⟶ voice spam (reply to user)\n"
        "│ stopslidespam   ⟶ halt voice spam\n"
        "│ swipe <name>    ⟶ targeted voice domination\n"
        "│ stopswipe       ⟶ terminate swipe\n\n"

        "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n\n"

        "⌁⌁⌁  A U T O   R E A C T I O N   C O R E  ⌁⌁⌁\n"
        "│ rect            ⟶ automatic reaction ritual (🤣)\n"
        "│ stoprect        ⟶ disable reaction system\n"
        "│ deletmsg        ⟶ auto delete messages of target users\n"
        "│ stopdelete      ⟶ disable delete system\n"
        "│ listdelete      ⟶ show delete targets\n"
        "│ fulladmin       ⟶ promote all bots to admin\n"
        "│ userreply       ⟶ auto 30 replies to replied target\n"
        "│ stopuserreply   ⟶ disable user reply system\n\n"

        "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n\n"

        "⌁⌁⌁  S U D O   &   A C C E S S   C O N T R O L  ⌁⌁⌁\n"
        "│ addsudo (reply) ⟶ grant sudo privileges\n"
        "│ delsudo (reply) ⟶ revoke sudo privileges\n"
        "│ listsudo        ⟶ show all sudo users\n\n"

        "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n\n"

        "⌁⌁⌁  A C C E S S   P R O T O C O L  ⌁⌁⌁\n"
        "│ owner           ⟶ absolute control authority\n"
        "│ sudo            ⟶ delegated execution power\n"
        "│ unauthorized    ⟶ access denied\n\n"

        "⸸⸸⸸  N O T E S   F R O M   T H E   V O I D  ⸸⸸⸸\n"
        "│ this system operates without mercy\n"
        "│ loops are persistent until terminated\n"
        "│ misuse may result in forced shutdown\n"
        "│ all commands require SUDO or OWNER access\n\n"

        "⸸⸸⸸  E N D   O F   V O I D  ⸸⌁ T R A N S M I S S I O N  ⸸⸸⸸\n"
        "⸸⸸⸸  L O F I ⸸⌁  C O R E   S T A B L E  ⸸⸸⸸"
    )
    await update.message.reply_text(HELP_TEXT)

@only_sudo
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    latency = int((end_time - start_time) * 1000)
    await msg.edit_text(f"🏓 Pong! ✅ {latency} ms")

@only_sudo
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.effective_user.id}")

@only_owner
async def voice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start voice loop with text (EXACTLY as provided, no modifications).
    Does NOT reply to command, starts standalone voice sends.
    """
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: ~voice <text>")
    
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Stop any existing voice loop for this chat
    if chat_id in voice_tasks:
        try:
            voice_tasks[chat_id].cancel()
        except Exception:
            pass
    
    # Get a bot instance (use the first available bot for sending)
    if not bots:
        return await update.message.reply_text("❌ No bots available")
    
    bot = bots[0]  # Use first bot to send voice
    
    # Create new voice loop task
    task = asyncio.create_task(voice_loop(bot, chat_id, text))
    voice_tasks[chat_id] = task
    
    # Confirm to user (this is the command reply)
    await update.message.reply_text(f"🎤 Voice loop started: '{text}'")
    
    logging.info(f"Voice loop started in chat {chat_id}: '{text}'")

@only_sudo
async def stopvoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop voice loop and clean up resources."""
    chat_id = update.message.chat_id
    
    if chat_id in voice_tasks:
        try:
            voice_tasks[chat_id].cancel()
            
            # Wait briefly for task to complete
            try:
                await voice_tasks[chat_id]
            except asyncio.CancelledError:
                pass
            
            del voice_tasks[chat_id]
            await update.message.reply_text("🛑 Voice loop stopped.")
            logging.info(f"Voice loop stopped in chat {chat_id}")
        except Exception as e:
            logging.error(f"Error stopping voice loop: {e}")
            await update.message.reply_text(f"⚠️ Error stopping voice: {e}")
    else:
        await update.message.reply_text("❌ No voice loop running in this chat.")

# --- Picture Loop (Group Photo Change) ---
async def pic_loop(bot, chat_id: int, photo_bytes: bytes):
    """Download photo ONCE, then loop changing group profile picture forever."""
    global delay, pic_running
    try:
        while pic_running.get(chat_id, False) and not shutdown_event.is_set():
            try:
                # Create fresh BytesIO from cached bytes for each send
                photo_io = io.BytesIO(photo_bytes)
                await bot.set_chat_photo(chat_id=chat_id, photo=photo_io)
                safe_delay = max(MIN_DELAY, min(delay, MAX_DELAY))
                await asyncio.sleep(safe_delay)
                # Yield to prevent event loop starvation
                await asyncio.sleep(0)
            except telegram_error.RetryAfter as e:
                # Handle Telegram rate limiting
                await asyncio.sleep(min(e.retry_after + 0.1, 1.0))
            except asyncio.CancelledError:
                logging.debug(f"pic_loop cancelled for {chat_id}")
                break
            except telegram_error.Forbidden:
                # Lost permissions - exit gracefully
                logging.warning(f"Picture loop: Lost permissions in chat {chat_id}")
                break
            except Exception as e:
                if pic_running.get(chat_id, False):
                    logging.debug(f"Picture loop error in {chat_id}: {e}")
                    await asyncio.sleep(0.1)
                else:
                    break
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.debug(f"Unexpected error in pic_loop: {e}")

@only_sudo
async def pic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply to a photo with /pic to start looping group profile changes."""
    global pic_running, pic_tasks, pic_cache, bots
    
    chat_id = update.message.chat_id
    
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a photo with /pic")
    
    if not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ Replied message must contain a photo")
    
    try:
        # Stop existing pic loop if running
        if chat_id in pic_running and pic_running[chat_id]:
            pic_running[chat_id] = False
            if chat_id in pic_tasks:
                for task in pic_tasks[chat_id]:
                    try:
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                    except Exception as e:
                        logging.error(f"Error cancelling task: {e}")
                pic_tasks[chat_id] = []
            await asyncio.sleep(0.2)  # Let tasks cleanup
        
        # Download photo file bytes
        bot = context.bot
        photo = update.message.reply_to_message.photo[-1]  # Get largest
        photo_file = await bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Cache photo bytes
        pic_cache[chat_id] = photo_bytes
        
        # Enable pic running flag
        pic_running[chat_id] = True
        
        # Initialize task list for this chat
        pic_tasks[chat_id] = []
        
        # Start pic loop for ALL bots
        for bot_instance in bots:
            try:
                task = asyncio.create_task(pic_loop(bot_instance, chat_id, photo_bytes))
                pic_tasks[chat_id].append(task)
                logging.info(f"Started pic loop for bot in chat {chat_id}")
            except Exception as e:
                logging.error(f"Error starting pic loop: {e}")
        
        await update.message.reply_text(f"✅ Picture loop started for {len(pic_tasks[chat_id])} bot(s).")
        logging.info(f"Picture loop started in chat {chat_id} with {len(pic_tasks[chat_id])} bots")
        
    except Exception as e:
        logging.error(f"Error in pic_cmd: {e}")
        await update.message.reply_text(f"❌ Error starting picture loop: {e}")

@only_sudo
async def stoppic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop ALL group picture loops globally and immediately."""
    global pic_running, pic_tasks, pic_cache
    
    if not pic_tasks:
        return await update.message.reply_text("❌ No picture loops running.")
    
    try:
        # Stop ALL picture loop tasks across all chats
        stopped_count = 0
        chats_list = list(pic_tasks.keys())
        
        for chat_id in chats_list:
            try:
                # Set running flag to False FIRST (stops loop immediately)
                pic_running[chat_id] = False
                
                # Get all tasks for this chat (now a list)
                tasks = pic_tasks.get(chat_id, [])
                
                # Cancel all tasks
                for task in tasks:
                    try:
                        task.cancel()
                    except Exception as e:
                        logging.error(f"Error cancelling pic task: {e}")
                
                # Await all cancellations
                for task in tasks:
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logging.error(f"Error awaiting pic task cancellation: {e}")
                
                # Clean up state
                if chat_id in pic_tasks:
                    del pic_tasks[chat_id]
                pic_cache.pop(chat_id, None)
                if chat_id in pic_running:
                    del pic_running[chat_id]
                
                stopped_count += len(tasks)
                logging.info(f"Stopped {len(tasks)} pic loop(s) for chat {chat_id}")
            
            except Exception as e:
                logging.error(f"Error stopping pic loops for chat {chat_id}: {e}")
        
        if stopped_count > 0:
            await update.message.reply_text(f"🛑 {stopped_count} picture loop(s) stopped globally.")
        else:
            await update.message.reply_text("❌ No picture loops to stop.")
            
    except Exception as e:
        logging.error(f"Error in global stoppic: {e}")
        await update.message.reply_text(f"⚠️ Error: {e}")

# --- GC Loops (SMART STAGGERED MULTI-BOT FLOOD SYSTEM) ---
@only_sudo
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start NC with ultra-fast burst mode.
    Every bot continuously updates its title with no additional waiting.
    """
    try:
        if not is_authorized(update.effective_user.id):
            return
        if not context.args:
            return await update.message.reply_text("⚠️ Usage: ~ncloop <text>")

        base = " ".join(context.args)
        chat_id = update.message.chat_id
        user_id = update.effective_user.id

        if not bots:
            return await update.message.reply_text("❌ No bots available")

        if chat_id in nc_tasks and nc_tasks[chat_id]:
            return await update.message.reply_text("⚠️ NC loop already active in this chat.")

        nc_counters[chat_id] = 0
        nc_modes[chat_id] = "raid"
        nc_enabled_by[chat_id] = user_id
        group_tasks.setdefault(chat_id, {})
        nc_tasks[chat_id] = []

        for bot_idx, bot in enumerate(bots):
            key = getattr(bot, "token", str(id(bot)))
            if key in group_tasks[chat_id]:
                continue
            task = asyncio.create_task(_bot_nc_loop(bot, chat_id, base, "raid"))
            nc_tasks[chat_id].append(task)
            group_tasks[chat_id][key] = task

        await update.message.reply_text(
            f"✅ ULTRA FAST NC FLOOD STARTED\n"
            f"🔁 All {len(bots)} bots are changing titles continuously\n"
            f"⚡ No delay, no switching wait, maximum speed"
        )
    except Exception as e:
        logging.error(f"Error in gcnc: {e}")
        try:
            await update.message.reply_text(f"⚠️ Error starting NC: {str(e)[:50]}")
        except:
            pass

@only_sudo
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start EMOJI NC with ultra-fast continuous bot title updates.
    """
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /ncemo <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id

    if not bots:
        return await update.message.reply_text("❌ No bots available")

    if chat_id in nc_tasks and nc_tasks[chat_id]:
        return await update.message.reply_text("⚠️ NC loop already active in this chat.")

    nc_counters[chat_id] = 0
    nc_modes[chat_id] = "emoji"
    nc_enabled_by[chat_id] = update.effective_user.id
    group_tasks.setdefault(chat_id, {})
    nc_tasks[chat_id] = []

    for bot_idx, bot in enumerate(bots):
        key = getattr(bot, "token", str(id(bot)))
        if key in group_tasks[chat_id]:
            continue
        task = asyncio.create_task(_bot_nc_loop(bot, chat_id, base, "emoji"))
        nc_tasks[chat_id].append(task)
        group_tasks[chat_id][key] = task

    await update.message.reply_text(
        f"✅ ULTRA FAST EMOJI NC STARTED\n"
        f"🔁 All {len(bots)} bots are changing titles continuously\n"
        f"⚡ No delay, no switching wait, maximum speed"
    )

@only_sudo
async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop NC in current chat and cancel all worker tasks."""
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id].values():
            task.cancel()
        group_tasks[chat_id] = {}
        
        # Clean up state
        if chat_id in nc_tasks:
            del nc_tasks[chat_id]
        if chat_id in nc_counters:
            del nc_counters[chat_id]
        if chat_id in nc_modes:
            del nc_modes[chat_id]
        
        await update.message.reply_text("⏹ NC Loop stopped in this GC.")
    else:
        await update.message.reply_text("❌ No NC loop running in this GC.")

@only_sudo
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop all loops in all chats and clean up all resources."""
    try:
        await cancel_all_tasks()
        # Additional state cleanup
        nc_tasks.clear()
        nc_counters.clear()
        nc_modes.clear()
        nc_enabled_by.clear()
        replytext_mode.clear()
        replytext_counter.clear()
        replytext_enabled_by.clear()
        replytext_tasks.clear()
        userreply_targets.clear()
        userreply_enabled_by.clear()
        if userreply_tasks:
            for task in userreply_tasks.values():
                if not task.done():
                    task.cancel()
            userreply_tasks.clear()
        pic_tasks.clear()
        pic_cache.clear()
        pic_running.clear()
        pin_on_spam.clear()
        await update.message.reply_text("⏹ All loops stopped and all active tasks cleared.")
    except Exception as e:
        logging.error(f"Error in stopall: {e}")
        await update.message.reply_text(f"⚠️ Error stopping all loops: {e}")

@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    if not context.args:
        return await update.message.reply_text(f"⏱ Current delay: {delay}s (range: {MIN_DELAY}s - {MAX_DELAY}s)")
    try:
        new_delay = float(context.args[0])
        # Enforce safety bounds
        new_delay = max(MIN_DELAY, min(new_delay, MAX_DELAY))
        delay = new_delay
        await update.message.reply_text(f"✅ Delay set to {delay}s")
    except: await update.message.reply_text("⚠️ Invalid number.")

@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Active Loops:\n"
    for chat_id, tasks in group_tasks.items():
        msg += f"Chat {chat_id}: {len(tasks)} bots running\n"
    await update.message.reply_text(msg)

# --- SUDO ---
@only_owner
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    OWNER ONLY: Add a user to SUDO list.
    CRITICAL SECURITY: Only OWNER can add sudo users.
    """
    uid = None
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            uid = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("⚠️ Usage: ~addsudo <user_id> or reply to a message")
    else:
        return await update.message.reply_text("⚠️ Usage: ~addsudo <user_id> or reply to a message")
    
    # Prevent adding OWNER to SUDO (OWNER is already maximum privilege)
    if uid == OWNER_ID:
        return await update.message.reply_text("❌ OWNER cannot be added to SUDO (already maximum privilege).")
    
    if uid in SUDO_USERS:
        return await update.message.reply_text(f"⚠️ {uid} is already a sudo user.")
    
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ {uid} added as SUDO user by OWNER.")

@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    OWNER ONLY: Remove a user from SUDO list.
    CRITICAL SECURITY: Only OWNER can remove sudo users.
    """
    uid = None
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            uid = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("⚠️ Usage: ~delsudo <user_id> or reply to a message")
    else:
        return await update.message.reply_text("⚠️ Usage: ~delsudo <user_id> or reply to a message")
    
    # Prevent removing OWNER (impossible, since OWNER not in SUDO)
    if uid == OWNER_ID:
        return await update.message.reply_text("❌ Cannot modify OWNER (OWNER is defined in script only).")
    
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"🗑 {uid} removed from SUDO by OWNER.")
    else:
        await update.message.reply_text(f"❌ {uid} is not a SUDO user.")

@only_sudo
async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show current OWNER and SUDO list.
    CRITICAL SECURITY: OWNER is defined in script only and cannot be changed.
    """
    owner_name = f"<code>{OWNER_ID}</code>"
    
    sudo_list = []
    if SUDO_USERS:
        for uid in sorted(SUDO_USERS):
            sudo_list.append(f"<code>{uid}</code>")
        sudo_users_text = "\n".join(sudo_list)
    else:
        sudo_users_text = "None (only OWNER can run admin commands)"
    
    message = (
        "🔐 AUTHORIZATION HIERARCHY:\n\n"
        f"👑 OWNER (SCRIPT-ONLY):\n{owner_name}\n\n"
        "⚡ SUDO USERS (changeable by OWNER only):\n"
        f"{sudo_users_text}"
    )
    
    await update.message.reply_text(message, parse_mode="HTML")

# --- Slide / Spam / Swipe ---
@only_sudo
async def targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slide_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🎯 Target slide added.")

@only_sudo
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        slide_targets.discard(uid)
        await update.message.reply_text("🛑 Target slide stopped.")

@only_sudo
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slidespam_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("💥 Slide spam started.")

@only_sudo
async def stopslidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slidespam_targets.discard(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🛑 Slide spam stopped.")

@only_sudo
async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable swipe mode: Must be used as a REPLY to a user's message.
    Extracts target user_id and base text, stores persistently.
    """
    # CRITICAL SECURITY: Check authorization IMMEDIATELY
    if not is_authorized(update.effective_user.id):
        return  # Silently ignore unauthorized requests
    
    # Must be a reply to a message
    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "⚠️ ~swipe must be used as a REPLY to a message.\n"
            "Reply to a user's message with: ~swipe <base_text>"
        )
    
    # Extract target user_id from replied message
    target_user_id = update.message.reply_to_message.from_user.id
    target_user_name = update.message.reply_to_message.from_user.first_name or "User"
    
    # Get base text from command args
    if not context.args:
        return await update.message.reply_text(
            "⚠️ Usage: Reply to a message with: ~swipe <base_text>"
        )
    base_text = " ".join(context.args)
    
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    
    # Store target user_id and base text for this chat
    swipe_target_user_id[chat_id] = target_user_id
    swipe_base_text[chat_id] = base_text
    swipe_enabled_by[chat_id] = user_id  # SECURITY: Track who enabled this
    
    await update.message.reply_text(
        f"⚡ Swipe mode ACTIVE\n"
        f"Target: {target_user_name} (ID: {target_user_id})\n"
        f"Base text: '{base_text}'\n"
        f"Will reply to every message from this user.\n"
        f"Use ~stopswipe to disable."
    )

@only_sudo
async def stopswipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    STRICT ISOLATION: Stops ONLY swipe mode.
    Does NOT affect replytext or any other features.
    """
    chat_id = update.message.chat_id
    if chat_id in swipe_target_user_id:
        # Remove both target user_id and base text atomically
        swipe_target_user_id.pop(chat_id, None)
        swipe_base_text.pop(chat_id, None)
        
        # Confirmation: swipe is stopped
        await update.message.reply_text("🛑 Swipe mode stopped.")
    else:
        # Swipe was not active
        await update.message.reply_text("❌ Swipe mode not active.")

# --- Nonstop Spam ---
@only_sudo
async def spamloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pin_on_spam
    # CRITICAL SECURITY: Check authorization IMMEDIATELY
    if not is_authorized(update.effective_user.id):
        return  # Silently ignore unauthorized requests
    
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /spamloop <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    
    if chat_id in spam_tasks:
        spam_tasks[chat_id].cancel()
    
    # Set flag to enable auto-pinning in spam_loop
    pin_on_spam[chat_id] = True
    spam_enabled_by[chat_id] = user_id  # SECURITY: Track who enabled this
    
    task = asyncio.create_task(spam_loop(update, text))
    spam_tasks[chat_id] = task
    await update.message.reply_text("🔄 Spam loop started - messages will be auto-pinned!")

@only_sudo
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pin_on_spam
    chat_id = update.message.chat_id
    # Clear pin flag for this chat
    pin_on_spam.pop(chat_id, None)
    if chat_id in spam_tasks:
        spam_tasks[chat_id].cancel()
        spam_tasks.pop(chat_id)
        await update.message.reply_text("🛑 Spam stopped.")
    else:
        await update.message.reply_text("❌ No spam running.")

async def emospam_loop(update, text):
    """Emoji spam loop with proper shutdown handling."""
    global shutdown_event
    chat_id = update.message.chat_id
    i = 0
    try:
        while not shutdown_event.is_set():
            try:
                pattern = EMOSPAM_PATTERNS[i % len(EMOSPAM_PATTERNS)]
                emo_text = pattern.replace("[ any text ]", text).replace("[ text ]", text).replace("[ Text ]", text)
                await update.message.reply_text(emo_text)
                i += 1
                # Enforce configurable delay
                safe_delay = max(MIN_DELAY, min(delay, MAX_DELAY))
                await asyncio.sleep(safe_delay)
            except telegram_error.RetryAfter as e:
                await asyncio.sleep(min(e.retry_after + 0.5, 5.0))
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass

@only_sudo
async def emospam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /emospam <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in emospam_tasks:
        emospam_tasks[chat_id].cancel()
    task = asyncio.create_task(emospam_loop(update, text))
    emospam_tasks[chat_id] = task
    await update.message.reply_text("🎯 Emoji spam started!")

@only_sudo
async def stopemospam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in emospam_tasks:
        emospam_tasks[chat_id].cancel()
        emospam_tasks.pop(chat_id)
        await update.message.reply_text("🛑 Emoji spam stopped.")
    else:
        await update.message.reply_text("❌ No emoji spam running.")

@only_sudo
async def replytext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # CRITICAL SECURITY: Check authorization IMMEDIATELY
    if not is_authorized(update.effective_user.id):
        return  # Silently ignore unauthorized requests
    
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: ~replytext <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    
    replytext_mode[chat_id] = base
    replytext_enabled_by[chat_id] = user_id  # SECURITY: Track who enabled this
    # No longer using counter (moved to FULL RAID mode)
    replytext_counter[chat_id] = 0
    await update.message.reply_text(
        f"✅ FULL RAID MODE ENABLED\n"
        f"Base text: '{base}'\n\n"
        f"For EACH incoming message:\n"
        f"• Send FULL RAID_TEXTS list × 2 rounds\n"
        f"• ≈ 70-80 replies per message\n"
        f"• Use ~stopreplytext to disable"
    )

@only_sudo
async def stopreplytext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in replytext_mode:
        # INSTANT HARD STOP: Disable mode and cancel all running tasks
        replytext_mode.pop(chat_id, None)
        replytext_counter.pop(chat_id, None)
        replytext_enabled_by.pop(chat_id, None)
        
        # Cancel all running raid tasks for this chat
        if chat_id in replytext_tasks:
            tasks = replytext_tasks[chat_id]
            for task in tasks:
                if not task.done():
                    task.cancel()
            # Wait briefly for cancellation to propagate
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            replytext_tasks[chat_id].clear()
        
        await update.message.reply_text("🛑 Reply text mode stopped (hard stop).")
    else:
        await update.message.reply_text("❌ Reply text mode not active.")

# ============================================
# REPLY TEXT RAID EXECUTOR (task-based)
# ============================================
async def _execute_replytext_raid(chat_id: int, base_text: str, update: Update):
    """
    Execute replytext raid as a cancellable task.
    Checks replytext_mode before each send for instant stop capability.
    """
    try:
        for round_num in range(2):
            # Cancellation-aware check: stop if mode disabled
            if not replytext_mode.get(chat_id):
                return
            
            for raid_text in RAID_TEXTS:
                # Cancellation-aware check before each send
                if not replytext_mode.get(chat_id):
                    return
                
                try:
                    text = f"{base_text} {raid_text}"
                    await update.message.reply_text(text)
                    # Yield to prevent event-loop freeze
                    await asyncio.sleep(0)
                except telegram_error.RetryAfter as e:
                    # Rate limited: skip and continue to next
                    logging.debug(f"Reply raid rate limited (round {round_num+1}): {e}")
                    continue
                except telegram_error.Forbidden:
                    # Lost permissions: stop raid immediately
                    logging.debug(f"Reply raid forbidden in {chat_id}: stopping")
                    return
                except asyncio.CancelledError:
                    # Task was cancelled - exit cleanly
                    logging.debug(f"Reply raid cancelled in {chat_id}")
                    return
                except Exception as e:
                    # Other errors: continue to next reply
                    logging.debug(f"Reply raid send error: {e}")
                    continue
    except asyncio.CancelledError:
        logging.debug(f"Reply raid task cancelled for {chat_id}")
        return
    except Exception as raid_error:
        logging.debug(f"Reply raid error in {chat_id}: {raid_error}")
    finally:
        # Clean up task tracking when done
        if chat_id in replytext_tasks:
            replytext_tasks[chat_id].discard(asyncio.current_task())


# --- Reaction Mode (😂 on OWNER/SUDO messages) ---
@only_sudo
async def rect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable reaction mode: ALL bots react 🤣 to OWNER/SUDO messages."""
    # CRITICAL SECURITY: Check authorization IMMEDIATELY
    if not is_authorized(update.effective_user.id):
        return  # Silently ignore unauthorized requests
    
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    global rect_groups
    
    if chat_id in rect_groups:
        return await update.message.reply_text("✅ Reaction mode already active")
    
    rect_groups.add(chat_id)
    rect_enabled_by[chat_id] = user_id  # SECURITY: Track who enabled this
    await update.message.reply_text("✅ Reaction mode enabled. I'll react 🤣 to OWNER/SUDO messages.")

@only_sudo
async def stoprect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disable reaction mode."""
    chat_id = update.message.chat_id
    rect_groups.discard(chat_id)
    rect_enabled_by.pop(chat_id, None)
    await update.message.reply_text("✅ Reaction mode stopped.")

@only_sudo
async def deletmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: ~deletmsg @username1 @username2 ...")

    chat_id = update.message.chat_id
    delete_targets.setdefault(chat_id, set())
    delete_target_names.setdefault(chat_id, {})

    added = []
    failed = []

    for arg in context.args:
        username = arg.lstrip("@")
        if not username:
            continue

        user_obj = None
        try:
            user_obj = await context.bot.get_chat(f"@{username}")
        except Exception:
            # fallback to text_mention entity if one exists for this arg
            if update.message.entities:
                for ent in update.message.entities:
                    if ent.type == "text_mention":
                        text = update.message.text[ent.offset:ent.offset + ent.length]
                        if text == arg and ent.user:
                            user_obj = ent.user
                            break

        if user_obj and user_obj.id:
            delete_targets[chat_id].add(user_obj.id)
            delete_target_names[chat_id][user_obj.id] = user_obj.username or user_obj.full_name or str(user_obj.id)
            added.append(f"{user_obj.username or user_obj.full_name or user_obj.id}")
        else:
            failed.append(arg)

    result_parts = []
    if added:
        result_parts.append(f"✅ Added to delete list: {', '.join(added)}")
    if failed:
        result_parts.append(f"⚠️ Failed to resolve: {', '.join(failed)}")

    await update.message.reply_text("\n".join(result_parts))

@only_sudo
async def stopdelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in delete_targets:
        delete_targets.pop(chat_id, None)
        delete_target_names.pop(chat_id, None)
        await update.message.reply_text("✅ Delete list cleared for this chat.")
    else:
        await update.message.reply_text("❌ No delete targets configured for this chat.")

@only_sudo
async def listdelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in delete_targets or not delete_targets[chat_id]:
        return await update.message.reply_text("⚠️ No delete targets configured for this chat.")

    lines = ["🗑️ Delete targets for this chat:"]
    for uid in sorted(delete_targets[chat_id]):
        display_name = delete_target_names.get(chat_id, {}).get(uid, None)
        if display_name:
            lines.append(f"• {display_name} (<code>{uid}</code>)")
        else:
            lines.append(f"• <code>{uid}</code>")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

@only_sudo
async def fulladmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Promote all bots present in the group to admin with full permissions.
    """
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("❌ This command only works in groups.")
    if not is_authorized(update.effective_user.id):
        return
    executor = None
    for bot in bots:
        try:
            me = await bot.get_me()
            member = await bot.get_chat_member(chat.id, me.id)
            if member.status in ["administrator", "creator"] and member.can_promote_members:
                executor = bot
                break
        except Exception:
            continue
    if not executor:
        return await update.message.reply_text("❌ No bot with promotion permission is available.")
    promoted = []
    failed = []
    for bot in bots:
        try:
            me = await bot.get_me()
            member = await executor.get_chat_member(chat.id, me.id)
            if member.status in ["administrator", "creator"]:
                promoted.append(me.username or str(me.id))
                continue
            await executor.promote_chat_member(
                chat.id,
                me.id,
                can_change_info=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True,
                can_manage_video_chats=True,
                can_manage_chat=True,
            )
            promoted.append(me.username or str(me.id))
        except Exception:
            failed.append(getattr(bot, 'username', str(getattr(bot, 'id', 'unknown'))))
    msg = []
    if promoted:
        msg.append(f"✅ Promoted: {', '.join(promoted)}")
    if failed:
        msg.append(f"❌ Failed: {', '.join(failed)}")
    if not msg:
        msg.append("No bots found in group or insufficient permissions.")
    await update.message.reply_text("\n".join(msg))

@only_sudo
async def userreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Enable auto-reply for the replied user.
    """
    if not is_authorized(update.effective_user.id):
        return
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("⚠️ Usage: ~userreply <text> (reply to a user message)")
    target_user = update.message.reply_to_message.from_user
    if not target_user:
        return await update.message.reply_text("❌ Could not determine target user.")
    chat_id = update.message.chat_id
    userreply_targets[chat_id] = {
        "target_id": target_user.id,
        "base": " ".join(context.args),
    }
    userreply_enabled_by[chat_id] = update.effective_user.id
    await update.message.reply_text(f"✅ User reply enabled for {target_user.first_name}.")

@only_sudo
async def stopuserreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in userreply_targets:
        userreply_targets.pop(chat_id, None)
        userreply_enabled_by.pop(chat_id, None)
        if chat_id in userreply_tasks:
            task = userreply_tasks.pop(chat_id)
            if not task.done():
                task.cancel()
        await update.message.reply_text("🛑 User reply disabled.")
    else:
        await update.message.reply_text("❌ User reply not active.")

async def send_userreply_loop(message, chat_id: int, base_text: str):
    try:
        for i in range(30):
            if chat_id not in userreply_targets:
                return
            raid_text = random.choice(RAID_TEXTS)
            emoji = random.choice(EMOJI_LIST)
            reply_text = f"{base_text} {raid_text} {emoji}"
            try:
                await message.reply_text(reply_text)
            except Exception:
                pass
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        return
    finally:
        if chat_id in userreply_tasks and userreply_tasks[chat_id] is asyncio.current_task():
            userreply_tasks.pop(chat_id, None)

# --- Auto Replies ---
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Deprecated: Auto-reply handler kept for backward compatibility.
    Actual replytext, swipe, and reaction logic now handled in reaction_handler
    which uses filters.ALL and processes all messages correctly.
    """
    # This handler is now mostly unused as reaction_handler (filters.ALL) 
    # handles all the reply logic. Kept for now to avoid breaking changes.
    pass

# ---------------------------
# ASYNC TASK CLEANUP & SHUTDOWN
# ---------------------------
async def cancel_all_tasks():
    """Cancel all background tasks gracefully."""
    # Cancel group tasks
    for chat_id in list(group_tasks.keys()):
        for task in group_tasks[chat_id].values():
            if not task.done():
                task.cancel()
        group_tasks[chat_id] = {}
    
    # Clean up NC resources
    nc_tasks.clear()
    nc_counters.clear()
    nc_modes.clear()
    nc_enabled_by.clear()
    
    # Cancel spam tasks
    for chat_id in list(spam_tasks.keys()):
        if not spam_tasks[chat_id].done():
            spam_tasks[chat_id].cancel()
    spam_tasks.clear()
    
    # Cancel emoji spam tasks
    for chat_id in list(emospam_tasks.keys()):
        if not emospam_tasks[chat_id].done():
            emospam_tasks[chat_id].cancel()
    emospam_tasks.clear()
    
    # Cancel replytext tasks
    for chat_id in list(replytext_tasks.keys()):
        for task in list(replytext_tasks[chat_id]):
            if not task.done():
                task.cancel()
        replytext_tasks[chat_id].clear()
    replytext_tasks.clear()
    replytext_mode.clear()
    replytext_counter.clear()
    replytext_enabled_by.clear()
    
    # Cancel userreply tasks
    for chat_id in list(userreply_tasks.keys()):
        if not userreply_tasks[chat_id].done():
            userreply_tasks[chat_id].cancel()
    userreply_tasks.clear()
    userreply_targets.clear()
    userreply_enabled_by.clear()
    
    # Cancel picture tasks
    for chat_id in list(pic_tasks.keys()):
        for task in pic_tasks[chat_id]:
            if not task.done():
                task.cancel()
    pic_tasks.clear()
    pic_cache.clear()
    pic_running.clear()

    # Cancel voice tasks
    for chat_id in list(voice_tasks.keys()):
        if not voice_tasks[chat_id].done():
            voice_tasks[chat_id].cancel()
    voice_tasks.clear()
    
    # Clear voice cache (memory cleanup)
    voice_cache.clear()
    
    # Clear spam pin state
    pin_on_spam.clear()
    
    # Give tasks a moment to clean up
    await asyncio.sleep(0.1)

async def graceful_shutdown(apps_list):
    """
    Properly shutdown all bot applications.
    Ensures no tasks are accessing closed event loops.
    """
    global shutdown_event
    logging.info("🛑 Graceful shutdown initiated...")
    
    # Signal all tasks to stop
    shutdown_event.set()
    
    # Cancel all background tasks
    await cancel_all_tasks()
    
    # Stop and shutdown all applications
    for app in apps_list:
        try:
            await app.stop()
            await app.shutdown()
        except Exception as e:
            logging.warning(f"Error stopping app: {e}")
    
    logging.info("✅ All bots stopped cleanly.")

# ---------------------------
# BUILD APP & RUN
# ---------------------------
async def universal_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Universal handler for all "~" commands.
    Extracts command and arguments, then routes to appropriate handler.
    """
    try:
        text = update.message.text
        if not text.startswith("~"):
            return
        
        # Remove "~" and split into command + args
        parts = text[1:].split(None, 1)
        if not parts:
            return
        
        command = parts[0].lower()
        args_str = parts[1] if len(parts) > 1 else ""
        
        # Convert args_str to context.args format
        context.args = args_str.split() if args_str else []
        
        # Route to appropriate handler
        handlers = {
            "start": start_cmd,
            "help": help_cmd,
            "ping": ping_cmd,
            "myid": myid,
            "voice": voice_cmd,
            "stopvoice": stopvoice,
            "pic": pic_cmd,
            "stoppic": stoppic,
            "ncloop": gcnc,
            "ncemo": ncemo,
            "stopgcnc": stopgcnc,
            "stopall": stopall,
            "delay": delay_cmd,
            "status": status_cmd,
            "addsudo": addsudo,
            "delsudo": delsudo,
            "listsudo": listsudo,
            "targetslide": targetslide,
            "stopslide": stopslide,
            "slidespam": slidespam,
            "stopslidespam": stopslidespam,
            "swipe": swipe,
            "stopswipe": stopswipe,
            "spamloop": spamloop,
            "stopspam": stopspam,
            "emospam": emospam,
            "stopemospam": stopemospam,
            "replytext": replytext,
            "stopreplytext": stopreplytext,
            "rect": rect,
            "stoprect": stoprect,
            "deletmsg": deletmsg,
            "stopdelete": stopdelete,
            "listdelete": listdelete,
            "fulladmin": fulladmin,
            "userreply": userreply,
            "stopuserreply": stopuserreply,
        }
        
        if command in handlers:
            await handlers[command](update, context)
        
    except Exception as e:
        logging.error(f"Error in universal_command_handler: {e}")
        try:
            await update.message.reply_text(f"⚠️ Command error: {e}")
        except:
            pass

async def reaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Process ALL messages for reaction, userreply, replytext and swipe features.
    """
    if not update.effective_message or not update.effective_user:
        return
    if update.effective_user.is_bot:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    message = update.effective_message
    message_text = message.text or ""
    is_command = message_text.startswith("~")

    # --- RECT: Auto Reaction System ---
    if chat_id in rect_groups and update.effective_chat.type in ["group", "supergroup"]:
        enabler_id = rect_enabled_by.get(chat_id)
        if enabler_id is None or is_authorized(enabler_id):
            if user_id == OWNER_ID or user_id in SUDO_USERS:
                # Use direct message reaction support if available.
                for bot_instance in bots:
                    try:
                        await bot_instance.set_message_reaction(
                            chat_id=chat_id,
                            message_id=message.message_id,
                            reaction="🤣",
                        )
                    except telegram_error.RetryAfter as e:
                        await asyncio.sleep(min(getattr(e, 'retry_after', 0.5) + 0.1, 5.0))
                    except Exception:
                        continue
        else:
            rect_groups.discard(chat_id)
            rect_enabled_by.pop(chat_id, None)

    # --- DELETE TARGET SYSTEM ---
    if chat_id in delete_targets:
        target_ids = delete_targets.get(chat_id, set())
        sender_id = message.from_user.id if message.from_user else None
        should_delete = False

        if sender_id in target_ids:
            should_delete = True
        elif message.forward_from and message.forward_from.id in target_ids:
            should_delete = True
        elif message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id in target_ids:
            should_delete = True
        elif message.entities:
            for ent in message.entities:
                if ent.type == "text_mention" and ent.user and ent.user.id in target_ids:
                    should_delete = True
                    break
                if ent.type == "mention" and message.text:
                    mention_text = message.text[ent.offset:ent.offset + ent.length]
                    if mention_text.startswith("@"):
                        mention_name = mention_text[1:]
                        for uid, saved_name in delete_target_names.get(chat_id, {}).items():
                            if saved_name and saved_name.lstrip("@").lower() == mention_name.lower():
                                should_delete = True
                                break
                        if should_delete:
                            break

        if should_delete:
            try:
                await message.delete()
            except telegram_error.Forbidden:
                pass
            except Exception:
                pass
            return

    # --- USER REPLY TRIGGER ---
    if chat_id in userreply_targets:
        enabler_id = userreply_enabled_by.get(chat_id)
        if enabler_id and not is_authorized(enabler_id):
            userreply_targets.pop(chat_id, None)
            userreply_enabled_by.pop(chat_id, None)
        else:
            target_info = userreply_targets[chat_id]
            if user_id == target_info.get("target_id"):
                existing = userreply_tasks.get(chat_id)
                if existing and not existing.done():
                    return
                userreply_tasks[chat_id] = asyncio.create_task(
                    send_userreply_loop(message, chat_id, target_info.get("base", ""))
                )

    if is_command:
        return

    # --- REPLY TEXT MODE ---
    if chat_id in replytext_mode:
        try:
            if chat_id in replytext_enabled_by and not is_authorized(replytext_enabled_by[chat_id]):
                replytext_mode.pop(chat_id, None)
                replytext_counter.pop(chat_id, None)
                if chat_id in replytext_tasks:
                    tasks = replytext_tasks[chat_id]
                    for task in list(tasks):
                        if not task.done():
                            task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks.clear()
                return

            if chat_id not in replytext_tasks:
                replytext_tasks[chat_id] = set()
            task = asyncio.create_task(_execute_replytext_raid(chat_id, replytext_mode[chat_id], update))
            replytext_tasks[chat_id].add(task)
        except Exception as e:
            logging.debug(f"Replytext handling error in {chat_id}: {e}")

    # ============================================
    # SWIPE MODE (reply-based target user_id match)
    # STRICTLY ISOLATED - NO FALLTHROUGH TO OTHER MODES
    # ============================================
    if chat_id in swipe_target_user_id:
        try:
            if chat_id in swipe_enabled_by and not is_authorized(swipe_enabled_by[chat_id]):
                swipe_target_user_id.pop(chat_id, None)
                swipe_base_text.pop(chat_id, None)
                swipe_enabled_by.pop(chat_id, None)
                return

            target_user_id = swipe_target_user_id.get(chat_id)
            if target_user_id is None:
                return

            if user_id == target_user_id:
                try:
                    base_text = swipe_base_text.get(chat_id, "")
                    raid_text = random.choice(RAID_TEXTS)
                    reply_text = f"{base_text} {raid_text}"
                    await message.reply_text(reply_text)
                    logging.debug(f"Swipe triggered for target user {target_user_id}")
                except Exception as swipe_error:
                    logging.debug(f"Swipe reply error in {chat_id}: {swipe_error}")
        except Exception as swipe_process_error:
            logging.debug(f"Swipe processing error: {swipe_process_error}")
        return

    await asyncio.sleep(0)

async def bot_watchdog():
    """
    Lightweight watchdog that monitors bot health periodically.
    Logs critical info but does NOT spam.
    Runs in background and does not crash the bot.
    """
    global shutdown_event
    last_log_time = {}
    min_log_interval = 60  # Only log once per minute per event
    
    try:
        while not shutdown_event.is_set():
            try:
                current_time = time.time()
                
                # Check NC tasks
                if nc_tasks:
                    total_nc = sum(len(tasks) for tasks in nc_tasks.values())
                    event_key = f"nc_tasks_{total_nc}"
                    if event_key not in last_log_time or current_time - last_log_time[event_key] > min_log_interval:
                        logging.info(f"📊 NC tasks running: {total_nc}")
                        last_log_time[event_key] = current_time
                
                # Check spam tasks
                if spam_tasks:
                    event_key = "spam_tasks"
                    if event_key not in last_log_time or current_time - last_log_time[event_key] > min_log_interval:
                        logging.info(f"📊 Spam tasks running: {len(spam_tasks)}")
                        last_log_time[event_key] = current_time
                
                # Yield to prevent event loop starvation
                await asyncio.sleep(0)
                
                # Check every 10 seconds
                await asyncio.sleep(10)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.debug(f"Watchdog check error (non-critical): {e}")
                await asyncio.sleep(0)
    
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.debug(f"Watchdog error (non-critical): {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler - prevents any exception from crashing the bot."""
    try:
        logging.error(f"Update {update} caused error: {context.error}")
    except Exception as e:
        logging.error(f"Error in error handler itself: {e}")


def build_app(token):
    try:
        app = Application.builder().token(token).build()
    except InvalidToken as e:
        logging.error(f"Invalid token skipped during app build: {token} -> {e}")
        return None
    except Exception as e:
        logging.error(f"Failed building app for token {token}: {e}")
        return None
    
    # Add global error handler to catch any unhandled exceptions
    app.add_error_handler(error_handler)
    
    # CRITICAL: Handler groups ensure proper execution order
    # Group 0 (HIGHEST PRIORITY): Reaction handler MUST run first for rect feature
    app.add_handler(MessageHandler(filters.ALL, reaction_handler), group=0)
    
    # Group 1: Command handler for ~ commands
    app.add_handler(MessageHandler(filters.Regex(r"^~\w"), universal_command_handler), group=1)
    
    # Group 2: Auto replies for non-command messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.Regex(r"^~\w"), auto_replies), group=2)
    
    return app

async def cleanup_voice_cache():
    """Clean up voice cache on startup (memory optimization)."""
    global voice_cache
    try:
        voice_cache.clear()
        logging.info("Voice cache cleared")
    except Exception as e:
        logging.warning(f"Error clearing voice cache: {e}")

async def run_all_bots():
    """
    Main bot runner with proper lifecycle management and hardening.
    - Initializes shutdown_event
    - Starts all bot applications
    - Runs watchdog for health monitoring
    - Handles graceful shutdown on signal
    - Prevents crashes from propagating
    """
    global apps, bots, shutdown_event
    
    # Initialize shutdown event
    shutdown_event = asyncio.Event()
    
    # Clean up voice cache on startup (memory optimization)
    await cleanup_voice_cache()
    
    # Deduplicate tokens while preserving order
    seen = set()
    unique_tokens = []
    for t in TOKENS:
        if t and t not in seen:
            seen.add(t)
            unique_tokens.append(t)

    # Build all applications and skip tokens that fail validation
    build_failures = 0
    invalid_tokens = []
    build_results = []
    for token in unique_tokens:
        app = build_app(token)
        if app is None:
            build_failures += 1
            invalid_tokens.append(token)
            continue
        build_results.append((token, app))

    if invalid_tokens:
        logging.warning(f"⚠️ {len(invalid_tokens)} invalid or failed tokens skipped.")
        for invalid in invalid_tokens:
            logging.warning(f"Skipped invalid token: {invalid}")

    if build_failures > 0:
        logging.warning(f"⚠️ {build_failures} app build failures - continuing with {len(build_results)} valid app definitions")

    # Initialize and start all applications
    startup_failures = 0
    active_apps = []
    active_bots = []

    for token, app in build_results:
        try:
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            active_apps.append(app)
            active_bots.append(app.bot)
            logging.info(f"✅ Bot started successfully for token: {token}")
            await asyncio.sleep(0.5)  # Stagger startup to avoid conflicts
        except InvalidToken as e:
            logging.error(f"Invalid token skipped during startup: {token} -> {e}")
            startup_failures += 1
        except telegram_error.Unauthorized as e:
            logging.error(f"Unauthorized token skipped during startup: {token} -> {e}")
            startup_failures += 1
        except Exception as e:
            logging.error(f"Failed starting app for token {token}: {e}")
            startup_failures += 1

    # Replace apps and bots lists with only successfully started instances
    apps = active_apps
    bots = active_bots

    if not apps:
        logging.error("❌ No bots could be started!")
        return

    logging.info(f"🚀 lofi Bot is running ({len(apps)} bots active, {startup_failures} startup failures).")
    
    # Start watchdog task in background
    watchdog_task = asyncio.create_task(bot_watchdog())
    
    try:
        # Keep the bot running until shutdown signal
        await shutdown_event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        # Cancel watchdog
        try:
            watchdog_task.cancel()
            await watchdog_task
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        
        # Ensure graceful shutdown happens
        await graceful_shutdown(apps)

async def main():
    """
    Main entry point using asyncio.run().
    Properly handles KeyboardInterrupt and cleanup.
    Global exception safety wrapper.
    """
    try:
        await run_all_bots()
    except KeyboardInterrupt:
        logging.info("\n🛑 Keyboard interrupt received - shutting down cleanly...")
    except Exception as e:
        logging.error(f"🚨 Fatal error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Use asyncio.run() for proper event loop lifecycle management
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\n🛑 Bot stopped by user")
    except Exception as e:
        logging.error(f"🚨 Fatal error: {e}", exc_info=True)
    finally:
        logging.info("✅ Bot shutdown complete")