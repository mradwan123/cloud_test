from django.contrib import admin
from .models import Books, Review

# Register your models here.

admin.site.register(Books), 
admin.site.register(Review)