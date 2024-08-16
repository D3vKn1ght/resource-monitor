from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from define import *
from method import *
from db import *

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-agents/")
async def get_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    return agents

@app.post("/send-system-info/")
async def receive_system_info(info: SystemInfo, db: Session = Depends(get_db)):
    try:
        print(info)
        agent = get_or_create_agent(info, db)
        message, is_alert = process_system_info(info, db)
        
        if is_alert:
            send_alert(info.id, message)
        
        delete_alert_over_save(db)
        
        return {"message": "System info received successfully"}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@app.post("/get-alerts/")
async def get_alerts(agent_id: str, db: Session = Depends(get_db)):
    alerts = db.query(AlertLog).filter(AlertLog.agent_id == agent_id).order_by(AlertLog.timestamp.desc()).all()
    return alerts


if __name__ == "__main__":
    uvicorn.run("main:app", port=80, host='0.0.0.0', reload=True)