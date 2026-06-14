from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, ForeignKey,
    Integer, String, Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), default="")
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_banned = Column(Boolean, default=False)
    language = Column(String(5), nullable=True, default=None)
    oauth_access_token = Column(Text, nullable=True)
    oauth_refresh_token = Column(Text, nullable=True)
    oauth_token_expiry = Column(DateTime, nullable=True)
    has_personal_drive = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    upload_limit_exempt = Column(Boolean, default=False)
    referral_unlocked = Column(Boolean, default=False)
    referred_by_id = Column(BigInteger, nullable=True)
    daily_upload_bytes = Column(BigInteger, default=0)
    daily_upload_count = Column(Integer, default=0)
    daily_reset_date = Column(String(10), nullable=True)

    uploads = relationship("Upload", back_populates="user", lazy="select")
    rate_limit = relationship("RateLimit", back_populates="user", uselist=False, lazy="select")


class ServiceAccount(Base):
    __tablename__ = "service_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    storage_used_bytes = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    uploads = relationship("Upload", back_populates="service_account", lazy="select")


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    service_account_id = Column(Integer, ForeignKey("service_accounts.id"), nullable=True)
    gdrive_file_id = Column(String(500), nullable=False)
    file_name = Column(String(1000), nullable=False)
    file_size_bytes = Column(BigInteger, default=0)
    share_link = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_personal_drive = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="uploads")
    service_account = relationship("ServiceAccount", back_populates="uploads")


class RateLimit(Base):
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)
    upload_count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rate_limit")


class BotSetting(Base):
    __tablename__ = "bot_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, default="")
