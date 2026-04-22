from pydantic import BaseModel, field_validator
from typing import Optional, List

class EventCreate(BaseModel):
    user_id: str
    occurred_at: str
    kind: str
    tags: Optional[List[str]] = None
    payload: Optional[dict] = None
    
    @field_validator("user_id")
    def validate_user_id(cls, v):
        if not (1 <= len(v) <= 64 and all(c.isalnum() or c=='_' for c in v)):
            raise ValueError("Invalid user_id")
        return v
    
    @field_validator("kind")
    def validate_kind(cls, v):
        if v not in ["click", "purchase", "view", "signup", "custom"]:
            raise ValueError("Invalid kind")
        return v
    
    @field_validator("tags")
    def validate_tags(cls, v):
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("tags must be a list of strings")
            if len(v) == 0:
                raise ValueError("Empty tags are not allowed")
            if len(v) > 16:
                raise ValueError("Maximum 16 tags allowed")
            for tag in v:
                if not isinstance(tag, str) or not (1<= len(tag) <= 32):
                    raise ValueError("Tag length 1-32 charactesr")
                if not all(c in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in tag):
                    raise ValueError("Invalid tag characters")
                if len(set(v)) != len(v):
                    raise ValueError("Duplicate tags are not allowed")
                return v


class EventResponse(BaseModel):
    id: int
    user_id: str
    occurred_at: str
    recorded_at: str
    kind: str
    tags: Optional[List[str]] = None
    payload: Optional[dict] = None