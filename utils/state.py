"""
Lightweight in-memory state store for per-user conversation flows.

All state is lost on restart; flows (OAuth, broadcast) re-prompt if the bot
restarts mid-flow, which is acceptable for these short-lived interactions.
"""
from enum import Enum, auto
from typing import Any

from google_auth_oauthlib.flow import Flow


class UserState(Enum):
    IDLE = auto()
    WAITING_OAUTH_CODE = auto()   # Waiting for user to paste OAuth redirect URL
    WAITING_BROADCAST = auto()    # Admin: waiting for message to broadcast


# user_id → current state
user_states: dict[int, UserState] = {}

# user_id → arbitrary data dict for the current flow
user_state_data: dict[int, dict[str, Any]] = {}

# user_id → google_auth_oauthlib Flow object (kept until code is exchanged)
oauth_flows: dict[int, Flow] = {}

# user_ids currently running an upload (prevents concurrent duplicate uploads)
currently_uploading: set[int] = set()
