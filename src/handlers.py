import io
import logging

import openai
import telebot

from config import ChangeableParameters, Config
from db import (
    add_message,
    add_token_usage,
    clear_conversation_history,
    get_conversation_history,
    get_total_tokens_used,
)
from utils import (
    download_and_convert_audio,
    generate_command_keyboard,
    log_message,
    process_set_parameters,
    save_new_parameter_value,
    text_to_speech,
    transcribe_audio,
)

config = Config()
bot = telebot.TeleBot(config.telegram_api_token)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
telebot.logger.handlers = logger.handlers


user_data = {}
user_state = {}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    log_message(logger, message)
    user_id = message.from_user.id
    clear_conversation_history(user_id)
    user_data[user_id] = False
    bot.reply_to(message, "Hello! Please enter the password:", reply_markup=generate_command_keyboard())


@bot.message_handler(commands=["commands"])
def show_commands(message):
    user_id = message.from_user.id
    if user_data.get(user_id):
        bot.reply_to(message, "Here are the available commands:", reply_markup=generate_command_keyboard())
    else:
        bot.reply_to(message, "You need to provide the correct password before using this command.")


@bot.message_handler(commands=["clearhistory"])
def clear_history(message):
    user_id = message.from_user.id
    if user_data.get(user_id):
        clear_conversation_history(user_id)
        bot.reply_to(message, "Conversation history cleared.")
    else:
        bot.reply_to(message, "You need to provide the correct password before using this command.")


@bot.message_handler(commands=["listparameters"])
def list_parameters(message):
    user_id = message.from_user.id
    if user_data.get(user_id):
        user_params = user_state.get(user_id, config.changeable_parameters)
        if not isinstance(user_params, ChangeableParameters):
            user_params = config.changeable_parameters
        params = "\n".join(
            [f"{param.capitalize()}: {getattr(user_params, param)}" for param in user_params.__fields__.keys()]
        )
        bot.reply_to(message, f"Current parameters:\n\n{params}")
    else:
        bot.reply_to(message, "You need to provide the correct password before using this command.")


@bot.message_handler(commands=["setparameters"])
def set_parameters(message):
    user_id = message.from_user.id
    if user_data.get(user_id):
        parameter_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        for field_name in config.changeable_parameters.__fields__.keys():
            parameter_keyboard.row(field_name)

        parameter_keyboard.row("Cancel")
        user_state[user_id] = "setparameters"
        bot.reply_to(message, "Select a parameter to change:", reply_markup=parameter_keyboard)
    else:
        bot.reply_to(message, "You need to provide the correct password before using this command.")


@bot.message_handler(commands=["infotokens"])
def info_tokens(message):
    user_id = message.from_user.id
    if user_data.get(user_id):
        total_tokens = get_total_tokens_used(user_id)
        bot.reply_to(message, f"Total number of tokens used: {total_tokens}")
    else:
        bot.reply_to(message, "You need to provide the correct password before using this command.")


@bot.message_handler(func=lambda message: True)
def process_message(message):
    user_id = message.from_user.id
    user_params = user_state.get(user_id, config.changeable_parameters)
    if not user_data.get(user_id):
        log_message(logger, message)
        if message.text == config.correct_password:
            user_data[user_id] = True
            bot.reply_to(message, "Password is correct. You can now send messages.")
        else:
            bot.reply_to(message, "Incorrect password. Please try again.")
    elif user_state.get(user_id) == "setparameters":
        process_set_parameters(bot, user_state, user_id, message)
    elif user_state.get(user_id) in config.changeable_parameters.__fields__.keys():
        save_new_parameter_value(bot, logger, user_state, user_id, message)
    else:
        if message.voice:
            audio_file = download_and_convert_audio(bot, message.voice.file_id)
            text = transcribe_audio(audio_file)
        else:
            text = message.text
        log_message(logger, message)
        add_message(user_id, "user", text)
        conversation_history = get_conversation_history(user_id)
        response = openai.ChatCompletion.create(
            model=user_params.model,
            messages=conversation_history,
            temperature=user_params.temperature,
            max_tokens=user_params.max_tokens,
        )
        reply = response.choices[0].message.content
        add_message(user_id, "assistant", reply)

        # Save and display token usage
        usage = response["usage"]
        add_token_usage(user_id, usage["prompt_tokens"], usage["completion_tokens"], usage["total_tokens"])

        if message.voice:
            audio_content = text_to_speech(reply)
            bot.send_voice(
                chat_id=message.chat.id, voice=io.BytesIO(audio_content), reply_to_message_id=message.message_id
            )
        else:
            bot.reply_to(message, reply)

        if config.changeable_parameters.verbose:
            add_info = (
                f"\n\n(prompt_tokens: {usage['prompt_tokens']}, completion_tokens: {usage['completion_tokens']},"
                f" total_tokens: {usage['total_tokens']})"
            )
            bot.reply_to(message, add_info)
