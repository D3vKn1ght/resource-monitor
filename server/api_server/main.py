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

# SQLAlchemy model for the Agent table
class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    os = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    architecture = Column(String, nullable=False)

# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)

# Dependency to get the SQLAlchemy session
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
        message_string = create_message(info)
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
            send_telegram_message(TOKEN, "1016719068", message_string)
        else:
            print(f"Agent with id {info.id} already exists.")
        
        return {"message": "System info received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", port=80, host='0.0.0.0', reload=True)
