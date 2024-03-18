import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures', null=True, blank=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=150, unique=True, null=True)

class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="student"
    )
   
    StudentID = models.CharField("Registration ID", max_length=4, unique=True, editable=False)
    date_of_birth = models.DateField(unique=True, null=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    gender = models.CharField(max_length=10, unique=True, null=True, choices=GENDER_CHOICES)
    MARITAL_STATUS_CHOICES = (
        ('Sinle', 'Single'),
        ('Married', 'Married'),
        ('Other', 'Other')
    )
    marital_status = models.CharField(max_length=10, unique=True, null=True, choices=MARITAL_STATUS_CHOICES)
    religion = models.CharField(max_length=100, unique=True, null=True)
    nationality = models.CharField(max_length=100, unique=True, null=True)
    cnic = models.CharField(max_length=15, unique=True, null=True)
    father_name = models.CharField(max_length=255, unique=True, null=True)
    father_occupation = models.CharField(max_length=100, unique=True, null=True)
    semester = models.CharField(max_length=100, unique=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    StudentID = models.CharField("Registration ID", max_length=6, unique=True, editable=False)

    def generate_unique_code(self):
        code = ''.join(random.choices(string.digits, k=6))
        return code


    def save(self, *args, **kwargs):
        if not self.StudentID:
            while True:
                code = self.generate_unique_code()
                if not Student.objects.filter(StudentID=code).exists():
                    self.StudentID = code
                    break
        super().save(*args, **kwargs)

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
