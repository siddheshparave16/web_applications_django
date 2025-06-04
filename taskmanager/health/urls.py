from django.urls import path
from health.views import liveness, readiness

app_name = "health"

urlpatterns = [
    path("liveness/", liveness, name="liveness"),
    path("readiness/", readiness, name="readiness"),
]