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
    # profile_picture = models.ImageField(
    #     upload_to='profile_pictures', null=True, blank=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=150, unique=True, null=True)

class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="student"
    )
   
    date_of_birth = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER_CHOICES)
    MARITAL_STATUS_CHOICES = (
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Other', 'Other')
    )
    marital_status = models.CharField(max_length=10, null=True, blank=True, choices=MARITAL_STATUS_CHOICES)
    religion = models.CharField(max_length=100, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    cnic = models.CharField(max_length=15, null=True, blank=True)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    father_occupation = models.CharField(max_length=100, null=True, blank=True)
    semester = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(max_length=200, blank=True, null=True)
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

    date_of_birth = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER_CHOICES)
    MARITAL_STATUS_CHOICES = (
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Other', 'Other')
    )
    marital_status = models.CharField(max_length=10, null=True, blank=True, choices=MARITAL_STATUS_CHOICES)
    religion = models.CharField(max_length=100, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    cnic = models.CharField(max_length=15, null=True, blank=True)
    office_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(max_length=200, blank=True, null=True)

   
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class School(models.Model):
    SchoolID = models.AutoField(primary_key=True)
    school_name = models.CharField(max_length=100)
    school_intro = models.TextField()

    def __str__(self):
        return self.school_name


class Department(models.Model):
    DepartmentID = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=100)
    department_intro = models.TextField()

    def __str__(self):
        return self.department_name
    

class Program(models.Model):
    ProgramID = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program_name = models.CharField(max_length=100)
    total_semester = models.IntegerField(default=8)

    def __str__(self):
        return self.program_name
    


class Degree(models.Model):
    DegreeID = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    degree_name = models.CharField(max_length=100)

    def __str__(self):
        return self.degree_name
    

class SemesterDetails(models.Model):
    SemesterDetailsID = models.AutoField(primary_key=True)
    semester_number = models.PositiveIntegerField()
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)

    def __str__(self):
        return f"Semester {self.semester_number} - {self.degree}"


class Course(models.Model):
    CourseID = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    course_name = models.CharField(max_length=100)
    theory_credit_hours = models.IntegerField()
    lab_credit_hours = models.IntegerField()

    def __str__(self):
        return self.course_name
    

class SemesterCourses(models.Model):
    SemesterCoursesID = models.AutoField(primary_key=True)
    semester_details = models.ForeignKey(SemesterDetails, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return f"Semester Courses: {self.semester_details.semester_number}"


class CoursePrerequisite(models.Model):
    CoursePrerequisiteID = models.AutoField(primary_key=True)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return f"Course Prerequisite: {self.CoursePrerequisiteID}"