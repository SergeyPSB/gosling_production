import json
import psycopg2
import os
from utils import logger

# # Connect to your PostgreSQL database
file_name = 'scripts/events.json'

def start_script(conn):
    cursor = conn.cursor()
    
    create_tables(cursor=cursor)
    parse_and_store_json(cursor=cursor)
    logger.info("successfull")
    cursor.close()

def create_tables(cursor):
    # Create the events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name TEXT,
            images TEXT[],
            is_final INTEGER
        )
    ''')

    # Create the actions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY,
            event_id INTEGER REFERENCES events(id),
            description TEXT,
            price INTEGER,
            next_event_id INTEGER
        )
    ''')
    
def parse_and_store_json(cursor):
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            insert(cursor, item['event'])
        
def insert(cursor, event):
    event_id = event['id']
    images_array = process_image_field(event['image'])
    cursor.execute('''
        INSERT INTO events (id, name, images, is_final) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING 
    ''', (event['id'], event['name'], images_array, event['is_final']))
    # Get the id of the inserted event
    # event_id = cursor.fetchone()[0]  
    for action in event['actions']:
        cursor.execute('''
        INSERT INTO actions (id, event_id, description, price, next_event_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING 
        ''', (action['action_id'], event_id, action['description'], action['price'], action['next_event_id']))
        

def process_image_field(image_field):
    if isinstance(image_field, str):
        # If it's a string, convert it to a list with one item
        return [image_field]
    elif isinstance(image_field, list):
        # If it's already a list, return it as is
        return image_field
    else:
        # If it's neither a string nor a list, return an empty list
        return []
