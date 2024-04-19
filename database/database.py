import psycopg2
import os
from database.database_manager import MockDatabaseManager, DatabaseManager

class Database:
    def __init__(self, use_mock_database = False):
        self.connection = psycopg2.connect(
            os.getenv("DATABASE_URL")
        )
        if use_mock_database:
            self.manager = MockDatabaseManager()
        else:
            self.manager = DatabaseManager(self.connection)
        

            
  
        