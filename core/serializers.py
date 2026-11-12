from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
import os
from rest_framework import serializers

from .models import (
    Job,
    Employer,
    Candidate,
    User as CoreUser,
    UserRole
)

AuthUser = get_user_model()


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'



class CandidateSerializer(serializers.ModelSerializer):

    def validate_resume(self, value):
        allowed_extensions = ['.pdf', '.doc', '.docx']

        extension = os.path.splitext(value.name)[1].lower()

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only PDF, DOC and DOCX files are allowed."
            )

        max_size = 5 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "Resume file size cannot exceed 5 MB."
            )

        return value

    def update(self, instance, validated_data):
        old_resume = instance.resume
        new_resume = validated_data.get('resume')

        if new_resume and old_resume:
            if old_resume.name != new_resume.name:
                old_resume.delete(save=False)

        return super().update(instance, validated_data)

    class Meta:
        model = Candidate
        fields = [
            'id',
            'phone',
            'skills',
            'resume',
            'education',
            'experience',
            'expected_salary',
        ]


        fields = [
            'id',
            'phone',
            'skills',
            'resume',
            'education',
            'experience',
            'expected_salary',
        ]

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = [
            'id',
            'company_name',
            'company_description',
            'domain',
            'company_size',
        ]
class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[
            (UserRole.EMPLOYER, 'Employer'),
            (UserRole.CANDIDATE, 'Candidate'),
        ]
    )

    def validate_email(self, value):
        if AuthUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )

        if CoreUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )

        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        name = validated_data.pop('name')
        email = validated_data.pop('email')
        phone = validated_data.pop('phone')
        role = validated_data.pop('role')

        auth_user = AuthUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
        )

        CoreUser.objects.create(
            auth_user=auth_user,
            name=name,
            email=email,
            phone=phone,
            role=role,
        )

        return auth_user
