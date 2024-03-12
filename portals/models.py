from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures', null=True, blank=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=150, unique=True, null=True)

class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="student"
    )
    # first_name = models.CharField(max_length=100)
    # last_name = models.CharField(max_length=100)
    # batch = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=100)
    section = models.CharField(max_length=100, null = True, blank = True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="teacher"
    )
    # first_name = models.CharField(max_length=100)
    # last_name = models.CharField(max_length=100)
    # subject = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
