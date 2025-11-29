from django.db import models
from django.contrib.auth.models import User

class UserReviews (models.Model):
    id = models.AutoField(primary_key=True)
    from_user_id = models.CharField(max_length=50)
    to_user_id = models.CharField(max_length=50)
    comments = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    rating = models.CharField(max_length=50)

class Jobs (models.Model):
    id = models.AutoField(primary_key=True)
    task_id = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    subject = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    status = models.CharField(max_length=50)
    assigned_to = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jobs_created'
    )