from django.contrib import admin
from .models import UserReviews, Jobs, Bids


class BaseAuditAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "update_at", "created_by", "modified_by")

    list_display = ("id", "created_by", "modified_by", "created_at", "update_at")
    list_filter = ("created_by", "modified_by", "created_at", "update_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserReviews)
class UserReviewsAdmin(BaseAuditAdmin):
    list_display = (
        "id",
        "from_user_id",
        "to_user_id",
        "comments",
        "rating",
        "created_by",
        "modified_by",
        "created_at",
        "update_at",
    )
    search_fields = ("from_user_id", "to_user_id", "comments", "rating")


@admin.register(Jobs)
class JobsAdmin(BaseAuditAdmin):
    list_display = (
        "id",
        "task_id",
        "category",
        "priority",
        "subject",
        "description",
        "status",
        "assigned_to",
        "created_by",
        "modified_by",
        "created_at",
        "update_at",
    )
    search_fields = ("task_id", "category", "priority", "status", "assigned_to")


@admin.register(Bids)
class BidsAdmin(BaseAuditAdmin):
    list_display = (
        "id",
        "job",
        "bidder",
        "amount",
        "status",
        "created_by",
        "modified_by",
        "created_at",
        "update_at",
    )
    search_fields = ("job__task_id", "bidder__username", "status")
