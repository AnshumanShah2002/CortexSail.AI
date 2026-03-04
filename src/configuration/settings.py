"""Base settings configuration for Cortexsail"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):

    ## Environ variables for usage gemini model
    gemini_api_key: str = "####"
    gemini_api_endpoint = "####"
    gemini_api_version = "###"
    gemini_model_version = "####"

    ### Basic configuration ###

    base_model_name: str = "gemini-2.5-flash"
    base_model_llm_temperature: float = 0.3
    model_max_tokens = 1000


    ### memory flag ###
    short_term_memory_flag:bool = False
    long_term_memory_flag:bool = False


    def boot_settings(self) -> Settings:
        try:
            load_dotenv()
            settings = Settings()
            os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
            os.environ["GEMINI_API_ENDPOINT"] = settings.gemini_api_endpoint
            os.environ["GEMINI_MODEL_VERSION"] = settings.gemini_model_version
            os.environ["GEMINI_API_VERSION"] = settings.gemini_api_version

            #To be toggled when declaring the memory config file for both types
            return settings
        except Exception as e:
            print(f"Failed to load the config with issue as: {e}")
            raise ValueError(f"Config issue occured")
        
settings = Settings() 

