from datetime import datetime

from sqlmodel import Field, SQLModel


class KnowledgeSource(SQLModel, table=True):
    __tablename__ = "knowledge_sources"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    source_type: str
    content: str
    status: str = Field(default="queued", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class KnowledgeChunk(SQLModel, table=True):
    __tablename__ = "knowledge_chunks"

    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="knowledge_sources.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    chunk_index: int
    text: str
