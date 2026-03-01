import yaml
import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Task
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class CrewManager:
    def __init__(self, agent_config_path: str):
        self.agent_config_path = agent_config_path
        self.llm = self.initialize_llm()
        self.agents = 