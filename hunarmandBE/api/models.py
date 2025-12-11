from django.db import models
from django.conf import settings
from api.middleware.current_user import get_current_user


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
    priority = models.CharField(max_length=50)
    subject = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    status = models.CharField(max_length=50)
    assigned_to = models.CharField(max_length=50)
    
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