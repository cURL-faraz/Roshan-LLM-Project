from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import AskView, QAViewSet

router = DefaultRouter()
router.register("history", QAViewSet)

urlpatterns = [
    path("ask/", AskView.as_view()),
    path("", include(router.urls))
]
