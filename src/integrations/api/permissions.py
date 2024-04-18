from django.conf import settings

from rest_framework import permissions


class AppTokenIsCorrect(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.data["auth[application_token]"] == settings.BITRIX_APP_TOKEN
