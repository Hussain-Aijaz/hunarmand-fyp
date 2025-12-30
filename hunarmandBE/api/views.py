from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from hmusers.models import Users
from .models import UserReviews, Jobs, Bids
from .serializers import UserReviewsSerializer, JobsSerializer, BidsSerializer
from api.middleware.current_user import get_current_user
from api.utils import *
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .enum import *
from django.db.models import Count, Min
from django.db import transaction


class UserReviewsViewSet(viewsets.ModelViewSet):
    queryset = UserReviews.objects.all()
    serializer_class = UserReviewsSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filters and search
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['from_user_id', 'to_user_id', 'rating']
    search_fields = ['from_user_id', 'to_user_id', 'comments', 'rating']
    ordering_fields = ['created_at', 'update_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        user = get_current_user()
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = get_current_user()
        serializer.save(modified_by=user)


class JobsViewSet(viewsets.ModelViewSet):
    queryset = Jobs.objects.all()
    serializer_class = JobsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        all_jobs = Jobs.objects.select_related('created_by').all()

        if user.role == 'provider':
            jobs_filtered = calculate_distance(user.latitude, user.longitude, all_jobs)
            # convert list to queryset
            job_ids = [job.id for job in jobs_filtered]
            queryset = Jobs.objects.filter(id__in=job_ids).annotate(
            total_bids=Count('bids'),
            minimum_bid=Min('bids__amount')
            ).order_by('created_at')
            return queryset  # optional ordering

        elif user.role == 'seeker':
            return Jobs.objects.filter(created_by=user).annotate(
                total_bids=Count('bids'),
                minimum_bid=Min('bids__amount')
            )

        return Jobs.objects.none() 
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'priority', 'status', 'assigned_to']
    search_fields = ['task_id', 'category', 'priority', 'subject', 'description', 'status', 'assigned_to']
    ordering_fields = ['created_at', 'update_at', 'priority']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            modified_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(
            modified_by=self.request.user
        )


class BidsViewSet(viewsets.ModelViewSet):
    queryset = Bids.objects.all()
    serializer_class = BidsSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job', 'bidder', 'status']
    search_fields = ['job__task_id', 'bidder__username', 'status']
    ordering_fields = ['created_at', 'update_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        job_id = self.request.query_params.get('job')

        if self.request.method == 'GET' and not job_id:
            raise ValidationError({
                "job": "job_id query parameter is required."
            })

        queryset = Bids.objects.filter(job_id=job_id)

        if user.role == 'provider':
            return queryset.filter(bidder=user)

        elif user.role == 'seeker':
            return queryset.filter(job__created_by=user)

        return Bids.objects.none()    
    

    
    def perform_create(self, serializer):
        user = self.request.user

        # Apply rule only for providers
        if user.role == 'provider':
            job = serializer.validated_data.get('job')
            bidder_id = self.request.data.get('bidder')

            draft_exists = Bids.objects.filter(
                job=job,
                #bidder=user,
                bidder=get_object_or_404(Users, id=bidder_id),
                status='Draft'
            ).exists()

            if draft_exists:
                raise ValidationError({
                    "detail": "You already have a draft bid for this job. Please update the existing draft instead of creating a new one."
                })
            
            if approved_bid_check(job.id):
                raise ValidationError({
                    "detail": "An approved bid already exists for this job. No further bids can be placed."
                })

        job_id = serializer.validated_data.get('job').id
        bid_count = Bids.objects.filter(job_id=job_id).count()
        if bid_count == 0:
            job_status_update(job_id, 'Waiting')

        serializer.save(
            bidder=get_object_or_404(Users, id=bidder_id),
            created_by=user,
            modified_by=user
        )

    def perform_update(self, serializer):
        if serializer.validated_data.get('status') == 'Approved':
            job = serializer.validated_data.get('job')
            bid_status_update(job.id, 'Rejected', serializer.instance.id)
            job_assigned_to(job.id, serializer.validated_data.get('bidder').id)
        serializer.save(modified_by=self.request.user)
    
    def perform_destroy(self, instance):
        job = instance.job
        remaining_bids_count = count_bids_del(job.id)

        with transaction.atomic():
            instance.delete()

            if remaining_bids_count == 1:
                job.status = "Draft"  # or any required status
                job.save(update_fields=["status"])
    

class EnumListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "job_status": [key for key, _ in JOB_STATUS_ENUM],
            "priority": [key for key, _ in PRIORITY_ENUM],
            "user_roles": [key for key, _ in USER_ROLE_ENUM],
            "bid_status": [key for key, _ in BID_STATUS_ENUM],
            "category": [key for key, _ in CATEGORY_ENUM],
        })
