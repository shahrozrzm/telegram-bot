# فایل main.py

import json
import random
import os
import logging
import requests
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from deep_translator import GoogleTranslator

TOKEN = "7667664423:AAE0wi3t8RC-jkIFPVNwJ0cuTzg427Uzkdk"
ADMIN_USERNAME = "@shahrozrzm"
WEATHER_API_KEY = "KDXAHPA3N49E28VLU3AQ4MWYH"

logging.basicConfig(level=logging.INFO)
users_file = "users.json"
config_file = "configs.json"

# ---------------------- Utility Functions ---------------------- #
def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_user(user_id):
    users = load_json(users_file)
    users[str(user_id)] = True
    save_json(users_file, users)

def get_users():
    return list(load_json(users_file).keys())

# ---------------------- Static Data ---------------------- #
jokes = [
    "یه روز یه مردی می‌ره دکتر، دکتر می‌گه چی شده؟ می‌گه هیچی فقط اومدم ببینم دکتر خودت خوبی؟ 😄",
    "معلم: چرا دیر اومدی؟ دانش‌آموز: چون زود نیومدم! 😂",
    "می‌دونی چرا ماهی ورزش نمی‌کنه؟ چون همیشه فیت هست! 🐟",
    "داداشم می‌گه روزی ۵ تا موز بخوریم قوی می‌شیم، الآن موندم موزم یا من! 🍌",
    "یارو تو تاکسی خوابش برد، راننده نگه داشت گفت بیدار شو رسیدیم، گفت کاش خونه بود! 🚕",
    "دختره بهم گفت بی تو می‌میرم، الآن یه ساله جوابشو ندادم، هنوز زندست! 🤨",
    "یه روز یه مورچه افتاد تو لیوان چای گفت آخ داغه، گفتن چطور حرف زدی؟ گفت استثناء بود! 🐜",
    "رفتم پیش فال‌گیر، گفت آینده‌ت روشنه، گفتم لامپمه روشن گذاشتم! 😂",
    "با مامانم دعوام شد رفتم بیرون، زنگ زد گفت نون بخر، گفتم قهرم، گفت باشه ولی نون یادت نره! 🫠",
    "گربه‌مون پیتزا خورده بود، الآن داره پشت بوم راه می‌ره دلیوری می‌کنه! 🐱🍕",
    "چرا کامپیوتر نمی‌ره مهمونی؟ چون با ویروس می‌ره! 💻🦠",
    "از امروز تصمیم گرفتم ورزش کنم، فقط تصمیم گرفتم! 💪😂",
    "یارو انقدر دروغ گفته آیفونش تبدیل شده به دروغ‌فون! 📱",
    "تو خونه ما کنترل تلویزیون قوی‌تر از رئیس جمهوره، چون حرف اونو همه گوش می‌کنن! 📺",
    "یه بار تصمیم گرفتم زود بخوابم، خوابم نبرد، تصمیمم شکست خورد! 😅"
    
    

    ]
fortunes = [
    "امروز روز خوبیه برای شروع یه کار جدید! 🌞",
    "به حرف دلت گوش بده، راه درسته! 💖",
    "یک دوست قدیمی بهت سر خواهد زد. 🤝",
    "با اعتماد به نفس جلو برو، موفق می‌شی! 🚀",
    "خبر خوبی در راهه! 📩",
    "امروز یه فرصت عالی در انتظارت هست. 🌈",
    "آرومت کن و لبخند بزن. 😊",
    "به کسی که دوستش داری زنگ بزن. ☎️",
    "وقتشه به هدفت نزدیک‌تر بشی. 🎯",
    "دنیا پر از اتفاقات خوبه. 🌍",
    "به زودی سورپرایز می‌شی! 🎉",
    "صبور باش، همه چیز درست می‌شه. 🕊️",
    "یک تصمیم مهم باید بگیری. 🤔",
    "شانس با تو یاره! 🍀",
    "امروز قراره لبخند بزنی. 😄",]

questions = [
    "آیا شما فرد منظمی هستید؟",
    "آیا به راحتی عصبانی می‌شوید؟",
    "آیا از تنهایی لذت می‌برید؟",
    "آیا زیاد صحبت می‌کنید؟",
    "آیا در تصمیم‌گیری سریع هستید؟",
    "آیا ترجیح می‌دهید برنامه‌ریزی کنید؟",
    "آیا در جمع احساس راحتی دارید؟",
    "آیا خلاق هستید؟",
    "آیا اغلب احساس نگرانی دارید؟",
    "آیا اهل ریسک هستید؟",
]

iranian_cities = [
    "تهران", "مشهد", "اصفهان", "شیراز", "تبریز", "کرمانشاه", "اهواز",
    "رشت", "ارومیه", "همدان", "یزد", "بندرعباس", "کرج", "ساری", "زنجان"
]

# ---------------------- Keyboards ---------------------- #
main_menu = ReplyKeyboardMarkup([
    ["🃏 فال", "😂 جوک"],
    ["🧠 تست شخصیت", "🌦 آب‌وهوا"],
    ["🌐 ترجمه", "⚙️ کانفیگ"]
], resize_keyboard=True)

back_button = ReplyKeyboardMarkup([
    ["🔙 بازگشت"]
], resize_keyboard=True)

admin_panel = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ افزودن کانفیگ", callback_data="add_config")],
    [InlineKeyboardButton("📝 ویرایش کانفیگ", callback_data="edit_config")],
    [InlineKeyboardButton("❌ حذف کانفیگ", callback_data="delete_config")],
    [InlineKeyboardButton("📤 ارسال پیام", callback_data="broadcast_msg")],
    [InlineKeyboardButton("📎 ارسال فایل", callback_data="broadcast_file")],
    [InlineKeyboardButton("📊 آمار کاربران", callback_data="stats")],
    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu")],
])

