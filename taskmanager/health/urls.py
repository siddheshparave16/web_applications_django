from django.urls import path
from health.views import liveness, readiness

urlpatterns = [
    path("liveness/", liveness, name="liveness_check"),
    path("readiness/", readiness, name="readiness_check"),
]
