from celery import Celery

from src.common.config import get_settings

settings = get_settings()
celery_app = Celery("rag_worker", broker=settings.redis_url, backend=settings.redis_url)
