from django.db import models
from django.conf import settings
from api.middleware.current_user import get_current_user
from .enum import JOB_STATUS_ENUM, PRIORITY_ENUM
from .number_seq_format import TASK_PREFIX
import uuid


class UserReviews (models.Model):
    id = models.AutoField(primary_key=True)
    from_user_id = models.CharField(max_length=50)
    to_user_id = models.CharField(max_length=50)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    rating = models.CharField(max_length=50)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_items'
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_%(class)s_items'
    )

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            if not self.pk:  # new object
                self.created_by = user
            self.modified_by = user
        super().save(*args, **kwargs)


class Jobs (models.Model):
    id = models.AutoField(primary_key=True)
    task_id = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    priority = models.CharField(max_length=50, choices=PRIORITY_ENUM, null=True, blank=True, default=None)
    subject = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    status = models.CharField(max_length=50, choices=JOB_STATUS_ENUM)
    assigned_to = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_items'
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_%(class)s_items'
    )

    def save(self, *args, **kwargs):
        if not self.task_id:
            # Get the last task ID
            last_job = Jobs.objects.order_by('-id').first()
            if last_job and last_job.task_id:
                # Extract the number part from last task ID
                last_number = int(last_job.task_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            # Format with leading zeros
            self.task_id = f"{TASK_PREFIX}-{new_number:03d}"  # e.g., JOB-001
        super().save(*args, **kwargs)

class Bids (models.Model):
    id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bids_made'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_items'
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_%(class)s_items'
    )
    

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            if not self.pk:  # new object
                self.created_by = user
            self.modified_by = user
        super().save(*args, **kwargs)