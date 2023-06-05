import logging
from telegram import Update, ChatInviteLink
from telegram.ext import Updater, CommandHandler, CallbackContext



logging.basicConfig(level=logging.INFO)
updater = Updater("Bot_Token")



def get_link(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    try:
        limit = int(context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /getlink <number_of_uses>")
        return

    if limit < 1:
        update.message.reply_text("The number of uses should be at least 1.")
        return

    try:
        invite_link = context.bot.create_chat_invite_link(chat_id, member_limit=limit)
        update.message.reply_text(f"Here's your invite link: {invite_link.invite_link}")
    except Exception as e:
        update.message.reply_text("An error occurred while generating the invite link.")
        logging.error(e)



dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("getlink", get_link, pass_args=True))
updater.start_polling()
updater.idle()
