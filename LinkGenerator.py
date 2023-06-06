import logging
import time
from datetime import datetime, timedelta
from telegram import Update, ChatMember
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters

logging.basicConfig(level=logging.INFO)
updater = Updater("Bot_Token")

VERSION = "V2.0"

def get_link(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if not context.bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']:
        update.message.reply_text("Only admins can use this command.")
        return

    try:
        limit = int(context.args[0])
        duration = int(context.args[1])
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /getlink <number_of_uses> <duration_in_minutes>")
        return

    if limit < 1:
        update.message.reply_text("The number of uses should be at least 1.")
        return

    if duration < 1:
        update.message.reply_text("The duration should be at least 1 minute.")
        return

    try:
        expire_date = datetime.utcnow() + timedelta(minutes=duration)
        invite_link = context.bot.create_chat_invite_link(chat_id, member_limit=limit, expire_date=expire_date)
        context.chat_data['invite_link'] = invite_link.invite_link
        context.chat_data['expire_date'] = expire_date.timestamp()
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


def migrateid(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    try:
        target_user_id = int(context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /migrateid <user_id>")
        return

    if user_id == target_user_id:
        update.message.reply_text("You cannot migrate yourself.")
        return

    try:
        context.bot.ban_chat_member(chat_id, user_id)
        expire_date = datetime.utcnow() + timedelta(minutes=1)
        invite_link = context.bot.create_chat_invite_link(chat_id, member_limit=1, expire_date=expire_date)
        context.bot.send_message(target_user_id, f"Migrate link: {invite_link.invite_link}")
    except Exception as e:
        update.message.reply_text("An error occurred while migrating the user.")
        logging.error(e)

def check_expired_links(context: CallbackContext):
    for chat_id, chat_data in context.chat_data.items():
        if 'expire_date' in chat_data and chat_data['expire_date'] <= time.time():
            try:
                context.bot.revoke_chat_invite_link(chat_id, chat_data['invite_link'])
                del chat_data['invite_link']
                del chat_data['expire_date']
            except Exception as e:
                logging.error(e)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(f"Hey there, I'm alive! This is Link Generator {VERSION}")

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("getlink", get_link, pass_args=True, filters=Filters.chat_type.groups))
dispatcher.add_handler(CommandHandler("revoke", revoke_link, filters=Filters.chat_type.groups))
dispatcher.add_handler(CommandHandler("migrateid", migrateid, pass_args=True, filters=Filters.chat_type.groups))
dispatcher.add_handler(CommandHandler("start", start))
updater.job_queue.run_repeating(check_expired_links, interval=60, first=0)
updater.start_polling()
updater.idle()
