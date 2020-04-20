import telebot
from telebot.types import Message

from db.models import User
from utils import prepare_user_data


def sudoers_process(message: Message, bot: telebot):
    """
    Return sudoers list in private message.
    :param message: Telegram API Message
    :param bot: Telebot instance
    """
    users = [user for user in User.select().where(User.is_sudo == True)]
    msg = 'Sudo пользователи: '
    for user in users:
        msg += '`{}` {}; '.format(user.telegram_id, prepare_user_data(user))
    bot.send_message(message.from_user.id, text=msg, parse_mode='markdown')
