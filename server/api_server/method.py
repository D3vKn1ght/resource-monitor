from fastapi import HTTPException
from define import SystemInfo
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
