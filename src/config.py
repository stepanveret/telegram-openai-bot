from pydantic import BaseSettings, Field


class ChangeableParameters(BaseSettings):
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 150
    history_limit: int = 10
    verbose: bool = True
    audio_model: str = "whisper-1"
    audio_language_code: str = "ru-RU"
    audio_language_name: str = "ru-RU-Standard-E"  # en-US-Standard-C"


class Config(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    # google_api_key: str = Field(..., env="GOOGLE_APPLICATION_CREDENTIALS")
    telegram_api_token: str = Field(..., env="TELEGRAM_YJACDNX_API_KEY")
    correct_password: str = Field(..., env="TELEGRAM_YJACDNX_PASSWORD")
    changeable_parameters: ChangeableParameters = ChangeableParameters()
