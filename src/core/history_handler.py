"""
Conversation history handler — persists sessions to a flat JSON file.
Each session = { id, title, date, messages: [{role, content, timestamp}] }
"""

import json
import os
import uuid
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "data", "conversation_history.json")


def _ensure_file():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_all() -> list:
    """Return all sessions, newest first."""
    _ensure_file()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data, key=lambda s: s.get("date", ""), reverse=True)
    except Exception:
        return []


def _save_all(sessions: list):
    _ensure_file()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def new_session(title: str = None) -> dict:
    """Create and persist a new empty session."""
    session = {
        "id": str(uuid.uuid4()),
        "title": title or f"Session {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "date": datetime.now().isoformat(),
        "messages": []
    }
    sessions = load_all()
    sessions.insert(0, session)
    _save_all(sessions)
    return session


def append_message(session_id: str, role: str, content: str):
    """Append a message to an existing session and persist."""
    sessions = load_all()
    for s in sessions:
        if s["id"] == session_id:
            s["messages"].append({
                "role": role,          # "user" or "assistant"
                "content": content,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            # Auto-update title from first user message
            if role == "user" and s["title"].startswith("Session "):
                s["title"] = content[:50] + ("…" if len(content) > 50 else "")
            break
    _save_all(sessions)


def delete_session(session_id: str):
    sessions = [s for s in load_all() if s["id"] != session_id]
    _save_all(sessions)


def get_session(session_id: str) -> dict | None:
    for s in load_all():
        if s["id"] == session_id:
            return s
    return None
