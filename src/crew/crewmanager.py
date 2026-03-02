import yaml
import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Task, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.memory import ShortTermMemory, LongTermMemory
from src.configuration import settings

load_dotenv()

class CrewManager:
    def __init__(self, agent_config_path: str):
        self.agent_config_path = agent_config_path
        self.llm = self.initialize_llm()
        self.agents = self.listed_agents()
        self.tasks = self.boot_tasks()
        ##Private to prevent the memory() call from other files and functions
        self._conversation_memory()

        # def _conversation_memory(self):
        #     try:
        #         ###Conditional Memory flag check###
        #         if settings.

    def initialize_llm():
        try:
            llm = LLM(
                model = settings.base_model_name,
            )
