from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Zone(models.Model):
    name = models.CharField(max_length=50)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    limit = models.FloatField(default=0)

    def __str__(self):
        return self.name