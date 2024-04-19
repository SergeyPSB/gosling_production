import psycopg2
from database.models import *
from typing import List
from database.test_data import test_events, start_event
from collections import defaultdict
import os

# Mock class for testing
class MockDatabaseManager:
    def __init__(self):
        pass

    def move_player(self, session_code, player_id, field_id):
        # Mock method for moving player
        print(f"Moving player {player_id} to field {field_id} in session {session_code}")
        return True
    
    def get_start_problem(self):
        # return random problem
        return start_event.to_json()
        
    def get_event_by_id(self, id: int):
        return test_events[id]

# Database class for interacting with PostgreSQL
class DatabaseManager:
    def __init__(self, connection):
        self.conn = connection

    def move_player(self, session_code, player_id, field_id):
        pass
        # try:
        #     with self.conn.cursor() as cursor:
        #         cursor.execute(
        #             """
        #             UPDATE player_movement
        #             SET field_id = %s
        #             WHERE player_id = %s
        #             """,
        #             (field_id, player_id)
        #         )
        #         self.conn.commit()
        #     return True
        # except psycopg2.Error as e:
        #     print(f"Error moving player: {e}")
        #     return False
        
        
    def get_start_problem(self):
        # return random problem
        return self.get_event_by_id(id=1000)
        
    def get_event_by_id(self, id: int):
        query = """
            SELECT events.id AS event_id, events.name AS event_name, events.images as event_images, events.is_final as event_is_final,
            actions.id AS action_id, actions.description AS action_description, actions.price AS action_price, actions.next_event_id as action_next_event_id
            FROM events JOIN actions ON events.id = actions.event_id
            WHERE events.id = %s;
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (id,))
        rows = cursor.fetchall()

        event_actions = defaultdict(list)
        for row in rows:
            event_id = row[0]  # Index 0 corresponds to the event_id field
            event_name = row[1]  # Index 1 corresponds to the event_name field
            event_image = row[2]  # Index 1 corresponds to the event_name field
            event_is_final = row[3]
            action_id = row[4]  # Index 2 corresponds to the action_id field
            action_description = row[5]  # Index 3 corresponds to the action_description field
            action_price = row[6]
            action_next_event_id = row[7]
            # Create ActionDTO object
            action_dto = Action(id=action_id, description=action_description, price = action_price, next_event_id=action_next_event_id)
            
            # Check if the event already exists in the defaultdict
            if event_id in event_actions:
                # Append the action to the existing list of actions for this event
                event_actions[event_id].actions.append(action_dto)
            else:
                # Create a new EventDTO with the current action for this event
                event_dto = Event(id=event_id, description=event_name, actions=[action_dto], is_final=event_is_final, images=event_image)
                event_actions[event_id] = event_dto
        return event_actions[event_id]