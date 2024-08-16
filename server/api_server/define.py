from pydantic import BaseModel
from typing import Dict, Any


TOKEN=""

CHAT_ID=""

CPU_TYPE="CPU"
RAM_TYPE="RAM"
STORAGE_TYPE="Storage"

class SystemInfo(BaseModel):
    cpu: Dict[str, Any] = {}
    memory: Dict[str, Any] = {}
    storage: Dict[str, Dict[str, Any]] = {}
    id:str
    os: str
    platform: str
    architecture: str


