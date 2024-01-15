from django.db import models
import uuid
from django.contrib.auth.models import User


# Create your models here.


class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to the built-in User model
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField()
