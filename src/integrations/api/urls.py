from django.urls import path

from .views import PhoneCallInfoAPI, DealCreationHandlerAPI, BaseView, GetCalls, TestPost
urlpatterns = [
    path('phone-call-info', PhoneCallInfoAPI.as_view()),
    path('deal-creation-handler', DealCreationHandlerAPI.as_view()),
    path('calls', GetCalls.as_view()),
    path('test', TestPost.as_view()),
    path('', BaseView.as_view()),
]
