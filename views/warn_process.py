import datetime

import telebot
from telebot.types import Message

from db.models import Warns
from utils import prepare_user_data, get_or_create_user


def warn_process(message: Message, bot: telebot) -> Message:
    """
    Warning user. User delete from chat member if get three warnings.
    :param message: Telegram API Message
    :param bot: Telebot instance
    :return response message from Telegram API server
    """
    msg = message.text.split()
    if len(msg) > 1:
        reason = msg[1:]
        user, created = get_or_create_user(message.reply_to_message)
        if user:
            warns_count = Warns.select().filter(user=user).count()
            warning_user = prepare_user_data(user)
            reason = ' '.join([i for i in reason])
            if warns_count == 2:
                warns_count += 1
                Warns.create(
                    user=user,
                    warn_number=warns_count,
                    reason=reason,
                    datetime_add=datetime.datetime.now(),
                )
                msg = f'*{message.from_user.username} предупредил пользователя {warning_user}\nПричина:*\n`{reason}`\n' \
                      f'Предупреждение `{warns_count}/3`\n' \
                      f'`Пользователь заблокирован`'
                bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                return bot.reply_to(message.reply_to_message, text=msg, parse_mode='markdown')
            elif warns_count < 2:
                warns_count += 1
                Warns.create(
                    user=user,
                    warn_number=warns_count,
                    reason=reason,
                    datetime_add=datetime.datetime.now(),
                )
                msg = f'*{message.from_user.username} предупредил пользователя {warning_user}\nПричина:*\n`{reason}`\n' \
                      f'Предупреждение `{warns_count}/3`\n' \
                      f'`После третьего предупреждения будет применена автоматическая блокировка`'
                return bot.reply_to(message.reply_to_message, text=msg, parse_mode='markdown')
            else:
                msg = '*Пользователь уже заблокирован*'
                bot.reply_to(message.reply_to_message, text=msg, parse_mode='markdown')
