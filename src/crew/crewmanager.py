import yaml
import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Task, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.memory import ShortTermMemory, LongTermMemory
from src.configuration.settings import settings
from typing import Optional
from typing import Dict, List
from pathlib import Path
from crewai_tools import MCPServerAdapter
##Tools import for Agents
from src.Tools.rag_tools import confluence_document_fetcher, similar_documents_fetcher

load_dotenv()

####Check if agent init is correct
class CrewManager:
    def __init__(self, agent_config_path: Optional[str] = None, session_id: Optional[str] = None):
        ##current directory parent folder path
        self.crew_dir = Path(__file__).parent
        self.agent_config_path = agent_config_path
        self.session_id = session_id
        self.listed_mcp_tools = self.load_mcp_tools()
        self.llm = self.initialize_llm()
        self.agents = self.boot_agents()
        self.tasks = self.boot_tasks()
        ##Private to prevent the memory() call from other files and functions
        self._conversation_memory()

    def _conversation_memory(self):
            """Setting up memory storage directory"""
            try:
                if settings.short_term_memory_flag or settings.long_term_memory_flag:
                    memory_path = Path(settings.memory_storage_path)
                    if self.session_id:
                        ##Creating memory directory
                        memory_path = memory_path / self.session_id
                    memory_path.mkdir(parents=True, exist_ok=True)
                    print(f"Memory storage directory set up at: {memory_path}")
            except Exception as e:
                print(f"Error occurred while setting up memory storage directory: {e}")
                raise
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

                rag_tool_registry = {
                    "vector_search_tool" : similar_documents_fetcher,
                    "confluence_fetch_tool":confluence_document_fetcher
                }

                ### Giving the orchestrator agent a toolbox of both MCP and local tools (RAG tools) to manage the orchestration of the other agents
                all_tools = list(self.listed_mcp_tools)    
                ## MCP Tools + vector store tools 
                all_tools.append(similar_documents_fetcher)

                ##Orchestration agent (MCP + vector store tools)
                orchestrator_config  = agent_configuration["orchestrator_agent"]
                agents["orchestration_agent"] = Agent(
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

                ##Adding the tools as a list of functions to the knowledge agent configuration - Cannot directly add the tools as a string
                resolved_knowledge_tools_list = []
                ###Validates the tools listed in the agents.yaml file against the rag_tool_registry and adds them to the resolved_knowledge_tools_list
                for tool_name in knowledge_agent_configuration.get("tools",[]):
                    callable_tool = rag_tool_registry.get(tool_name)
                    if callable_tool is None:
                        raise ValueError(f"Tool not found in the registry: {tool_name}")
                    resolved_knowledge_tools_list.append(callable_tool)
                        
                agents['knowledge_agent'] = Agent(
                    role = knowledge_agent_configuration["role"],
                    goal = knowledge_agent_configuration["goal"],
                    backstory = knowledge_agent_configuration["backstory"],
                    # tools = knowledge_agent_configuration["tools"],
                    instructions = knowledge_agent_configuration["instructions"],
                    context = knowledge_agent_configuration["context"],
                    retrieval_rules = knowledge_agent_configuration["retrieval_rules"],
                    llm = self.llm,
                    tools = resolved_knowledge_tools_list,
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

    ##Declaring the boot_tasks()
    def boot_tasks(self) -> Dict:
        """Loading the tasks yaml file"""
        try:
            task_configuration = self.crew_dir / 'tasks.yaml'
            with open(task_configuration,'r', encoding='utf-8') as f:   
                task_configuration = yaml.safe_load(f)

                tasks = {}
                ##Implement task function from here
                ##Orchestration Task
                orchestrator_task_configuration = task_configuration["task_orchestrate"]
                tasks["task_orchestrate"] = Task(
                    description=orchestrator_task_configuration["description"],
                    agent=self.agents["orchestration_agent"],
                    expected_output = orchestrator_task_configuration["expected_output"],
                    #Check if this is the last output that we want or are we passing this output to any other agent for further processing, if output is final then we can directly return the output to the user from the service layer, if not, then we can pass the output to the next agent for further processing until we get the final output that we want to return to the user
                    # output_json=self.agents['orchestrator_agent']
                )

                #Retrieve knowledge task
                retrieve_knowledge_task_configuration = task_configuration["task_retrieve_knowledge"]
                tasks["task_retrieve_knowledge"] = Task(
                    description=retrieve_knowledge_task_configuration["description"],
                    agent=self.agents["knowledge_agent"],
                    expected_output=retrieve_knowledge_task_configuration["expected_output"],
                )

                #Reason over evidence task
                reasoning_task_configuration = task_configuration["task_reasoning_over_evidence"]
                tasks["task_reasoning_over_evidence"] = Task(
                    description=reasoning_task_configuration["description"],
                    agent=self.agents["reasoning_agent"],
                    expected_output=reasoning_task_configuration["expected_output"],
                )

                #Memory sync task
                memory_sync_task_configuration = task_configuration["task_memory_sync"]
                tasks["task_memory_sync"] = Task(
                    description=memory_sync_task_configuration["description"],
                    agent=self.agents["memory_agent"],
                    expected_output=memory_sync_task_configuration["expected_output"],
                )

                #Response formatting task
                response_formatting_task_configuration = task_configuration["task_format_response"] 
                tasks["task_format_response"] = Task(
                    description=response_formatting_task_configuration["description"],
                    agent=self.agents["response_agent"],
                    expected_output=response_formatting_task_configuration["expected_output"],
                )
                print("Tasks successfully loaded and initialized.")
                return tasks    
        except Exception as e:
            print(f'Error loading task configuration: {e}')
            raise

    ##Initializing the crew instance with the agents and memory, this will be used to execute the tasks assigned by the service layer
    def get_crew_instance(self) -> Crew:
        """Function to intialze the crew instance with the agents and memory, this will be used to execute the tasks assigned by the service layer"""

        try:
            print(f"Setting up the crew instance for the session with memory{self.session_id}")
            memory_configuration = {
                "verbose" : True,
            }
            ###Initialize the memory instance
            if settings.short_term_memory_flag or settings.long_term_memory_flag:
                memory_configuration["memory"] = True
                ##Short-Term Memory instance
                if settings.short_term_memory_flag:
                    memory_configuration["short_term_memory"] = ShortTermMemory()
                    print(f"Short-term memory enabled for the session {self.session_id}")
                ##Long-Term Memory instance
                if settings.long_term_memory_flag:
                    memory_configuration["long_term_memory"] = LongTermMemory()
                    print(f"Long-term memory enabled for the session {self.session_id}")
            ##Fixed returning the crew instance with the agents and the tasks, and the memory configuration - Crew Agents, Tasks, Memory Instance
            crew_instance = Crew(
                agents = [self.agents["orchestration_agent"],
                self.agents["knowledge_agent"],
                self.agents["reasoning_agent"],
                self.agents["memory_agent"],
                self.agents["response_agent"]],

                tasks = [self.tasks["task_orchestrate"], self.tasks["task_retrieve_knowledge"], self.tasks["task_reasoning_over_evidence"], self.tasks["task_memory_sync"], self.tasks["task_format_response"]],
                **memory_configuration
            )
            return crew_instance
        except Exception as e:
            print(f"Error occured while setting up the crew instance: {e}")

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

                