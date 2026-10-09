from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class AdminLoginIn(LoginIn):
    mfa_code: str = Field(pattern=r"^\d{6}$")


class RequestMfaIn(LoginIn):
    pass


class AccountOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class InfoOut(BaseModel):
    payload: dict
    account: AccountOut


class MessageOut(BaseModel):
    message: str


class CandidateIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class CandidateOut(BaseModel):
    candidate_id: int
    name: str
    email: EmailStr
    admin_id: int | None

    model_config = {"from_attributes": True}


class VoteIn(BaseModel):
    candidate_id: int = Field(gt=0)


class VoteOut(BaseModel):
    message: str
    vote_id: int


class VotePublic(BaseModel):
    """A vote as shown publicly. The voter's id is deliberately left out (ballot secrecy)."""

    vote_id: int
    candidate_id: int

    model_config = {"from_attributes": True}


class CandidateResult(BaseModel):
    candidate_id: int
    name: str
    votes: int


class VotesOut(BaseModel):
    total_votes: int
    results: list[CandidateResult]
    votes: list[VotePublic]
