import yaml
import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Task, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.memory import ShortTermMemory, LongTermMemory
from src.configuration.settings import settings
from typing import Dict, List
from pathlib import Path
from crewai_tools import MCPServerAdapter

load_dotenv()

class CrewManager:
    def __init__(self, agent_config_path: str):
        ##current directory parent folder path
        self.crew_dir = Path(__file__).parent
        self.agent_config_path = agent_config_path
        self.listed_mcp_tools = self.load_mcp_tools()
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
                api_version = settings.azure_api_version,
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
                agents = {}

                ###Initialize the tools in Tools folder then enable
                all_tools = list(self.listed_mcp_tools)
                

                ## MCP Tools + vector store tools 
                

                ##Orchestration agent (MCP + vector store tools)
                orchestrator_config  = agent_configuration["orchestrator_agent"]
                agents["orchestation_agent"] = Agent(
                    role = orchestrator_config["role"],
                    goal = orchestrator_config["goal"],
                    backstory = orchestrator_config["backstory"],
                    tools = all_tools,
                    instructions = orchestrator_config["instructions"],
                    intent_category = orchestrator_config["intent_categories"],
                    allowed_execution_steps = orchestrator_config["allowed_execution_steps"],
                    allowed_agents = orchestrator_config["allowed_agents"],
                    output_contract = orchestrator_config["output_contract"],
                    decision_policy = orchestrator_config["decision_policy"],
                    guardrails_llm = orchestrator_config["guardrails_llm"],
                    guardrails_output = orchestrator_config["guardrails_output"],
                    llm = self.llm,
                    verbose = orchestrator_config.get('verbose', True)
                )


                ##Knowledge agent (RAG tools)
                knowledge_agent_configuration = agent_configuration["knowledge_agent"]
                agents['knowledge_agent'] = Agent(
                    role = knowledge_agent_configuration["role"],
                    goal = knowledge_agent_configuration["goal"],
                    backstory = knowledge_agent_configuration["backstory"],
                    tools = knowledge_agent_configuration["tools"],
                    instructions = knowledge_agent_configuration["instructions"],
                    context = knowledge_agent_configuration["context"],
                    retrieval_rules = knowledge_agent_configuration["retrieval_rules"],
                    llm = self.llm,
                    tools = knowledge_agent_configuration["tools"],
                    output_contract = knowledge_agent_configuration["output_contract"],
                    verbose = knowledge_agent_configuration.get('verbose', True),
                    guardrails = knowledge_agent_configuration["guardrails"],
                    guardrails_output = knowledge_agent_configuration["guardrails_output"]
                )

                ##Reasoning agent (no tools)
                reasoning_agent_configuration = agent_configuration["reasoning_agent"]
                agents['reasoning_agent'] = Agent(
                    role = reasoning_agent_configuration["role"],
                    goal = reasoning_agent_configuration["goal"],
                    backstory = reasoning_agent_configuration["backstory"],
                    instructions = reasoning_agent_configuration["instructions"],
                    context = reasoning_agent_configuration["context"],
                    llm = self.llm,
                    output_contract = reasoning_agent_configuration["output_contract"],
                    tools = reasoning_agent_configuration["tools"],
                    guardrails = reasoning_agent_configuration["guardrails"],
                    guardrails_output = reasoning_agent_configuration["guardrails_output"] 
                )

                ###Memory agent (memory management tools)
                memory_agent_configuration = agent_configuration["memory_agent"]
                agents['memory_agent'] = Agent(
                    role = memory_agent_configuration["role"],
                    goal = memory_agent_configuration["goal"],
                    backstory = memory_agent_configuration["backstory"],
                    instructions = memory_agent_configuration["instructions"],
                    context = memory_agent_configuration["context"],
                    llm = self.llm,
                    tools = memory_agent_configuration["tools"],
                    output_contract = memory_agent_configuration["output_contract"],
                    verbose = memory_agent_configuration.get('verbose', True),
                    guardrails = memory_agent_configuration["guardrails"],
                    guardrails_output = memory_agent_configuration["guardrails_output"] 
                ) 
                ###Response agent (final response generation, no tools)
                response_agent_configuration = agent_configuration["response_agent"]
                agents['response_agent'] = Agent(
                    role = response_agent_configuration["role"],
                    goal = response_agent_configuration["goal"],
                    backstory = response_agent_configuration["backstory"],
                    instructions = response_agent_configuration["instructions"],
                    context = response_agent_configuration["context"],
                    llm = self.llm,
                    tools = response_agent_configuration["tools"],
                    output_contract = response_agent_configuration["output_contract"],
                    verbose = response_agent_configuration.get('verbose', True),
                    guardrails = response_agent_configuration["guardrails"],
                )

                print("Agents successfully loaded and initialized.")
                return agents

                ###all logger after initialization dont print in prod
        except Exception as e:
            print(f'Error loading agent configuration: {e}')
            raise
    def load_mcp_tools(self) -> List:
        """Loading the listed MCP tools from the tools directory"""
        try:
            print("MCP tools setup initialized.")
            mcp_endpoint = getattr(settings, "mcp_endpoint", 'http://localhost:8081/sse')
            mcp_transport = getattr(settings, "mcp_transport", 'sse')
            mcp_connection_timeout = getattr(settings, "mcp_connection_timeout", 60)

            ###sse server parameters

            server_params = {
                "url" : mcp_endpoint,
                "transport" : mcp_transport,
                "connection_timeout" : mcp_connection_timeout
            }

            ###MCP adapter initialization for server connection and tool execution

            ### **serverparams for dict unpacking in the adapter initialization
            mcp_adapter = MCPServerAdapter(server_params, connection_timeout = mcp_connection_timeout)

            ##To get the tools from the adapter, we need to enter the context manager
            mcp_tools = mcp_adapter.__enter__()

            print(f"Available MCP tools loaded: {[tool.name for tool in mcp_tools]}")
            print("MCP tools setup completed.")
            return mcp_tools

        except Exception as e:
            print(f'Error loading MCP tools: {e}')
            raise

                