from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.job_service import get_all_jobs
from .serializers import JobSerializer

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

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )
class UserTestAPIView(APIView):

    def get(self, request):
        return Response({
            "message": "User API is working successfully",
            "status": "success"
        })