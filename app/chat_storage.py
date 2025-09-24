# chat_storage.py

import os
import json
import time
import uuid
from typing import List, Dict, Optional

CHAT_HISTORY_DIR = "./chat_histories"


def _ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def _sanitize_segment(segment: str) -> str:
    # Replace characters that are problematic on filesystems (Windows-safe)
    safe = []
    for ch in segment:
        if ch.isalnum() or ch in ("_", "-", "."):
            safe.append(ch)
        else:
            safe.append("_")
    return "".join(safe)[:128]


def _legacy_history_file_path(user_id: str, collection_name: str) -> str:
    _ensure_dir(CHAT_HISTORY_DIR)
    filename = f"{_sanitize_segment(user_id)}__{_sanitize_segment(collection_name)}.json"
    return os.path.join(CHAT_HISTORY_DIR, filename)


def _chat_dir(user_id: str, collection_name: str) -> str:
    user = _sanitize_segment(user_id or "anonymous")
    coll = _sanitize_segment(collection_name or "default")
    path = os.path.join(CHAT_HISTORY_DIR, f"{user}__{coll}")
    _ensure_dir(path)
    return path


# --- Legacy single-chat helpers (kept for backward compatibility) ---

def load_chat_history(user_id: str, collection_name: str) -> List[Dict]:
    """Legacy: returns a single chat history list if present (pre-multi-chat)."""
    path = _legacy_history_file_path(user_id or "anonymous", collection_name or "default")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_chat_history(user_id: str, collection_name: str, messages: List[Dict]) -> None:
    """Legacy: saves a single chat history list (pre-multi-chat)."""
    path = _legacy_history_file_path(user_id or "anonymous", collection_name or "default")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(messages or [], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def delete_chat_history(user_id: str, collection_name: str) -> None:
    """Legacy: deletes the single chat history file (pre-multi-chat)."""
    path = _legacy_history_file_path(user_id or "anonymous", collection_name or "default")
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# --- Multi-chat helpers ---

def list_chats(user_id: str, collection_name: str) -> List[Dict]:
    """Return a list of chats metadata for a user+collection, newest first."""
    base = _chat_dir(user_id, collection_name)
    items: List[Dict] = []
    try:
        for fname in os.listdir(base):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(base, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    items.append({
                        "chat_id": data.get("chat_id") or os.path.splitext(fname)[0],
                        "title": data.get("title") or data.get("created_at") or os.path.splitext(fname)[0],
                        "created_at": data.get("created_at") or "",
                        "updated_at": data.get("updated_at") or "",
                    })
            except Exception:
                continue
    except Exception:
        return []
    # Sort by updated_at desc, fallback to filename order
    items.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return items


def _chat_file_path(user_id: str, collection_name: str, chat_id: str) -> str:
    base = _chat_dir(user_id, collection_name)
    return os.path.join(base, f"{_sanitize_segment(chat_id)}.json")


def create_chat(user_id: str, collection_name: str, title: Optional[str] = None) -> str:
    chat_id = str(uuid.uuid4())
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    record = {
        "chat_id": chat_id,
        "title": title or f"Chat {now}",
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }
    path = _chat_file_path(user_id, collection_name, chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return chat_id


def load_chat_messages(user_id: str, collection_name: str, chat_id: str) -> List[Dict]:
    path = _chat_file_path(user_id, collection_name, chat_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        msgs = data.get("messages", [])
        if isinstance(msgs, list):
            return msgs
    except Exception:
        pass
    return []


def save_chat_messages(user_id: str, collection_name: str, chat_id: str, messages: List[Dict]) -> None:
    path = _chat_file_path(user_id, collection_name, chat_id)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"chat_id": chat_id, "messages": []}
        data["messages"] = messages or []
        data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if "title" not in data:
            data["title"] = f"Chat {data['updated_at']}"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def rename_chat(user_id: str, collection_name: str, chat_id: str, new_title: str) -> None:
    path = _chat_file_path(user_id, collection_name, chat_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["title"] = new_title
        data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def delete_chat_by_id(user_id: str, collection_name: str, chat_id: str) -> None:
    path = _chat_file_path(user_id, collection_name, chat_id)
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass 