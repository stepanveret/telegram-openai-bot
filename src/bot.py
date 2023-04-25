import logging

import telebot

from config import Config
from db import init_db
from handlers import (
    clear_history,
    info_tokens,
    list_parameters,
    process_message,
    send_welcome,
    set_parameters,
    show_commands,
)

config = Config()
init_db()

bot = telebot.TeleBot(config.telegram_api_token)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot.add_message_handler({"function": send_welcome, "filters": {"commands": ["start"]}})
bot.add_message_handler({"function": show_commands, "filters": {"commands": ["commands"]}})
bot.add_message_handler({"function": clear_history, "filters": {"commands": ["clearhistory"]}})
bot.add_message_handler({"function": list_parameters, "filters": {"commands": ["listparameters"]}})
bot.add_message_handler({"function": set_parameters, "filters": {"commands": ["setparameters"]}})
bot.add_message_handler({"function": info_tokens, "filters": {"commands": ["infotokens"]}})
bot.add_message_handler({"function": process_message, "filters": {}})  # empty filters for the process_message handler

bot.polling()
