import logging
import warnings
import asyncio
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CommandHandler, ApplicationBuilder
from datetime import datetime, timedelta
from dotenv import load_dotenv


#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

warnings.filterwarnings("ignore", category=DeprecationWarning, module="telegram.ext")

load_dotenv()
token = os.getenv('TOKEN')


def restricted_admin(func):
    async def wrapper(update: Update, context: CallbackContext) -> None:
        if update.message:
            chat = update.message.chat
            user_id = update.message.from_user.id

            is_admin = False
            try:
                member = await chat.get_member(user_id)
                is_admin = member.status in ['creator', 'administrator']
            except Exception as e:
                print(f"Error retrieving member: {e}")

            if user_id is not is_admin:
                await update.message.reply_text("You need to be an admin to do this.")
                return

        asyncio.create_task(func(update, context))  # Use 'create_task' to schedule the coroutine
    return wrapper



def adduser(func):
    async def wrapper(update: Update, context: CallbackContext) -> None:
        chat = update.effective_chat
        bot_id = context.bot.id
        if update.effective_chat.type == 'private':
            return
        
        is_admin = False
        try:
            member = await chat.get_member(bot_id)
            is_admin = member.status in ['creator', 'administrator']
        except Exception as e:
            print(f"Error retrieving bot member: {e}")

        if not is_admin:
            await update.message.reply_text("I need to be an admin to perform this action.")
            return
        permissions = await chat.get_member(bot_id)
        if not permissions.can_invite_users:
            await context.bot.send_message(chat.id, "I don't have enough rights for this.\nAllow Add Users permission.")
            return
        asyncio.create_task(func(update, context))
    return wrapper




def UserCanAddUser(func):
    async def wrapper(update: Update, context: CallbackContext) -> None:
        chat = update.effective_chat
        user_id = update.message.from_user.id
        if update.effective_chat.type == 'private':
            return
        
        permissions = await chat.get_member(user_id)
        if not permissions.status == 'creator' and not permissions.can_invite_users:
            await context.bot.send_message(chat.id, "You are missing the 'Add Users' permission to use this command.")
            return
        asyncio.create_task(func(update, context))
    return wrapper




@adduser
@restricted_admin
@UserCanAddUser
async def get_link(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
        await update.message.reply_text("Please use this command in a group chat")
        return
    if 'invite_link' not in context.chat_data:
        context.chat_data['invite_link'] = None
    if 'expire_date' not in context.chat_data:
        context.chat_data['expire_date'] = None

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    try:
        limit = int(context.args[0])
        duration = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /getlink <number_of_users> <duration_in_minutes>")
        return

    if limit < 1:
        await update.message.reply_text("The number of uses should be at least 1.")
        return

    if duration < 1:
        await update.message.reply_text("The duration should be at least 1 minute.")
        return

    try:
        expire_date = datetime.utcnow() + timedelta(minutes=duration)
        invite_link = await context.bot.create_chat_invite_link(chat_id, member_limit=limit, expire_date=expire_date)
        context.chat_data['invite_link'] = invite_link.invite_link
        context.chat_data['expire_date'] = expire_date.timestamp()

        chat = await context.bot.get_chat(chat_id)  # Await the 'get_chat' coroutine
        group_name = chat.title
        message = f"Here's your invite link for {group_name}: {invite_link.invite_link}"
        message += f"\n\nLink duration: {duration} min(s) \nUser limit: {limit}"

        try:
            await context.bot.send_message(user_id, message)
            await update.message.reply_text("Please check your PM for the invite link.")
        except Exception as pm_error:
            logging.error(pm_error)
            await update.message.reply_text("Why am I not allowed for PM? Interact with me otherwise I can't send you the invite link.")

    except Exception as e:
        await update.message.reply_text("An error occurred while generating the invite link.")
        logging.error(e)


@adduser
@restricted_admin
async def revoke_link(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
         await update.message.reply_text("Please use this command in a group chat")
         return
         
    if 'invite_link' not in context.chat_data:
        context.chat_data['invite_link'] = None
    if 'expire_date' not in context.chat_data:
        context.chat_data['expire_date'] = None

    chat_id = update.effective_chat.id

    try:
        invite_link = context.chat_data['invite_link']
        if invite_link is None:
            await update.message.reply_text("No invite link has been generated yet.")
        else:
            await context.bot.revoke_chat_invite_link(chat_id, invite_link)
            await update.message.reply_text("The invite link has been revoked.")
    except Exception as e:
        await update.message.reply_text("An error occurred while revoking the invite link.")
        logging.error(e)



async def migrateid(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
        await update.message.reply_text("Please use this command in a group chat")
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    try:
        target_user_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /migrateid <user_id>")
        return

    if user_id == target_user_id:
        await update.message.reply_text("You cannot migrate yourself.")
        return

    try:
        context.bot.ban_chat_member(chat_id, user_id)
        expire_date = datetime.utcnow() + timedelta(minutes=1)
        invite_link = await context.bot.create_chat_invite_link(chat_id, member_limit=1, expire_date=expire_date)
        await context.bot.send_message(target_user_id, f"Migrate link: {invite_link.invite_link}")
    except Exception as e:
        await update.message.reply_text("An error occurred while migrating the user.")
        logging.error(e)




start_text = '''Hey! My name is Link Generator. I am a assistant bot, here to help you get around and keep the order in your private groups!

Join the bot support group @TheHypernovaSupport if you need any bot support or help.

Follow @TheHypernovaNews if you want to keep up with the bot news, bot updates and bot downtime!


'''



async def start(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
            keyboard = [
                [InlineKeyboardButton("Add me to your chat!", url='https://t.me/GetInviteLinkBot?startgroup=true')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=start_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"Hey, I am Link Generator and I am alive.")




bot = ApplicationBuilder().token(token).build()

bot.add_handler(CommandHandler("start", start))

bot.add_handler(CommandHandler("getlink", get_link))
bot.add_handler(CommandHandler("revoke", revoke_link))
bot.add_handler(CommandHandler("migrateid", migrateid))

print('\n\nBOT Running...')
bot.run_polling()
