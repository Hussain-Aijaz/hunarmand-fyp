from django.urls import path
from .views import (
    UserReviewsViewSet,
    JobsViewSet,
    BidsViewSet
)

userreviews_list = UserReviewsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
userreviews_detail = UserReviewsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

jobs_list = JobsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
jobs_detail = JobsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

bids_list = BidsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
bids_detail = BidsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('userreviews/', userreviews_list, name='userreviews-list'),
    path('userreviews/<int:pk>/', userreviews_detail, name='userreviews-detail'),
    
    path('jobs/', jobs_list, name='jobs-list'),
    path('jobs/<int:pk>/', jobs_detail, name='jobs-detail'),
    
    path('bids/', bids_list, name='bids-list'),
    path('bids/<int:pk>/', bids_detail, name='bids-detail'),
]
