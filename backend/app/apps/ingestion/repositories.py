from sqlmodel import Session, delete, select

from app.apps.ingestion.models import KnowledgeChunk, KnowledgeSource


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, source: KnowledgeSource) -> KnowledgeSource:
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_by_id(self, source_id: int) -> KnowledgeSource | None:
        return self.db.exec(select(KnowledgeSource).where(KnowledgeSource.id == source_id)).first()

    def list_by_user(self, user_id: int) -> list[KnowledgeSource]:
        return list(
            self.db.exec(
                select(KnowledgeSource)
                .where(KnowledgeSource.user_id == user_id)
                .order_by(KnowledgeSource.created_at.desc())
            ).all()
        )

    def update(self, source: KnowledgeSource) -> KnowledgeSource:
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def delete(self, source: KnowledgeSource) -> None:
        self.db.exec(delete(KnowledgeChunk).where(KnowledgeChunk.source_id == source.id))
        self.db.delete(source)
        self.db.commit()


class ChunkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def bulk_create(self, chunks: list[KnowledgeChunk]) -> None:
        self.db.add_all(chunks)
        self.db.commit()
