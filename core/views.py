
from django.shortcuts import get_object_or_404
from .models import Application, Job
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .permissions import IsEmployer, IsCandidate

from .services.job_service import get_all_jobs
from .serializers import JobSerializer, SignupSerializer


def home(request):
    return JsonResponse({
        "message": "Hello Zecpath Backend"
    })


class JobListAPIView(APIView):

    def get(self, request):
        jobs = get_all_jobs()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


class JobCreateAPIView(APIView):
    permission_classes = [IsEmployer]

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            employer = request.user.core_user.employer_profile

            serializer.save(employer=employer)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserTestAPIView(APIView):

    def get(self, request):
        return Response({
            "message": "User API is working successfully",
            "status": "success",
            "user_role": getattr(request, 'user_role', None)
        })
    
class CandidateApplyAPIView(APIView):
    permission_classes = [IsCandidate]

    def post(self, request):
        job_id = request.data.get('job_id')

        if not job_id:
            return Response(
                {"error": "Job ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        job = get_object_or_404(Job, id=job_id)

        candidate = request.user.core_user

        if Application.objects.filter(
            user=candidate,
            job=job
        ).exists():
            return Response(
                {"error": "You have already applied for this job."},
                status=status.HTTP_400_BAD_REQUEST
            )

        application = Application.objects.create(
            user=candidate,
            job=job
        )

        return Response(
            {
                "message": "Job application submitted successfully.",
                "application_id": application.id
            },
            status=status.HTTP_201_CREATED
        )

class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "User registered successfully",
                    "status": "success"
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "message": "Logout successful.",
                    "status": "success"
                },
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )
