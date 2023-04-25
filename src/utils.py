import io

import openai
import requests
import telebot
from pydub import AudioSegment

from config import Config

config = Config()

from google.cloud import texttospeech

# def text_to_speech(text):
#     client = texttospeech.TextToSpeechClient()

#     synthesis_input = texttospeech.SynthesisInput(text=text)
#     voice = texttospeech.VoiceSelectionParams(
#         language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
#     )
#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
#     )

#     response = client.synthesize_speech(
#         input=synthesis_input, voice=voice, audio_config=audio_config
#     )

#     return response.audio_content


def text_to_speech(text):
    client = texttospeech.TextToSpeechClient()  # credentials=config.google_api_key)
    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=config.changeable_parameters.audio_language_code,
        name=config.changeable_parameters.audio_language_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(request={"input": input_text, "voice": voice, "audio_config": audio_config})

    return response.audio_content


def download_and_convert_audio(bot, file_id):
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{config.telegram_api_token}/{file_info.file_path}"

    response = requests.get(file_url)
    audio = AudioSegment.from_ogg(io.BytesIO(response.content)).export(format="wav")

    return audio


class NamedBytesIO(io.BytesIO):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)


def transcribe_audio(audio):
    audio_data = audio.read()
    named_audio_file = NamedBytesIO("audio.wav", audio_data)
    response = openai.Audio.transcribe(model=config.changeable_parameters.audio_model, file=named_audio_file)
    transcript = response["text"]
    return transcript


def log_message(logger, message):
    logger.info(f"Received message from {message.from_user.username}: {message.text}")


def generate_command_keyboard():
    command_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    command_keyboard.row("/start", "/clearhistory")
    command_keyboard.row("/listparameters", "/setparameters")
    command_keyboard.row("/infotokens")
    return command_keyboard


def process_set_parameters(bot, user_state, user_id, message):
    response = message.text.lower().replace(" ", "_")
    if response == "cancel":
        user_state.pop(user_id, None)
        bot.reply_to(message, "You can now send messages", reply_markup=generate_command_keyboard())
    else:
        user_state[user_id] = response
        bot.reply_to(message, f"Enter the new value for {message.text}:")


def save_new_parameter_value(bot, logger, user_state, user_id, message):
    try:
        key = user_state[user_id]
        value = eval(message.text)
        setattr(config.changeable_parameters, key, value)
        bot.reply_to(message, f"{key.capitalize()} updated to {value}", reply_markup=generate_command_keyboard())
    except Exception as e:
        logger.error(f"Error updating parameter: {e}")
        bot.reply_to(message, "Error updating parameter. Please check your input and try again.")
    user_state.pop(user_id, None)
