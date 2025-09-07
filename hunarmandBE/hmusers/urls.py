from django.urls import path, include 
from hmusers.views import *


urlpatterns = [
    path('registration/', UserRegistrationView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('profile/', UserProfileView.as_view()),
    path('password/change/', UserChangePasswordView.as_view()),
    path('password/reset-email/', SendPasswordResetEmailView.as_view()),
    path('password/reset/<uid>/<token>/', UserPasswordResetView.as_view()),
]
