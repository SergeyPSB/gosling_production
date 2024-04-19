from typing import List
from dataclasses_json import dataclass_json
from dataclasses import dataclass, asdict
import json


@dataclass
class Event:
    id: int
    description: str
    actions: List['Action']
    is_final: bool = False
    images: List['str'] = [],

    
    def to_json(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "image": [image for image in self.images],
            "is_final": self.is_final,
            "actions": [action.to_json() for action in self.actions]  # Convert actions to JSON
        }
       
@dataclass
class Action:
    id: int
    description: str
    price: int
    next_event_id: int
    
    def isLast(self) -> bool:
        return self.next_event_id is None

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "price": self.price,
            "next_event_id": self.next_event_id,
            "is_finish": self.isLast(),
        }