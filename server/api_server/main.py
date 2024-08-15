from fastapi import FastAPI, HTTPException
from define import *
from method import *
import uvicorn

app = FastAPI()

@app.post("/systeminfo/")
async def receive_system_info(info: SystemInfo):
    try:
        print(info)
        message_string = create_message(info)
        # print(message_string)
        send_telegram_message(TOKEN,"1016719068",message_string)
        return {"message": "System info received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", port=80, host='0.0.0.0', reload=True)
