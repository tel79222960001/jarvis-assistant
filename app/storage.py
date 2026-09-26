import sqlite3
import threading
from pathlib import Path

class ConversationStore:
    def __init__(self, db_path: str, max_messages: int = 12):
        self.db_path = db_path
        self.max_messages = max_messages
        self._lock = threading.Lock()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._lock, self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(channel, user_id, id)")
            conn.commit()

    def add(self, channel: str, user_id: str, role: str, content: str):
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO messages(channel, user_id, role, content) VALUES (?, ?, ?, ?)",
                (channel, user_id, role, content),
            )
            conn.execute("""
                DELETE FROM messages
                WHERE id IN (
                    SELECT id FROM messages
                    WHERE channel = ? AND user_id = ?
                    ORDER BY id DESC
                    LIMIT -1 OFFSET ?
                )
            """, (channel, user_id, self.max_messages))
            conn.commit()

    def history(self, channel: str, user_id: str) -> list[dict]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE channel = ? AND user_id = ? ORDER BY id ASC",
                (channel, user_id),
            ).fetchall()
        return [{"role": r, "content": c} for r, c in rows]

    def clear(self, channel: str, user_id: str):
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE channel = ? AND user_id = ?", (channel, user_id))
            conn.commit()
