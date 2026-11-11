from rest_framework.permissions import BasePermission
from .models import UserRole


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'core_user')
            and request.user.core_user.role == UserRole.ADMIN
        )


class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'core_user')
            and request.user.core_user.role == UserRole.EMPLOYER
        )


class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'core_user')
            and request.user.core_user.role == UserRole.CANDIDATE
        )