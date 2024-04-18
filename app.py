from fastapi import FastAPI, Request, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.websockets import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect  # Import WebSocketDisconnect
from random import choices
from string import ascii_uppercase, digits
from database.database import *
from typing import Dict
from utils import *
from constants import *
from pydantic import BaseModel
import json
from dataclasses_json import dataclass_json



app = FastAPI()
@dataclass
class Session:
    
    timer: SessionTimer
    current_position: int = 0
    next_event_id: int = -1
    map = generate_map(SIZE_MAP)
    user_id: str = None
    
    def get_time_on_position(self, position:int):
        old_pos = self.current_position
        new_pos = old_pos + position
        self.current_position = new_pos
        field = self.map[new_pos]['time_effect']
        self.timer.add_minutes(field)
        return self.timer.get_timer()
    
    def get_event_id(self):
        event_id = self.next_event_id
        self.next_event_id = -1
        if (event_id == self.next_event_id):
            raise Exception("Your event_id wasn't changed, probably you need to answer before to move")
        return event_id
        

sessions:Dict[str, Session] = {}


use_mock_database = True
if use_mock_database:
    db = MockDatabase()
else:
    db = Database()
# Enable CORS (Cross-Origin Resource Sharing) to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define HTTP endpoints
@app.post('/create_session')
async def create_session():
    session_code = ''.join(choices(ascii_uppercase + digits, k=LENGTH_SESSION_CODE))
    sessions[session_code] = Session(timer = SessionTimer(DEFAULT_TIME_HOURS))
    return JSONResponse(content={"session_code": session_code}, status_code=200)

@app.post('/leave_session')
async def leave_session(request: Request):
    try:
        data = await parse_request_data(request)
        session_code = check_session_code(data)

        if session_code in sessions:
                del sessions[session_code]
                return JSONResponse(content={"success": True}, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="Session code does not exist")
        
    except HTTPException as http_exc:
        return JSONResponse(content={"success": False, "error": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

@app.post('/get_config')
async def get_config(request: Request):
    try:
        data = await parse_request_data(request)
        session_code = check_session_code(data)
        map = generate_map(size = SIZE_MAP)
        event = db.get_random_problem()

        return JSONResponse(
            content={"event": event,"timmer": sessions[session_code].timer.get_timer(), "map": map},
            status_code = 200
        )
    except HTTPException as http_exc:
        return JSONResponse(content={"success": False, "error": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post('/answer')
async def answer(request: Request):
    try:
        data = await parse_request_data(request)
        session_code = check_session_code(data)
        event_id = int(parse_field(data, 'event_id'))
        action_id = int(parse_field(data, 'action_id'))
       
        event = db.get_event_by_id(event_id)
        action = next((action for action in event.actions if action.id == action_id), None)
        if (action is None):
            raise HTTPException(status_code=400, detail="We don't have a such action")
        
        session = sessions[session_code]
        session.next_event_id = action.next_event_id
        timer = session.timer
        timer.add_minutes(action.price)
        
        return JSONResponse(content={"timmer": timer.get_timer(), "is_final": action.isLast()}, status_code=200)
    except HTTPException as http_exc:
        return JSONResponse(content={"success": False, "error": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    
@app.post('/move')
async def move(request: Request):
    try:
        data = await parse_request_data(request)
        session_code = check_session_code(data)
        position = int(parse_field(data, 'position'))

        session = sessions[session_code]
        newTime = session.get_time_on_position(position)
        
        event = db.get_event_by_id(session.get_event_id())
        return JSONResponse(content={"event": event.to_json(), "timmer": newTime}, status_code=200)
    except HTTPException as http_exc:
        return JSONResponse(content={"success": False, "error": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    
def check_session_code(data:dict):
    code = data.get('session_code')
    if code is None:
        raise HTTPException(status_code=400, detail="Session code isn't passed")
    
    if code not in sessions:
        raise HTTPException(status_code=400, detail="Your session hasn't started yet")
    
    return code

def parse_field(data:dict, field:str):
    value = data.get(field)
    if value is None:
        raise HTTPException(status_code=400, detail=f"{field} code isn't passed")
    
    return value
    
async def parse_request_data(request: Request) -> dict:
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        data = await request.json()
    elif content_type == 'application/x-www-form-urlencoded':
        data = await request.form()
    else:
        data = {}

    return data


if __name__ == '__main__':
    sessions["TEST"] = Session(timer=SessionTimer(DEFAULT_TIME_HOURS))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
