from django.db import models

# Create your models here.
class Mail(models.Model):
    from_email = models.EmailField()
    to_email = models.EmailField()
    subject = models.TextField()
    message = models.TextField()
    received_at = models.DateTimeField()
    message_id = models.TextField()
