from fastapi import FastAPI, Request, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from random import choices
from string import ascii_uppercase, digits
from typing import Dict
from utils import *
from constants import *
from pydantic import BaseModel
from scripts.db_creator import start_script
from database.database import Database
from dataclasses import dataclass
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError



app = FastAPI()

@dataclass
class Session:
    
    timer: SessionTimer
    current_position: int = 0
    next_event_id: int = -1
    map = generate_map(SIZE_MAP)
    user_id: str = None
    
    def change_time(self, price) -> str:
        self.timer.add_minutes(price)
        return self.timer.get_timer()
    
    def get_new_field(self, position: int):
        new_pos = self.current_position + position
        self.current_position = new_pos
        return self.map[new_pos]
        
    
    # def get_event_id(self):
    #     event_id = self.next_event_id
    #     self.next_event_id = -1
    #     if (event_id == self.next_event_id):
    #         raise HTTPException(status_code=400, detail="Your event_id wasn't changed, probably you need to answer before to move")
    #     return event_id
        

sessions:Dict[str, Session] = {}
db: Database = None


# Enable CORS (Cross-Origin Resource Sharing) to allow requests from any origin


# Define HTTP endpoints
@app.post('/create_session', response_model_exclude_unset=True)
async def create_session():
    """
    Запрос на создание новой игровой сессии
    
    Обязательные параметры отсутствуют
    
    Возращает:
    session_code - integer;
    """
    session_code = ''.join(choices(ascii_uppercase + digits, k=LENGTH_SESSION_CODE))
    sessions[session_code] = Session(timer = SessionTimer(DEFAULT_TIME_HOURS))
    return JSONResponse(content={"session_code": session_code}, status_code=200)

@app.post('/leave_session', response_model_exclude_unset=True)
async def leave_session(request: Request):
    """
    Запрос на выход из игровой сессии
    
    Обязательные параметры:
    session_code - integer;
    """
    data = await parse_request_data(request)
    session_code = check_session_code(data)
    if session_code in sessions:
        del sessions[session_code]
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        raise HTTPException(status_code=400, detail="Session code does not exist")
        
        

@app.post('/get_config', response_model_exclude_unset=True)
async def get_config(request: Request):
    """
    Запрос необходимый для начала игры, возращает стартовое событие, стартовое время и карту
    
    Обязательные параметры:
    session_code - integer;
    
    Возвращает:
    event - стартовое событие;
    timmer - стартовое время;
    map - список ячеек с типом эффектов и ценой по времени;
    """
    data = await parse_request_data(request)
    session_code = check_session_code(data)
    map = generate_map(size = SIZE_MAP)
    event = db.manager.get_start_problem()

    return JSONResponse(
        content={"event": event.to_json(), "timmer": sessions[session_code].timer.get_timer(), "map": map},
        status_code = 200
    )


@app.post('/answer', response_model_exclude_unset=True)
async def answer(request: Request):
    """
    Запрос для синхранизации ответа и получение информации о следующем событии
    
    Обязательные параметры:
    session_code - integer;
    event_id - integer;
    action_id - integer;
    
    Возвращает:
    next_event_id - следующее новое событие;
    is_final - финальное ли было событие;
    new_time - время, которое посчиталось ответа;
    """
    data = await parse_request_data(request)
    session_code = check_session_code(data)
    event_id = int(parse_field(data, 'event_id'))
    action_id = int(parse_field(data, 'action_id'))
       
    event = db.manager.get_event_by_id(event_id)
    action = next((action for action in event.actions if action.id == action_id), None)
    if (action is None):
        raise HTTPException(status_code=400, detail="We don't have a such action")
        
    session = sessions[session_code]
    # session.next_event_id = action.next_event_id
    new_time = session.change_time(action.price)
        
    return JSONResponse(content={"next_event_id": action.next_event_id, "is_final": event.is_final, "new_time": new_time}, status_code=200)
    
@app.post('/move')
async def move(request: Request):
    """
    Запрос отправляется после броска кубика, для того чтобы узнать эффект ячейки, на которую встанет и новое событие
    
    Обязательные параметры:
    session_code - integer;
    next_event_id - integer;
    position - integer;
    
    Возвращает:
    event - новое событие;
    field - ячейку, на которую перешел пользователь;
    new_time - время, которое посчиталось после перехода;
    """
    data = await parse_request_data(request)
    session_code = check_session_code(data)
    next_event_id = int(parse_field(data, 'next_event_id'))
    position = int(parse_field(data, 'position'))
    session = sessions[session_code]
    # newTime = session.get_time_on_position(position)
    field = session.get_new_field(position=position)
    type = field["type"]
    
    if (type == 'positive'):
        field["description"] = "Захардкоженный позитивный текст!"
    elif (type == 'negative'):
        field["description"] = "Захардкоженный негативный текст!"
    else:
        field["description"] = ""
    new_time = session.change_time(field['price'])
    event = db.manager.get_event_by_id(next_event_id)
    # event = db.manager.get_event_by_id(session.get_event_id())
    return JSONResponse(content={"event": event.to_json(), "field": field, "new_time": new_time}, status_code=200)

    
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

# Custom exception handler
async def custom_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(content={"success": False, "error": exc.detail}, status_code=exc.status_code)
    elif isinstance(exc, (ValidationError, RequestValidationError)):
        return JSONResponse(content={"success": False, "error": "Validation error"}, status_code=422)
    else:
        logging.exception("An error occurred while processing the request.")
        return JSONResponse(content={"success": False, "error": "Internal server error"}, status_code=500)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(Exception, custom_exception_handler)


if __name__ == '__main__':
    db = Database()
    start_script(db.connection)
    sessions["TEST"] = Session(timer=SessionTimer(DEFAULT_TIME_HOURS))
    logger.info("successfull 2")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
