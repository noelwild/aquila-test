import json
from pathlib import Path
from typing import Any, List, Dict

import aiosqlite

DB_PATH = Path(__file__).parent / "aquila.db"


class SQLiteDatabase:
    """Simple async wrapper around SQLite for Aquila."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL
            )
            """
        )
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
            """
        )
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS data_modules (
                dmc TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
            """
        )
        await self.conn.commit()

    async def get_settings(self) -> Dict[str, Any] | None:
        async with self.conn.execute("SELECT data FROM settings WHERE id=1") as cur:
            row = await cur.fetchone()
            if row:
                return json.loads(row[0])
        return None

    async def save_settings(self, data: Dict[str, Any]) -> None:
        payload = json.dumps(data)
        await self.conn.execute(
            "INSERT OR REPLACE INTO settings(id, data) VALUES(1, ?)",
            (payload,),
        )
        await self.conn.commit()

    async def insert_document(self, doc_id: str, data: Dict[str, Any]) -> None:
        await self.conn.execute(
            "INSERT OR REPLACE INTO documents(id, data) VALUES(?, ?)",
            (doc_id, json.dumps(data)),
        )
        await self.conn.commit()

    async def list_documents(self) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        async with self.conn.execute("SELECT data FROM documents") as cur:
            async for row in cur:
                docs.append(json.loads(row[0]))
        return docs

    async def insert_data_module(self, dmc: str, data: Dict[str, Any]) -> None:
        await self.conn.execute(
            "INSERT OR REPLACE INTO data_modules(dmc, data) VALUES(?, ?)",
            (dmc, json.dumps(data)),
        )
        await self.conn.commit()

    async def list_data_modules(self) -> List[Dict[str, Any]]:
        modules: List[Dict[str, Any]] = []
        async with self.conn.execute("SELECT data FROM data_modules") as cur:
            async for row in cur:
                modules.append(json.loads(row[0]))
        return modules
