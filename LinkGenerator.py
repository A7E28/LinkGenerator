import logging
from telegram import Update, ChatInviteLink
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters

logging.basicConfig(level=logging.INFO)
updater = Updater("Bot_Token")

def get_link(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if not context.bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']:
        update.message.reply_text("Only admins can use this command.")
        return

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
        context.chat_data['invite_link'] = invite_link.invite_link
        update.message.reply_text(f"Here's your invite link: {invite_link.invite_link}")
    except Exception as e:
        update.message.reply_text("An error occurred while generating the invite link.")
        logging.error(e)

def revoke_link(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if not context.bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']:
        update.message.reply_text("Only admins can use this command.")
        return

    try:
        invite_link = context.chat_data['invite_link']
        context.bot.revoke_chat_invite_link(chat_id, invite_link)
        update.message.reply_text("The invite link has been revoked.")
    except KeyError:
        update.message.reply_text("No invite link has been generated yet.")
    except Exception as e:
        update.message.reply_text("An error occurred while revoking the invite link.")
        logging.error(e)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hey there! I'm alive:) This is link generator V1.0.17")

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("getlink", get_link, pass_args=True, filters=Filters.chat_type.groups))
dispatcher.add_handler(CommandHandler("revoke", revoke_link, filters=Filters.chat_type.groups))
dispatcher.add_handler(CommandHandler("start", start))
updater.start_polling()
updater.idle()
