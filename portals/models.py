from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="student"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    batch = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=100)
    section = models.CharField(max_length=100, null = True, blank = True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Teacher(models.Model):
<<<<<<< HEAD
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='teacher')
    username = models.CharField(max_length=100, null=True, blank=True)
=======
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="teacher"
    )
>>>>>>> be3c1a394142408575f1f28c9f2e46f63fe8a175
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
<<<<<<< HEAD




=======
>>>>>>> be3c1a394142408575f1f28c9f2e46f63fe8a175
