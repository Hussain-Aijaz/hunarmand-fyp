from rest_framework import serializers
from .models import UserReviews, Jobs, Bids
from api.utils import *


class UserReviewsSerializer(serializers.ModelSerializer):
    no_of_bids = serializers.SerializerMethodField()
    minimum_bid = serializers.SerializerMethodField()
    
    class Meta:
        model = UserReviews
        fields = "__all__"
        read_only_fields = ("created_by", "modified_by", "created_at", "update_at")

    def get_no_of_bids(self, obj):
        count = count_bids(obj.id)
        return count[0]
    def get_minimum_bid(self, obj):
        count = count_bids(obj.id)
        return count[1]

class JobsSerializer(serializers.ModelSerializer):
    total_bids = serializers.IntegerField(read_only=True)
    minimum_bid = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    all_bids_rejected = serializers.SerializerMethodField()

    class Meta:
        model = Jobs
        fields = "__all__"
        read_only_fields = ("created_by", "modified_by", "created_at", "update_at","task_id")

    def get_all_bids_rejected(self, obj):
        user = self.context['request'].user
        return rejected_bid_check(obj.id, user.id)
    
class BidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bids
        fields = "__all__"
        read_only_fields = ("created_by", "modified_by", "created_at", "update_at")