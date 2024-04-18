import psycopg2
from psycopg2 import sql
from database.models import *
from typing import List
from database.test_data import test_events, start_event

# Mock class for testing
class MockDatabase:
    def __init__(self):
        pass

    def move_player(self, session_code, player_id, field_id):
        # Mock method for moving player
        print(f"Moving player {player_id} to field {field_id} in session {session_code}")
        return True
    
    def get_random_problem(self):
        # return random problem
        return start_event.to_json()
        
    def get_event_by_id(self, id: int):
        return test_events[id]

# Database class for interacting with PostgreSQL
class Database:
    def __init__(self):
        self.conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

    def move_player(self, session_code, player_id, field_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE player_movement
                    SET field_id = %s
                    WHERE player_id = %s
                    """,
                    (field_id, player_id)
                )
                self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error moving player: {e}")
            return False