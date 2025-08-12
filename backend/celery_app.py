import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "drugsreminder",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.timezone = "Europe/Moscow"
celery_app.autodiscover_tasks(["backend"])
