from pydantic import BaseModel
from typing import Dict, Any


TOKEN=""

CHAT_ID="1016719068"

class SystemInfo(BaseModel):
    cpu: Dict[str, Any] = {}
    memory: Dict[str, Any] = {}
    storage: Dict[str, Dict[str, Any]] = {}
    id:str
    os: str
    platform: str
    architecture: str

