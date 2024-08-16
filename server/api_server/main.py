from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from define import *
from method import *
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLITE_DATABASE_URL  = "sqlite:////app//monitoring.db"
engine = create_engine(SQLITE_DATABASE_URL,connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    os = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    architecture = Column(String, nullable=False)
    

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/getagents/")
async def get_agents():
    db = SessionLocal()
    agents = db.query(Agent).all()
    return agents



@app.post("/systeminfo/")
async def receive_system_info(info: SystemInfo):
    try:
        print(info)
        db = SessionLocal()
        agent = db.query(Agent).filter(Agent.id == info.id).first()
        if not agent:
            print("new agent, monitoring it")
            
            new_agent = Agent(
                id=info.id,
                os=info.os,
                platform=info.platform,
                architecture=info.architecture
            )
            db.add(new_agent)
            db.commit()
            db.refresh(new_agent)
            message_string = create_message(info)
            send_telegram_message(TOKEN, CHAT_ID, message_string)
        else:
            print(f"Agent with id {info.id} already exists.")
            
        is_alert = False  
        message = ""          
        cpu_info = info.cpu
        is_alert_cpu, cpu_usage = check_cpu_usage(cpu_info)
        if is_alert_cpu:
            print(f"CPU usage is over threshold: {cpu_usage:.2f}%")
            is_alert = True
            message += f"+ CPU : {cpu_usage:.2f}%\n"
        
        memory_info = info.memory
        is_alert_memory, memory_usage = check_memory_usage(memory_info)
        if is_alert_memory:
            print(f"Memory usage is over threshold: {memory_usage:.2f}%")
            is_alert = True
            message += f"+ RAM : {memory_usage:.2f}%\n"        
        
        storage_infos = info.storage
        is_alert_storage, list_alert_storage = check_storage_usage(storage_infos)
        if is_alert_storage:
            print(f"Storage usage is over threshold")
            is_alert = True
            message += f"+ Bộ nhớ:\n"
            for mountpoint, storage_usage in list_alert_storage:
                message += f"\t\t\t{mountpoint} : {storage_usage:.2f}%\n"        
        
        if is_alert:
            send_alert(info.id, message)
        
        return {"message": "System info received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", port=80, host='0.0.0.0', reload=True)
