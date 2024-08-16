from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta

SQLITE_DATABASE_URL = "sqlite:////app//monitoring.db"
engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    os = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    architecture = Column(String, nullable=False)
    
class AlertLog(Base):
    __tablename__ = "alertslog"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, nullable=False)
    type_alert = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(String, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    is_check = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def insert_alert(db, agent_id, type_alert, message):
    new_alert = AlertLog(
        agent_id=agent_id,
        type_alert=type_alert,
        message=message,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")        
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

def check_alert_need_send(db, agent_id, type_alert, delta_time=5*60, threshold_number=3):
    now = datetime.now()
    time_check = now - timedelta(seconds=delta_time)
    alerts = db.query(AlertLog).filter(AlertLog.agent_id == agent_id, AlertLog.type_alert == type_alert, AlertLog.timestamp >= time_check, AlertLog.is_check == 0).all()
    if len(alerts) >= threshold_number:
        for alert in alerts:
            alert.is_check = 1
        db.commit()
        return True
    return False



def delete_alert_over_save(db, delta_time=60*60):
    now = datetime.now()
    time_check = now - timedelta(seconds=delta_time)
    db.query(AlertLog).filter(AlertLog.timestamp < time_check).delete()
    db.commit()
    

