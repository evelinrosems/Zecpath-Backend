
from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', views.home, name='home'),

    # Job APIs
    path(
        'api/jobs/',
        views.JobListAPIView.as_view(),
        name='job-list'
    ),
    path(
        'api/jobs/create/',
        views.JobCreateAPIView.as_view(),
        name='job-create'
    ),

    # User API
    path(
        'api/user-test/',
        views.UserTestAPIView.as_view(),
        name='user-test'
    ),

    # Candidate Apply API
    path(
        'api/apply/',
        views.CandidateApplyAPIView.as_view(),
        name='candidate-apply'
    ),

    # Signup API
    path(
        'api/signup/',
        views.SignupAPIView.as_view(),
        name='signup'
    ),

        # Profile APIs
    path(
        'api/profiles/candidate/',
        views.CandidateProfileAPIView.as_view(),
        name='candidate-profile'
    ),
    path(
        'api/profiles/employer/',
        views.EmployerProfileAPIView.as_view(),
        name='employer-profile'
    ),

    # JWT APIs
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'api/logout/',
        views.LogoutAPIView.as_view(),
        name='logout'
    ),
]
