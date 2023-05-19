from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')
    company= models.CharField(max_length=100, choices=[
        ("Yonna Foreign Exchange Bureau", "Yonna Foreign Exchange Bureau"),
        ("Yonna Islamic Microfinance", "Yonna Islamic Microfinance"),
        ("Yonna Enterprise", "Yonna Enterprise"),
        ("Yonna Insurance", "Yonna Insurance")
    ])
    title = models.CharField(max_length=50, choices=[
        ("IT", "IT"),
        ("Accountant", "Accountant"),
        ("Auditor", "Auditor"),
        ("Manager", "Manager"),
        ("CEO", "CEO"),
    ])

    def __str__(self) -> str:
        return f"{self.user.username}'s profile"
    
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        image = Image.open(self.image.path)
        if image.height > 300 or image.width > 300:
            output_size = (300, 300)
            image.thumbnail(output_size)
            image.save(self.image.path)
