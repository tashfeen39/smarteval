from django.urls import path
from . import views

app_name = 'student_portal'
urlpatterns = [
    path("", views.home, name="home"),
]
