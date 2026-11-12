
from django.shortcuts import get_object_or_404
from .models import (Application,Job,Candidate,Employer,UserRole,User as CoreUser)
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .permissions import IsEmployer, IsCandidate

from .services.job_service import get_all_jobs
from .serializers import (JobSerializer,SignupSerializer,CandidateSerializer,EmployerSerializer)
from rest_framework.parsers import MultiPartParser, FormParser

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
class EmployerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile_owner(self, request):
        core_user = getattr(request.user, "core_user", None)

        if core_user is None:
            return None, Response(
                {"error": "User profile not found."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Admin can access another employer's profile
        if core_user.role == UserRole.ADMIN:
            user_id = request.query_params.get('user_id')

            if not user_id:
                return None, Response(
                    {"error": "Admin must provide user_id."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            target_user = get_object_or_404(CoreUser, id=user_id)

            if target_user.role != UserRole.EMPLOYER:
                return None, Response(
                    {"error": "Selected user is not an employer."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return target_user, None

        # Employer can access only their own profile
        if core_user.role != UserRole.EMPLOYER:
            return None, Response(
                {"error": "Only employers or admins can access this profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        return core_user, None

    def get(self, request):
        target_user, error = self.get_profile_owner(request)

        if error:
            return error

        profile = get_object_or_404(
            Employer,
            user=target_user,
            is_deleted=False
        )

        serializer = EmployerSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        core_user = getattr(request.user, "core_user", None)

        if core_user is None or core_user.role != UserRole.EMPLOYER:
            return Response(
                {"error": "Only employers can create their own profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        if Employer.objects.filter(user=core_user).exists():
            return Response(
                {"error": "Employer profile already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EmployerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=core_user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request):
        target_user, error = self.get_profile_owner(request)

        if error:
            return error

        profile = get_object_or_404(
            Employer,
            user=target_user,
            is_deleted=False
        )

        serializer = EmployerSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        target_user, error = self.get_profile_owner(request)

        if error:
            return error

        profile = get_object_or_404(
            Employer,
            user=target_user,
            is_deleted=False
        )

        profile.is_deleted = True
        profile.save()

        return Response(
            {"message": "Employer profile deleted successfully."},
            status=status.HTTP_200_OK
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

    
class CandidateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def get_profile_owner(self, request):
        core_user = getattr(request.user, "core_user", None)

        if core_user is None:
            return None, Response(
                {"error": "User profile not found."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Admin can access another candidate's profile
        if core_user.role == UserRole.ADMIN:
            user_id = request.query_params.get('user_id')

            if not user_id:
                return None, Response(
                    {"error": "Admin must provide user_id."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            target_user = get_object_or_404(CoreUser, id=user_id)

            if target_user.role != UserRole.CANDIDATE:
                return None, Response(
                    {"error": "Selected user is not a candidate."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return target_user, None

        # Candidate can access only their own profile
        if core_user.role != UserRole.CANDIDATE:
            return None, Response(
                {"error": "Only candidates or admins can access this profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        return core_user, None

    def get(self, request):
        target_user, error = self.get_profile_owner(request)

        if error:
            return error

        profile = get_object_or_404(
            Candidate,
            user=target_user,
            is_deleted=False
        )

        serializer = CandidateSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        core_user = getattr(request.user, "core_user", None)

        if core_user is None or core_user.role != UserRole.CANDIDATE:
            return Response(
                {"error": "Only candidates can create their own profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        if Candidate.objects.filter(user=core_user).exists():
            return Response(
                {"error": "Candidate profile already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CandidateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=core_user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request):
        target_user, error = self.get_profile_owner(request)

        if error:
            return error

        profile = get_object_or_404(
            Candidate,
            user=target_user,
            is_deleted=False
        )

        serializer = CandidateSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        target_user, error = self.get_profile_owner(request)

        if error:
            return error

        profile = get_object_or_404(
            Candidate,
            user=target_user,
            is_deleted=False
        )

        profile.is_deleted = True
        profile.save()

        return Response(
            {"message": "Candidate profile deleted successfully."},
            status=status.HTTP_200_OK
        )


class CandidateResumeUploadAPIView(CandidateProfileAPIView):

    def post(self, request):
        target_user, error = self.get_profile_owner(request)

        if error:
            return error

        profile = get_object_or_404(
            Candidate,
            user=target_user,
            is_deleted=False
        )

        serializer = CandidateSerializer(
            profile,
            data=request.data,
            partial=True
        )
         
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Resume uploaded successfully.",
                    "resume": serializer.data.get('resume')
                },
                status=status.HTTP_200_OK
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