# ---------------------- Handlers ---------------------- #
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    await update.message.reply_text(
        f"سلام {user.first_name} عزیز! 👋\nآیدی شما: {user.id}",
        reply_markup=main_menu
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "😂 جوک":
        await update.message.reply_text(random.choice(jokes), reply_markup=back_button)

    elif text == "🃏 فال":
        await update.message.reply_text(random.choice(fortunes), reply_markup=back_button)

    elif text == "🧠 تست شخصیت":
        user_states[user_id] = {"step": 0, "yes": 0}
        await update.message.reply_text(f"{questions[0]}\n(بله / خیر)", reply_markup=back_button)

    elif text.lower() in ["بله", "خیر"] and user_id in user_states:
        state = user_states[user_id]
        if text == "بله":
            state["yes"] += 1
        state["step"] += 1
        if state["step"] < len(questions):
            await update.message.reply_text(f"{questions[state['step']]}\n(بله / خیر)")
        else:
            yes_count = state["yes"]
            if yes_count >= 8:
                result = "شخصیت فعال و اجتماعی"
            elif yes_count >= 5:
                result = "متعادل و محتاط"
            else:
                result = "درون‌گرا و آرام"
            await update.message.reply_text(f"نتیجه تست شخصیت: {result}", reply_markup=main_menu)
            del user_states[user_id]

    elif text == "🌐 ترجمه":
        context.user_data["translate"] = True
        await update.message.reply_text("لطفاً متنی برای ترجمه بنویسید:", reply_markup=back_button)

    elif text and context.user_data.get("translate"):
        translated = GoogleTranslator(source='auto', target='fa' if any('ا' <= c <= 'ی' for c in text) else 'en').translate(text)
        await update.message.reply_text(f"ترجمه: {translated}", reply_markup=main_menu)
        context.user_data["translate"] = False

    elif text == "🌦 آب‌وهوا":
        await update.message.reply_text("نام شهر مورد نظر را وارد کنید (مثلاً تهران):", reply_markup=ReplyKeyboardMarkup(
            [[city] for city in iranian_cities] + [["🔙 بازگشت"]],
            resize_keyboard=True
        ))

    elif text in iranian_cities:
        city = text
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={WEATHER_API_KEY}&contentType=json"
        response = requests.get(url).json()
        if "days" in response:
            today = response["days"][0]
            desc = f"آب‌وهوای امروز {city}:\n🌡 دما: {today['temp']}°C\n☁ وضعیت: {today['conditions']}"
            await update.message.reply_text(desc, reply_markup=main_menu)
        else:
            await update.message.reply_text("شهر یافت نشد.", reply_markup=main_menu)

    elif text == "⚙️ کانفیگ":
        configs = load_json(config_file)
        if configs:
            message = "🔧 لیست کانفیگ‌ها:\n" + "\n".join([f"- {key}: {val}" for key, val in configs.items()])
        else:
            message = "کانفیگی ثبت نشده است."
        await update.message.reply_text(message, reply_markup=main_menu)

    elif text == "🔙 بازگشت":
        await update.message.reply_text("بازگشت به منو اصلی:", reply_markup=main_menu)

    elif text == "پنل" and update.effective_user.username == ADMIN_USERNAME[1:]:
        await update.message.reply_text("🔐 ورود به پنل ادمین:", reply_markup=admin_panel)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    await query.answer()

    if user.username != ADMIN_USERNAME[1:]:
        await query.message.reply_text("دسترسی ندارید.")
        return

    if data == "add_config":
        context.user_data["admin_action"] = "add"
        await query.message.reply_text("نام کانفیگ را وارد کنید:")

    elif data == "delete_config":
        context.user_data["admin_action"] = "delete"
        await query.message.reply_text("نام کانفیگی که می‌خواهید حذف کنید را وارد کنید:")

    elif data == "stats":
        await query.message.reply_text(f"📊 تعداد کاربران: {len(get_users())}")

    elif data == "broadcast_msg":
        context.user_data["admin_action"] = "broadcast"
        await query.message.reply_text("پیامی که می‌خواهید به همه ارسال شود را بنویسید:")

async def admin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME[1:]:
        return

    action = context.user_data.get("admin_action")
    text = update.message.text

    if action == "add":
        context.user_data["config_key"] = text
        context.user_data["admin_action"] = "add_val"
        await update.message.reply_text("مقدار کانفیگ را وارد کنید:")

    elif action == "add_val":
        configs = load_json(config_file)
        configs[context.user_data["config_key"]] = text
        save_json(config_file, configs)
        await update.message.reply_text("✅ کانفیگ افزوده شد.", reply_markup=main_menu)
        context.user_data.clear()

    elif action == "delete":
        configs = load_json(config_file)
        if text in configs:
            del configs[text]
            save_json(config_file, configs)
            await update.message.reply_text("❌ کانفیگ حذف شد.", reply_markup=main_menu)
        else:
            await update.message.reply_text("کانفیگ پیدا نشد.")
        context.user_data.clear()

    elif action == "broadcast":
        count = 0
        for uid in get_users():
            try:
                await context.bot.send_message(chat_id=uid, text=text)
                count += 1
            except:
                continue
        await update.message.reply_text(f"📨 پیام برای {count} کاربر ارسال شد.", reply_markup=main_menu)
        context.user_data.clear()

# ---------------------- Main ---------------------- #
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(MessageHandler(filters.TEXT, admin_text_handler))

    app.run_polling(timeout=60)

if __name__ == "__main__":
    main()
