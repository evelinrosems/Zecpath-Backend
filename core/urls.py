from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/jobs/', views.JobListAPIView.as_view(), name='job-list'),
    path('api/jobs/create/', views.JobCreateAPIView.as_view(), name='job-create'),
    path('api/user-test/', views.UserTestAPIView.as_view(), name='user-test'),
]