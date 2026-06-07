import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_configs.settings")

app = Celery("resume_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_extended=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    timezone="UTC",
    enable_utc=True,
)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")