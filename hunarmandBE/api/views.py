from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserReviews, Jobs, Bids
from .serializers import UserReviewsSerializer, JobsSerializer, BidsSerializer
from api.middleware.current_user import get_current_user
from api.utils import calculate_distance


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
            return Jobs.objects.filter(id__in=job_ids).order_by('created_at')  # optional ordering

        elif user.role == 'seeker':
            return Jobs.objects.filter(created_by=user)  # already queryset

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

    def perform_create(self, serializer):
        user = get_current_user()
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = get_current_user()
        serializer.save(modified_by=user)
