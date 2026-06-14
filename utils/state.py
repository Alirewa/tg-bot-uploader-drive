from enum import Enum, auto
from typing import Any

from google_auth_oauthlib.flow import Flow


class UserState(Enum):
    IDLE = auto()
    WAITING_OAUTH_CODE = auto()
    WAITING_BROADCAST = auto()
    PENDING_DRIVE_SELECTION = auto()
    PENDING_DEST_SELECTION = auto()
    WAITING_USER_ID = auto()
    WAITING_CHANNEL_ADD = auto()
    WAITING_DRIVE_LINK = auto()
    WAITING_AUTO_MSG = auto()
    PENDING_YT_QUALITY = auto()


user_states: dict[int, UserState] = {}
user_state_data: dict[int, dict[str, Any]] = {}
oauth_flows: dict[int, Flow] = {}
currently_uploading: set[int] = set()
pending_uploads: dict[int, Any] = {}
# user_id → timestamp of last upload request (for cooldown enforcement)
upload_cooldowns: dict[int, float] = {}
# user_id → timestamp of last button press (3-second anti-spam)
btn_cooldowns: dict[int, float] = {}
