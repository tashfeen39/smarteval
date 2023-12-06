from django.urls import path
from . import views

app_name = 'portals'
urlpatterns = [
    path("", views.home, name="home"),
]
