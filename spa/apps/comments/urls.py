from django.urls import path
from .views import CommentListView, CommentDetailView, CaptchaView

urlpatterns = [
    path('comments/', CommentListView.as_view()),
    path('comments/<int:pk>/', CommentDetailView.as_view()),
    path('captcha/new/', CaptchaView.as_view()),
]