import yaml
import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Task, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.memory import ShortTermMemory, LongTermMemory
from src.configuration.settings import settings
from typing import Dict
from pathlib import Path

load_dotenv()

class CrewManager:
    def __init__(self, agent_config_path: str):
        ##current directory parent folder path
        self.crew_dir = Path(__file__).parent
        self.agent_config_path = agent_config_path
        self.listed_mcp_tools = 
        self.llm = self.initialize_llm()
        self.agents = self.boot_agents()
        self.tasks = self.boot_tasks()
        ##Private to prevent the memory() call from other files and functions
        self._conversation_memory()

        # def _conversation_memory(self):
        #     try:
        #         ###Conditional Memory flag check###
        #         if settings.short_term_memory_flag or settings.long_term_memory_flag:

        #     except Exception as e:
        #         print(f"Error occured as :{e}")

    def initialize_llm(self):
        try:
            llm = LLM(
                model = settings.base_model_name,
                api_version = settings.gemini_model_version,
                temperature = settings.base_model_llm_temperature,
                max_tokens = settings.model_max_tokens
            )

            return llm
        except Exception as e:
            print(f'Failed to initialize the llm with issue as: {e}')
            raise

    def boot_agents(self) -> Dict:
        """Loading agents for cortexsail.ai"""
        try: 
            agent_configuration = self.crew_dir / "agents.yaml"
            with open(agent_configuration,'r', encoding='utf-8') as f:
                ##safeload parsers yaml -> return python object
                agent_configuration = yaml.safe_load(f)
                ##temp storage var for agents
                agents{}

                mcp_tools = list(self.listed_mcp_tools)
                ###Initialize the tools in Tools folder then enable


                # mcp_tools.append(search_similar_defect)

                