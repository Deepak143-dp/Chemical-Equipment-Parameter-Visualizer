from django.db import models
class Dataset(models.Model):
    name = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='datasets/')
    row_count = models.IntegerField(default=0)
    checksum = models.CharField(max_length=128, blank=True)
    def __str__(self): return f"{self.name} ({self.upload_time})"
