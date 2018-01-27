from celery_config import app

@app.task
def add(a, b):
    return a + b