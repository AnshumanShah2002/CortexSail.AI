import datetime
import os
import uuid
import redis
import json

from src.model.models import ConfluenceUserLoginCredentialsModel

class ConfluenceSessionManager:
    #1 Hour TTL
    def __init__(self, host=None, port = None, db=None, ttl = 3600):
        """
        Redis session manager for managing the user sessions for the Confluence login and session management.
        """
        redis_host = host or os.getenv("REDIS_HOST", "localhost")
        redis_port = port or int(os.getenv("REDIS_PORT", '6379'))
        redis_db = db or int(os.getenv("REDIS_DB", '0'))
        
        #creating a connection object for the redis client using the redis host, port and db from the environment variables or the default values - StrictRedis class
        self.redis = redis.StrictRedis(host = redis_host, port = redis_port, db = redis_db, decode_responses = True)
        self.ttl = ttl
    
    ##Function to create a new session for the user with some user_id
    #Returns a session_id on successful creation of the session
    def create_new_session(self, user_id = None, confluence_user: ConfluenceUserLoginCredentialsModel = None):
        """
        Creates a new session for the user with some user_id and confluence_user details, stores the session data in Redis with a TTL (time to live) and returns the session_id.

        """
        try: 
            ##If user exist then the session_id will be same as the user_id, if user_id is not provided then a new session_id will be generated using uuid4
            session_id = user_id or str(uuid.uuid4())
            session_key = f"confluence_session:{session_id}"

            ##also passing other detials for the session data
            mappings = {
                "session_creation_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "confluence_user": confluence_user.confluence_username if confluence_user else "",
                "confluence_password": confluence_user.confluence_password if confluence_user else "",
                "confluence_url": confluence_user.confluence_url if confluence_user else "",
                "last_query" : "",
                "last_intent": "",
                "last_cql": "",
                "last_response": "[]"
            }

            ##Storing in Redis hset - hset(): one key can store multiple values and hgetall() to get all the values under that key
            self.redis.hset(session_key, mapping = mappings)
            self.redis.expire(session_key, self.ttl)
            print(f"Session created with {session_id} and {mappings}")
            return session_id
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            raise
    def save_dynamic_state(self, session_id, query = None, intent = None, cql = None, response = None):
        """Saves the dynamic state of the session for the given session_id, this includes the last query, last intent, last cql and last response
        """
        try:
            session_key = f"confluence_session:{session_id}"
            update = {}

            if query is not None:
                update["last_query"] = query
            if intent is not None:
                update["last_intent"] = intent
            if cql is not None:
                update["last_cql"] = cql
            if response is not None:
                update["last_response"] = response
            ##if update {} has something then that is to be updated in the redis session store for the given session_id
            if update:
                self.redis.hset(session_key, mapping = update)
            print(f"Session updated with the following dynamic state for session_id {session_id} : {update}")
        except Exception as e:
            print(f"Error updating session: {str(e)}")
            raise
    def get_session_data(self, session_id):
        """
        Retrieve the entire session data with the session_id
        """
        try:
            session_key = f"confluence_session:{session_id}"

            session_data = self.redis.hgetall(session_key)
            if not session_data:
                print(f"No session data found for session_id: {session_id}")
                return None
            return session_data
        except Exception as e:
            print(f"Error retrieving session data: {str(e)}")
            return None
        ##Function to add the history to the session
    def add_history_to_session(self,session_id,role, manage):
        """
        Append the chat history to the existing session"""
        try:
            key = f"confluence_session:{session_id}:history"

            entry = json.dumps({"role": role, "manage":manage, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})

            ##pushing in the redis list - rpush as we need proper sequence of history
            self.redis.rpush(key, entry)
            self.redis.expire(key, self.ttl)
            print(f"Added history to session {session_id} : {entry}")
        except Exception as e:
            print(f"Error adding history to session: {str(e)}")
            raise