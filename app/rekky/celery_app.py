from celery import Celery

celery_app = Celery("rekky", broker="redis://redis:6379/0")
celery_app.conf.update(
    task_serializer="pickle",
    result_serializer="pickle",
    event_serializer="json",
    accept_content=["application/json", "application/x-python-serialize"],
    result_accept_content=["application/json", "application/x-python-serialize"],
)
celery_app.autodiscover_tasks(["rekky.tasks.items"])
celery_app.autodiscover_tasks(["rekky.tasks.events"])

CELERY_ACCEPT_CONTENT = ["pickle"]
