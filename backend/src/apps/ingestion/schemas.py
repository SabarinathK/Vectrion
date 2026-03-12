from datetime import datetime

from pydantic import BaseModel, Field


class IngestTextRequest(BaseModel):
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)


class IngestUrlRequest(BaseModel):
    title: str = Field(min_length=1)
    url: str = Field(min_length=5)


class SourceOut(BaseModel):
    id: int
    title: str
    source_type: str
    status: str
    created_at: datetime
