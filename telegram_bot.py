from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
import pandas as pd
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

names = []


# پاسخ به start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ارسال فایل", callback_data="send_file")],
        [InlineKeyboardButton("ثبت نام", callback_data="register_name")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام من ربات تلگرامی شما هستم! لطفا گزینه مورد نظر خود را انتخاب کنید:",
                                    reply_markup=reply_markup)


# هندلر دکمه ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['mode'] = query.data

    if query.data == "send_file":
        await query.message.reply_document(
            document=open("introduction_to_computers_by_peter_norton.pdf", "rb")
        )
        await query.message.reply_text("فایل ارسال شد ✅")
        await show_menu(update, context)

    elif query.data == "register_name":
        await query.message.reply_text("لطفا نام و نام خانوادگی خود را ارسال کنید")


# دریافت نام و ذخیره در CSV
async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if mode == "register_name":
        name = update.message.text
        username=update.effective_user.username or "ندارد"

        #ذخیره به صورت دیکشنری
        names.append({"Name":name,"Username":username})
        df = pd.DataFrame(names)
        df.to_csv("names.csv", index=False)

        await update.message.reply_text(f"{name}جان اسم و نام کاربری شما ذخیره شد!")
        context.user_data['mode'] = None  # پاک کردن حالت
        await show_menu(update, context)

    else:
        await update.message.reply_text("لطفا ابتدا دکمه 'ثبت نام' را انتخاب کنید")


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ارسال فایل", callback_data="send_file")],
        [InlineKeyboardButton("ثبت نام", callback_data="register_name")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا گزینه بعدی مورد نظر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"خطا: {context.error}")


# ساخت اپلیکیشن
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_name))
app.add_error_handler(error_handler)

app.run_polling()
