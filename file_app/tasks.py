# your_app/tasks.py
from celery import shared_task
# from celery import Task
from file_manager import celery_app
# from time import sleep
from utils.s3 import upload_file_to_s3

@shared_task
def upload_file_to_s3_task(file, s3_key):
    upload_file_to_s3(file, s3_key)

