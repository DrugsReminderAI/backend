from celery import Celery

celery_app = Celery(
    "drugsreminder",
    broker="redis://localhost:6379/0",  # Redis как брокер
    backend="redis://localhost:6379/0",  # (опционально) хранить результаты
)

celery_app.conf.timezone = "Europe/Moscow"
