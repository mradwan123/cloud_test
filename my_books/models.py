from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Books(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    published_date = models.DateField()
    is_published = models.BooleanField(default=False)

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='user_reviews')
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()
    
    