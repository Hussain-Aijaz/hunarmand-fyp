from rest_framework import serializers
from .models import UserReviews, Jobs, Bids


class UserReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReviews
        fields = "__all__"
        read_only_fields = ("created_by", "modified_by", "created_at", "update_at")


class JobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = "__all__"
        read_only_fields = ("created_by", "modified_by", "created_at", "update_at","task_id")


class BidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bids
        fields = "__all__"
        read_only_fields = ("created_by", "modified_by", "created_at", "update_at")