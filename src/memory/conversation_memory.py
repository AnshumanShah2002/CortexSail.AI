"""Adding conversation memory management as history for the session in the confluence service layer, this is temporary until we have a proper memory management system in place"""

from datetime import datetime
from typing import Dict, List, Optional, Any

class ConversationMemory:
    """This class mamages the conversation memoery and history for the session, it will be used to store the conversation history and context for the session, and will be used by the agents to retrieve the relevant information for the conversation - will be used in confluence service layer , unitl we implement a proper memory management system"""

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.conversion_history = List[Dict[str, Any]]
        self.maximum_history_length = 10
    
    def add_to_history(self, user_prompt: str, result: Dict[str,Any]):
        """Add the prompt as a histroy dict to the conversation history list"""

        try:
            conversation_entry = {
                ####add the required fields after fixing the schema for the conversation history entry
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
            

