import logging
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChannelPrivate
from config import FORCE_JOIN_CHANNELS

logger = logging.getLogger(__name__)

_JOINED = {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}


async def get_unjoined_channels(client: Client, user_id: int) -> list[str]:
    """
    Returns the subset of FORCE_JOIN_CHANNELS the user has not joined.
    Channels that cannot be checked (private/inaccessible) are treated as unjoined.
    """
    unjoined: list[str] = []
    for channel in FORCE_JOIN_CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in _JOINED:
                unjoined.append(channel)
        except UserNotParticipant:
            unjoined.append(channel)
        except (ChatAdminRequired, ChannelPrivate):
            logger.warning("Cannot check membership for %s — bot may not be an admin", channel)
        except Exception as exc:
            logger.error("Force-join check failed for %s: %s", channel, exc)
            unjoined.append(channel)
    return unjoined
