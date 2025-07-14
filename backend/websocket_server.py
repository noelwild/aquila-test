"""Simplified Aquila backend using SQLite and WebSocket communication."""

import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .db_sqlite import SQLiteDatabase
from .models.document import UploadedDocument, DataModule
from .models.base import DMTypeEnum, SecurityLevel

logger = logging.getLogger(__name__)

app = FastAPI(title="Aquila S1000D-AI WS API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = SQLiteDatabase()


@app.on_event("startup")
async def startup() -> None:
    await DB.connect()
    if await DB.get_settings() is None:
        await DB.save_settings({"brex_rules": {}})


class WSMessage(BaseModel):
    action: str
    payload: Dict[str, Any] | None = None


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            text = await ws.receive_text()
            try:
                msg = WSMessage.parse_raw(text)
            except Exception as exc:  # pragma: no cover - simple validation
                await ws.send_text(json.dumps({"error": str(exc)}))
                continue
            if msg.action == "get_settings":
                settings = await DB.get_settings()
                await ws.send_text(json.dumps({"action": "settings", "data": settings}))
            elif msg.action == "list_documents":
                docs = await DB.list_documents()
                await ws.send_text(json.dumps({"action": "documents", "data": docs}))
            elif msg.action == "upload_document" and msg.payload:
                content = base64.b64decode(msg.payload.get("content", ""))
                filename = msg.payload.get("filename", "file.bin")
                doc = UploadedDocument(
                    filename=filename,
                    file_path=str(Path(DB.db_path).parent / filename),
                    mime_type="application/octet-stream",
                    file_size=len(content),
                    sha256_hash="",
                )
                await DB.insert_document(doc.id, doc.dict())
                await ws.send_text(json.dumps({"action": "uploaded", "data": doc.dict()}))
            elif msg.action == "list_modules":
                modules = await DB.list_data_modules()
                await ws.send_text(json.dumps({"action": "modules", "data": modules}))
            else:
                await ws.send_text(json.dumps({"error": "unknown action"}))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
