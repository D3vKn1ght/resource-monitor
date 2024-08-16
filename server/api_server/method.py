from fastapi import HTTPException
from define import *
import requests
from urllib.parse import quote

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