"""Adding conversation memory management as history for the session in the confluence service layer, this is temporary until we have a proper memory management system in place"""

from datetime import datetime
from typing import Dict, List, Optional, Any

class ConversationMemory:
    """This class mamages the conversation memory and history for the session, it will be used to store the conversation history and context for the session, and will be used by the agents to retrieve the relevant information for the conversation - will be used in confluence service layer , unitl we implement a proper memory management system"""

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.conversion_history = List[Dict[str, Any]]
        self.maximum_history_length = 10
    
    def add_to_history(self, user_prompt: str, result: Dict[str,Any]):
        """Add the prompt as a histroy dict to the conversation history list"""

        try:
            conversation_entry = {
                ####add the required fields after fixing the schema for the conversation history entry
                "timestamp": datetime.now().isoformat(),
                "user_prompt": user_prompt,
                "intent": result.get("intent"),
                "filters": result.get("filters", {}),
                "confluence_document": result.get("confluence_document", []),
                "output_format": result.get("output_format", {})
            }

            self.conversion_history.append(conversation_entry)

            ##Sliding window approach to maintain conversation history
            if len(self.conversion_history) > self.maximum_history_length:
                ##Remove the oldest entries to maintain the maximum history length
                self.conversion_history = self.conversion_history[-self.maximum_history_length:]
            print(f"Added the conversation entry to the history for the session {self.session_id}")
        except Exception as e:
            print(f"Error occured while adding to conversation history: {e}")
    
    def get_latest_conversation(self) -> Optional[Dict[str,Any]]:
        """Function to retrieve the latest conversation entry from the history, this can be used by the agents to get the context of the conversation"""

        if self.conversion_history:
            return self.conversion_history[-1]
        return None

    def get_latest_data_from_latest_query(self) -> Optional[List[Dict]]:
        """Fetching latest data from the latest conversation query that fetched data"""

        for entry in reversed(self.conversion_history):
            if entry.get("confluence_document"):
                return entry["confluence_document"]
        return None
    
    def get_latest_filters(self) -> Optional[Dict]:
        """Fetching latest filters from the latest conversation query that fetched data"""

        if self.conversion_history:
            return self.conversion_history[-1].get("filters",{})
        return None

    def check_previous_data(self) -> bool:
        """Check if there is any previous data in the conversation history"""

        return self.get_latest_data_from_latest_query() is not None and len(self.get_latest_data_from_latest_query()) > 0


    ###Fuction to get the context and summarize it as conversation context

    def conversation_context_summary(self) -> str:
        """Function to summarize the conversation context from the conversation history, this can be used by the agents to get the context of the conversation"""

        if not self.conversion_history:
            return "No conversation history available for summarization."

        ###Extract the last conversation from the conversation history
        latest_conversation = self.get_latest_conversation()
        if latest_conversation:
            context_summary = f"Latest prompt: {latest_conversation['user_prompt']}\n"
            context_summary += f"Intent: {latest_conversation['intent']}\n"
            ##Have optional metadata for the context summary
            if latest_conversation.get("filters"):
                context_summary += f"Filters: {latest_conversation['filters']}\n"
            if latest_conversation.get("confluence_document"):
                context_summary += f"Data: {len(latest_conversation['confluence_document'])} documents retrieved\n"
            return context_summary
        return "No valid conversation entry found for summarization."

    def clear_conversation_history(self):
        self.conversion_history = []
        print(f"Conversation history cleared for the session {self.session_id}")

_memory_in_store: Dict[str, ConversationMemory] = {}

def get_conversation_memory(session_id: str) -> ConversationMemory:
    """
    Function to get the conversation memory for a given session id, if the conversation memory does not exist for the session id, it will create a new conversation memory and return it
    """

    if session_id not in _memory_in_store:
        _memory_in_store[session_id] = ConversationMemory(session_id)
    return _memory_in_store[session_id]
