"""
Service layer for confluence integration in the CortexSail Agentic RAG System
"""

from src.configuration import settings
from src.crew.crewmanager import CrewManager
from typing import Dict, List
from src.memory.conversation_memory import get_conversation_memory


class ConfluenceService:

    """Service layer for handling interactions with Confluence API"""

    def __init__(self):
        ##crew_manager - Workspace brain holds the context and state for the current workspace, including Confluence credentials and session management - its for a single conversation or session
        self.crew_manager = None
        self.current_session_id = None
        self.conversation_memory = None
    
    def user_prompt(self, query: str) -> Dict:
        """Analyse user query and determine if it requires Confluence interaction, then route to appropriate agent or tool"""

        try:
            print(f"Extract the confluence credentials from the session")

            ###Fix this on actual session management implementation with auth services and session handling
            session_id = "default session"

            if self.crew_manager is None or self.current_session_id != session_id:

            ##if session not there and crew manager not initialized, initialize its object and the condition to check if the session has changed, if so, reinitialize the crew manager for the new session
                print (f"Initialize the cew manager for the session {session_id}")

                self.crew_manager = CrewManager(session_id=session_id)

                self.current_session_id = session_id

            ###Initializing the conversaion memory for the session - this is temporary until we have a proper session management and memory management in place

            if self.conversation_memory is None:
                print(f"Creating conversation memory for the session {session_id}")

                self.conversation_memory = get_conversation_memory(session_id)

            ###Fetching the conversation summary for the session from the conversation memory, this can be used to provide context to the agents for the conversation - latest conversation entry

            last_conversation = self.conversation_memory.get_latest_data_from_latest_query()

            #Fetching filters also
            conversation_filter = self.conversation_memory.get_latest_filters()

            print(f"Fetched previous data: {len(last_conversation) if last_conversation else 0}")

            ###Initializing the crew instance
            crew_instance = self.crew_manager.get_crew_instance()

            ##Collecting the context and routing to crew instance , LLM will determine the next steps and the tools to use based on the query, conversation history and filters 

            crew_inputs_llm = {
                "prompt": query,
                "previous_conversation":
                last_conversation if last_conversation else [],
                "previous_filters": conversation_filter if conversation_filter else {}
            }

            result = crew_instance.kickoff(input = crew_inputs_llm)

            ##Extracting the response
            if hasattr(result, "raw"):
                output_text = result.raw
            elif isinstance(result, dict) and "raw" in result:
                output_text = result["raw"]
            else:
                output_text = str(result)

            ##If no data is returned, 
            no_data_response = [
                "No relevant documents found",
                "No relevant information found",
                "No relevant data found",
                "No relevant results found",
                "No relevant content found",
                "No data found",
                "No information found",
                "No results found",
                "No content found",
                "could not find any relevant information",
                "could not find any relevant documents",
                "could not find any relevant data",
            ]

            if output_text.strip() == "" or any(phrase in output_text.lower() for phrase in no_data_response):
                return {
                    "success": False,
                    "output": "",
                    "message": "No relevant documents found matching your criteria"
                }
            print(f"Document retrieval successful, returning response to user")

            ##Storing this reponse in the conversation memory for the session, this can be used to provide context to the agents for the conversation
            try:
                result_data = {
                    "intent": getattr(result, "intent","analysis"),
                    "filters": crew_inputs_llm.get("previous_filters",{}),
                    "confluence_document": getattr(result, "confluence_document", []),
                    "output_format": getattr(result, "output_format", {"text": output_text}),
                }   