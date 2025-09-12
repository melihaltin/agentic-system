from typing import Dict, Any
import json
from datetime import datetime


class StateManager:
    def __init__(self):
        self.states: Dict[str, Any] = {}

    def save_state(self, session_id: str, state: Dict[str, Any]):
        """Session state'ini kaydet"""
        self.states[session_id] = {
            "state": state,
            "timestamp": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    def get_state(self, session_id: str) -> Dict[str, Any]:
        """Session state'ini getir"""
        return self.states.get(session_id, {})

    def clear_state(self, session_id: str):
        """Session state'ini temizle"""
        if session_id in self.states:
            del self.states[session_id]
