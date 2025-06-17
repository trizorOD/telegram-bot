
import os


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler


# 🔐 Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 467438413  # ← Укажите ваш Telegram ID от @userinfobot
# ADMIN_ID = 320352130  # ← Укажите ваш Telegram ID от @userinfobot

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {'step': 'product_name', 'items': []}

    await update.message.reply_text("Привет! Введите название первого продукта:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if chat_id not in user_data:
        user_data[chat_id] = {'step': 'product_name', 'items': []}
        await update.message.reply_text("Введите название продукта:")
        return

    state = user_data[chat_id]
    step = state['step']

    if step == 'product_name':
        state['current_product'] = text
        state['step'] = 'quantity'
        await update.message.reply_text("Введите количество:")
    elif step == 'quantity':
        product = state['current_product']
        quantity = text
        state['items'].append({'product': product, 'quantity': quantity})
        state['step'] = 'awaiting_choice'

        keyboard = [
            [InlineKeyboardButton("➕ Добавить товар", callback_data='add_more')],
            [InlineKeyboardButton("✅ Завершить заказ", callback_data='finish_order')]
        ]
        await update.message.reply_text("Хотите добавить ещё товар или завершить заказ?", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    state = user_data.get(chat_id)

    if query.data == 'new_order':
        user_data[chat_id] = {'step': 'product_name', 'items': []}
        await query.message.reply_text("Введите название продукта:")
        return


    if query.data == 'add_more':
        state['step'] = 'product_name'
        await query.message.reply_text("Введите название следующего продукта:")
    elif query.data == 'finish_order':
        items = state['items']
        user = query.from_user
        user_mention = f"@{user.username}" if user.username else str(user.id)

        lines = [f"📦 Новая заявка:", f"🔹 Пользователь - {user_mention}", ""]
        for idx, item in enumerate(items, 1):
            lines.append(f"{idx}. {item['product']} — {item['quantity']} шт.")

        message = "\n".join(lines)

        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=message)
            print("Заявка отправлена.")
        except Exception as e:
            print(f"Ошибка отправки админу: {e}")

        # Сбросим форму
        keyboard = [[InlineKeyboardButton("Новый заказ", callback_data='new_order')]]
        await query.message.reply_text("✅ Спасибо! Ваша заявка отправлена.", reply_markup=InlineKeyboardMarkup(keyboard))
        del user_data[chat_id]

    elif query.data == 'new_order':
        user_data[chat_id] = {'step': 'product_name', 'items': []}
        await query.message.reply_text("Введите название продукта:")

# Запуск
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

print("✅ Бот с мульти-товарными заказами запущен...")
app.run_polling()
