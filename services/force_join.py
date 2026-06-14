import logging
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChannelPrivate

logger = logging.getLogger(__name__)

_JOINED = {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}


async def get_force_join_channels(session) -> list[str]:
    from database.models import BotSetting
    setting = await session.get(BotSetting, "force_join_channels")
    if setting and setting.value.strip():
        return [ch.strip() for ch in setting.value.split(",") if ch.strip()]
    from config import FORCE_JOIN_CHANNELS
    return [ch for ch in FORCE_JOIN_CHANNELS if ch]


async def get_unjoined_channels(client: Client, user_id: int) -> list[str]:
    from database.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        channels = await get_force_join_channels(session)

    unjoined: list[str] = []
    for channel in channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in _JOINED:
                unjoined.append(channel)
        except UserNotParticipant:
            # User is definitely not a member
            unjoined.append(channel)
        except (ChatAdminRequired, ChannelPrivate):
            # Bot is not admin / channel is private and bot has no access.
            # Safe default: treat as unjoined so the user sees the join button.
            # Fix: add the bot as an admin (or at least a member) of the channel.
            logger.warning(
                "Cannot check membership for %s — bot must be a member or admin of this channel.",
                channel,
            )
            unjoined.append(channel)
        except Exception as exc:
            logger.error("Force-join check failed for %s: %s", channel, exc)
            # On any unexpected error, assume not joined (safe default)
            unjoined.append(channel)
    return unjoined
