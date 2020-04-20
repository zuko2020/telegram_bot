import datetime
import logging

import telebot
from telebot import apihelper
from telebot.types import Message

from credentials import BOT_TOKEN, PROXY
from commands import init_command
from db.models import init_db, get_sudoers
from utils import admin_list

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


bot = telebot.TeleBot(BOT_TOKEN)
apihelper.proxy = {'https': 'socks5://{}'.format(PROXY)}

print('@@@ => INITIALIZE DATABASE <= @@@')
init_db()
print('@@@ => INITIALIZE BOT', bot.get_me(), '<= @@@')

# INITIALIZE AVAILABLE COMMANDS.
light_commands = init_command('flood', 'share', 'tut', 'web', 'wq')
sudo_commands = init_command('ban', 'unban', 'sudo', 'warn', 'sudoers')


@bot.message_handler(regexp='^![a-z]')
def handle_message(message: Message):
    """
    Main command handler. All members can use light commands. Admins and sudo can use admins commands.
    Users can`t notify admins with this commands.
    :param message: Telegram API message
    """
    user_id, command = message.from_user.id, message.text.split()[0].lower()
    bot.delete_message(message.chat.id, message.message_id)
    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        reply_to = message.reply_to_message
        if reply_to and reply_to.from_user.id not in admin_list(message.chat.id, bot):
            if command:
                try:
                    light_commands[command](message, bot)
                except (AttributeError, KeyError, TypeError):
                    try:
                        if user_id in admin_list(message.chat.id, bot) + get_sudoers():
                            sudo_commands[command](message, bot)
                    except (AttributeError, KeyError, TypeError) as e:
                        print(e)


@bot.message_handler(content_types=['new_chat_members'])
def handler_new_member(message: Message):
    """
    New member mute chat group for 5 minutes.
    Works for joined and invited users.
    NOTE! mute_till.strftime('%s') not working on windows platform! Need to use timestamp() * 1000 or refactoring
    :param message: Telegram API message
    """
    mute_till = datetime.datetime.now() + datetime.timedelta(minutes=5)
    bot.restrict_chat_member(
        message.chat.id,
        message.new_chat_member.id,
        until_date=mute_till.strftime('%s'),
        can_send_media_messages=False,
        can_add_web_page_previews=False,
        can_send_other_messages=False,
        can_send_messages=False
    )


bot.polling()
