import os
import uuid
import redis

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

    def create_new_session(self, user_id = None, confluence_user: ConfluenceUserLoginCredentialsModel = None):
        """
        Creates a new session for the user with some user_id and confluence_user details, stores the session data in Redis with a TTL (time to live) and returns the session_id.

        """
        try: 
            ##If user exist then the session_id will be same as the user_id, if user_id is not provided then a new session_id will be generated using uuid4
            session_id = user_id or str(uuid.uuid4())
            session_key = f"confluence_session:{session_id}"
            mappings={"
            }
