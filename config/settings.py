from pydantic_settings import BaseSettings
from functools import lru_cache 
from dotenv import load_dotenv 
import os 

load_dotenv()

class Settings(BaseSettings):
  OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
  OPENAI_MODEL_NAME: str = os.getenv('OPENAI_MODEL_NAME')

@lru_cache()
def get_settings() -> Settings:
  return Settings()