
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Job, User as CoreUser, UserRole

AuthUser = get_user_model()


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


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
