# server.py
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorClient
# import aioredis

app = FastAPI()

# MongoDB setup
mongo = AsyncIOMotorClient("mongodb://localhost:27017")
db = mongo["cookie_checker"]

# Redis setup (cache hoặc Pub/Sub nếu cần)
# redis = aioredis.from_url("redis://localhost")

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        print("Client connected")
        # 1) Gửi yêu cầu lấy cookie
        await ws.send_json({"action": "get_cookies"})

        # 2) Nhận dữ liệu cookie từ extension
        msg = await ws.receive_text()
        print(f"Received message: {msg}")
        payload = json.loads(msg)
        if payload.get("action") == "cookies":
            cookies = payload["data"]

            # 3) Phân tích vi phạm (giả sử sync)
            violations = []
            for c in cookies:
                if "tracking" in c["name"]:
                    violations.append(c)

            # 4) Lưu kết quả vào MongoDB
            await db.violations.insert_one({
                "cookies": cookies,
                "violations": violations,
                "timestamp": asyncio.get_event_loop().time()
            })

            # 5) (Option) cache vào Redis
            # await redis.set("last_violations", json.dumps(violations))

            # 6) Trả kết quả phân tích về extension
            await ws.send_json({"action": "analysis_result", "data": violations})

    except WebSocketDisconnect:
        print("Client disconnected")
