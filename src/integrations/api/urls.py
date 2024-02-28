from django.urls import path

from .views import PhoneCallInfoAPI, DealCreationHandlerAPI, FormResponseAPI, TestAPI


urlpatterns = [
    path('phone-call-info', PhoneCallInfoAPI.as_view()),
    path('deal-creation-handler', DealCreationHandlerAPI.as_view()),
    path('form-response', FormResponseAPI.as_view()),
    path('tests', TestAPI.as_view()),
]

