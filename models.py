from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


def utcnow() -> datetime:
    """Naive UTC time (works the same on SQLite and Postgres)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    # MFA state (code is stored hashed, single use, short lived)
    mfa_code_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mfa_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    mfa_attempts: Mapped[int] = mapped_column(Integer, default=0)


class User(Base):
    """Same shape as Admin, minus the MFA columns."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    # which admin registered the candidate; becomes NULL if that admin is deleted
    admin_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True
    )


class Vote(Base):
    __tablename__ = "votes"

    vote_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # UNIQUE => one vote per citizen. Nullable + SET NULL so the vote still counts
    # if the voter later deletes their account (NULLs do not collide in a UNIQUE).
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True
    )
    # FK => the database itself rejects votes for candidates that do not exist
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidates.candidate_id"), nullable=False, index=True
    )
