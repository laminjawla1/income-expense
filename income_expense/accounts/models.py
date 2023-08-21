from django.db import models
from django.contrib.auth.models import User
from tracker.models import Company
from PIL import Image
from zone_expense.models import Zone


class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')
    company = models.ManyToManyField(Company, blank=True, related_name="employees")
    title = models.CharField(max_length=50, null=True, blank=True, choices=[
        ("Supervisor", "Supervisor"),
        ("IT", "IT"),
        ("HR", "HR"),
        ("Compliance Officer", "Compliance Officer"),
        ("Accountant", "Accountant"),
        ("Auditor", "Auditor"),
        ("Manager", "Manager"),
        ("CEO", "CEO"),
    ])
    role = models.ManyToManyField(Role, blank=True, related_name="roles")
    zone = models.ForeignKey(Zone, blank=True, null=True, on_delete=models.CASCADE, default="")

    def __str__(self) -> str:
        return f"{self.user.username}'s profile"
    
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        image = Image.open(self.image.path)
        if image.height > 300 or image.width > 300:
            output_size = (300, 300)
            image.thumbnail(output_size)
            image.save(self.image.path)