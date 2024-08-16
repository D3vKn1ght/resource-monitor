from fastapi import HTTPException
import requests
from urllib.parse import quote
from sqlalchemy.orm import Session
from define import *
from db import *

def create_message(info: SystemInfo) -> str:
    try:
        message_string = f"""
Thông tin agent {info.id}:

Thông tin CPU:
- Mô hình: {info.cpu['model']}
- Số lõi: {info.cpu['cores']}
- Sử dụng: {info.cpu['usage_percent']:.2f}%

Thông tin bộ nhớ RAM:
- Tổng dung lượng: {info.memory['total_mb']} MB
- Đã sử dụng: {info.memory['used_mb']} MB
- Còn trống: {info.memory['available_mb']} MB
- Phần trăm sử dụng: {info.memory['usage_percent']:.2f}%

Thông tin lưu trữ:
"""
        for mountpoint, storage_info in info.storage.items():
            message_string += f"""- '{mountpoint}':
  - Tổng dung lượng: {storage_info['total_gb']} GB
  - Đã sử dụng: {storage_info['used_gb']} GB
  - Còn trống: {storage_info['free_gb']} GB
  - Phần trăm sử dụng: {storage_info['usage_percent']:.2f}%
"""

        message_string += f"""
Thông tin hệ điều hành:
- Hệ điều hành: {info.os}
- Nền tảng: {info.platform}
- Kiến trúc: {info.architecture}
"""

        return message_string
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi: {e}")
    
    
def send_telegram_message(token="", chat_id='@detecteven123', message=""):
    # print(f"Sending message to {chat_id} with message: {message}")
    message = quote(message)
    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    response = requests.get(url)
    return response

def check_cpu_usage(cpu_info, threshold=90):
    if cpu_info["usage_percent"] > threshold:
        return True, cpu_info["usage_percent"]
    return False, cpu_info["usage_percent"]

def check_memory_usage(memory_info, threshold=90):
    if memory_info["usage_percent"] > threshold:
        return True, memory_info["usage_percent"]
    return False, memory_info["usage_percent"]

def check_storage_usage(storage_infos, threshold=90):
    list_alert = []
    for mountpoint, storage_info in storage_infos.items():
        if storage_info["usage_percent"] > threshold:
            list_alert.append((mountpoint, storage_info["usage_percent"]))
    if list_alert:
        return True, list_alert
    return False, list_alert

def send_alert(agent_id, message):
    message=f"⚠️Cảnh báo, agent {agent_id} đang sử dụng tài nguyên quá mức\n {message}"
    send_telegram_message(TOKEN , CHAT_ID, message)
    
    
def get_or_create_agent(info: SystemInfo, db: Session):
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
        return new_agent
    else:
        print(f"Agent with id {info.id} already exists.")
        return agent

def process_system_info(info: SystemInfo, db: Session):
    is_alert = False  
    message = ""          
    is_alert_cpu, cpu_message = check_and_handle_cpu_alert(info, db)
    is_alert_memory, memory_message = check_and_handle_memory_alert(info, db)
    is_alert_storage, storage_message = check_and_handle_storage_alert(info, db)

    if is_alert_cpu or is_alert_memory or is_alert_storage:
        is_alert = True
        message += cpu_message + memory_message + storage_message
        
    return message, is_alert

def check_and_handle_cpu_alert(info: SystemInfo, db: Session):
    cpu_info = info.cpu
    is_alert_cpu, cpu_usage = check_cpu_usage(cpu_info)
    message = ""
    if is_alert_cpu:
        print(f"CPU usage is over threshold: {cpu_usage:.2f}%")
        message += f"+ CPU : {cpu_usage:.2f}%\n"
        insert_alert(db, info.id, CPU_TYPE, f"CPU usage is over threshold: {cpu_usage:.2f}%")
        if check_alert_need_send(db, info.id, CPU_TYPE):
            return True, message
    return False, message

def check_and_handle_memory_alert(info: SystemInfo, db: Session):
    memory_info = info.memory
    is_alert_memory, memory_usage = check_memory_usage(memory_info)
    message = ""
    if is_alert_memory:
        print(f"Memory usage is over threshold: {memory_usage:.2f}%")
        message += f"+ RAM : {memory_usage:.2f}%\n"
        insert_alert(db, info.id, RAM_TYPE, f"Memory usage is over threshold: {memory_usage:.2f}%")
        if check_alert_need_send(db, info.id, RAM_TYPE):
            return True, message
    return False, message

def check_and_handle_storage_alert(info: SystemInfo, db: Session):
    storage_infos = info.storage
    is_alert_storage, list_alert_storage = check_storage_usage(storage_infos)
    message = ""
    if is_alert_storage:
        print(f"Storage usage is over threshold")
        message += f"+ Bộ nhớ:\n"
        for mountpoint, storage_usage in list_alert_storage:
            message += f"\t\t\t{mountpoint} : {storage_usage:.2f}%\n"
        insert_alert(db, info.id, STORAGE_TYPE, "Storage usage is over threshold")
        if check_alert_need_send(db, info.id, STORAGE_TYPE):
            return True, message
    return False, message