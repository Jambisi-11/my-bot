import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Replace with your actual bot token
API_TOKEN = '8038486969:AAEyibm7lESIkBOZrgLBwjC7CwB4yxbIfxs'

# Replace with your actual Telegram user ID (Admin ID)
ADMIN_CHAT_ID = 865785423

# Dictionary to store pending messages (message_id -> (user_id, chat_id, username, message_text))
pending_messages = {}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command."""
    await update.message.reply_text("Hello! Send me a message, and I will forward it after approval.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Intercept user messages and hold them for approval."""
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    username = update.message.from_user.username  # Get the username of the sender
    message_text = update.message.text
    message_id = update.message.message_id

    # Delete the original message
    await update.message.delete()

    # Notify the user that their message is under review
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🌱 Hi @{username}, your message is under review. Please wait for approval."
    )

    # Store the message for approval (including the username)
    pending_messages[message_id] = (user_id, chat_id, username, message_text)

    # Create an inline keyboard for approval
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f'approve_{message_id}'),
            InlineKeyboardButton("❌ Reject", callback_data=f'reject_{message_id}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message to the admin for approval (including the username)
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"New message for approval from @{username} (ID: {user_id}):",
        reply_markup=reply_markup
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_text)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin's approval or rejection."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    message_id = int(callback_data.split('_')[1])

    if message_id in pending_messages:
        user_id, chat_id, username, message_text = pending_messages[message_id]

        if callback_data.startswith('approve'):
            # Send the approved message to the user (including the username)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ Hi @{username}, your message has been approved:\n\n{message_text}"
            )
            await query.edit_message_text(text=f"✅ Message from @{username} approved:")
        elif callback_data.startswith('reject'):
            # Notify the user that their message was rejected (including the username)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Hi @{username}, your message was rejected."
            )
            await query.edit_message_text(text=f"❌ Message from @{username} rejected:")

        # Remove message from pending list
        del pending_messages[message_id]

def main() -> None:
    """Start the bot."""
    print("Bot is running...")
    
    app = Application.builder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Run the bot until you press Ctrl-C
    app.run_polling()

if __name__ == "__main__":
    print("Bot is starting...")
    main()