from django.urls import path

from .views import PhoneCallInfoAPI, DealCreationHandlerAPI
urlpatterns = [
    path('/phone-call-info', PhoneCallInfoAPI.as_view()),
    path('/deal-creation-handler', DealCreationHandlerAPI.as_view()),
]
