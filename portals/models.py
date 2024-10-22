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

    def __str__(self):
        return self.department_name
    

class Program(models.Model):
    ProgramID = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program_name = models.CharField(max_length=100)
    total_semester = models.IntegerField(default=8)

    def __str__(self):
        return f"{self.program_name } Program for {self.department.department_name}"
    


class Degree(models.Model):
    DegreeID = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    degree_name = models.CharField(max_length=100)
    degree_abbreviation = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.degree_abbreviation } - {self.degree_name}"
    

class SemesterDetails(models.Model):
    SemesterDetailsID = models.AutoField(primary_key=True)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    semester_number = models.PositiveIntegerField()

    def __str__(self):
        return f"Semester {self.semester_number} - {self.degree}"
    
    class Meta:
        verbose_name_plural = "Semester Details"


class Course(models.Model):
    CourseID = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    course_name = models.CharField(max_length=100)
    theory_credit_hours = models.IntegerField(default=3, blank=True, null=True)
    lab_credit_hours = models.IntegerField(default=1, blank=True, null=True)

    def __str__(self):
        return self.course_name
    

class SemesterCourses(models.Model):
    SemesterCoursesID = models.AutoField(primary_key=True)
    semester_details = models.ForeignKey(SemesterDetails, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return f"Semester {self.semester_details.semester_number} - {self.semester_details.degree} - Courses"
    
    class Meta:
        verbose_name_plural = "Semester Courses"


class Section(models.Model):
    section_name = models.CharField(max_length=100)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    semester = models.IntegerField()

    def __str__(self):
        return f"{self.degree.degree_abbreviation} - Semester {self.semester} - Section {self.section_name}"
    

class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="teacher"
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

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


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="student"
    )
    degree = models.ForeignKey(Degree, on_delete=models.SET_NULL, null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
   
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
    # semester = models.CharField(max_length=100, null=True, blank=True)
    semester = models.IntegerField(blank=True, null=True)
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

class TeacherCoursesTaught(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, blank=True, null=True)
    courses = models.ManyToManyField(Course, blank=True)

    def __str__(self):
        return f"{self.teacher.user.first_name} {self.teacher.user.last_name} - {self.teacher.user.username} - Courses"

    class Meta:
        verbose_name_plural = "Teacher Courses Taught"


class TeacherSectionsTaught(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.teacher.user.first_name} {self.teacher.user.last_name} - {self.course} - {self.section}"

    class Meta:
        verbose_name_plural = "Teacher Sections Taught"




class ClassRoom(models.Model):
    class_room_number = models.CharField(max_length=50, blank=True, null=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.department:
            return f"{self.class_room_number} - {self.department.department_name}"
        else:
            return self.class_room_number
        
    class Meta:
        verbose_name_plural = "Class Rooms"


class ClassTiming(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    weekday = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ])

    def __str__(self):
        return f"{self.weekday} {self.start_time} - {self.end_time}"
    
    class Meta:
        verbose_name_plural = "Class Timings"

class Class(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    class_timing = models.ForeignKey(ClassTiming, on_delete=models.CASCADE)
    class_taken = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course} - {self.section} - {self.teacher}"

    class Meta:
        verbose_name_plural = "Classes"


class SemesterMarksData(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    mids_marks = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    final_marks = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    semester_project_marks = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    semester_number = models.PositiveSmallIntegerField(blank=True, null=True)
    total_mids_marks = models.DecimalField(max_digits=5, decimal_places=1, default=25, blank=True, null=True)
    total_final_marks = models.DecimalField(max_digits=5, decimal_places=1, default=45, blank=True, null=True)
    total_project_marks = models.DecimalField(max_digits=5, decimal_places=1, default=10, blank=True, null=True)


    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name} - {self.course.course_name} - Semester {self.semester_number} Marks"
    
    class Meta:
        verbose_name_plural = "Semester Marks Data"
    

class AssignmentMarks(models.Model):
    semester_marks_data = models.ForeignKey(SemesterMarksData, on_delete=models.CASCADE, blank=True, null=True)
    assignment_num = models.CharField(max_length=20, blank=True, null=True) 
    assignment_marks = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    total_assignment_marks = models.DecimalField(default=10, max_digits=5, decimal_places=1, blank=True, null=True)


    def __str__(self):
        return f"{self.semester_marks_data} - Assignment {self.assignment_num} - Marks: {self.assignment_marks}"
    
    class Meta:
        verbose_name_plural = "Assignments Marks"
    

class QuizMarks(models.Model):
    semester_marks_data = models.ForeignKey(SemesterMarksData, on_delete=models.CASCADE, blank=True, null=True)
    quiz_num = models.CharField(max_length=20, blank=True, null=True)  
    quiz_marks = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    total_quiz_marks = models.DecimalField(default=10, max_digits=5, decimal_places=1, blank=True, null=True)
    

    def __str__(self):
        return f"{self.semester_marks_data} - Quiz {self.quiz_num} - Marks: {self.quiz_marks}"
    
    class Meta:
        verbose_name_plural = "Quizzes Marks"



class PresentationMarks(models.Model):
    semester_marks_data = models.ForeignKey(SemesterMarksData, on_delete=models.CASCADE, blank=True, null=True)
    presentation_num = models.CharField(max_length=20, blank=True, null=True) 
    presentation_marks = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    total_presentation_marks = models.DecimalField(default=10, max_digits=5, decimal_places=1, blank=True, null=True)


    def __str__(self):
        return f"{self.semester_marks_data} - Presentation {self.presentation_num} - Marks: {self.presentation_marks}"
    
    class Meta:
        verbose_name_plural = "Presentations Marks"

def get_default_course_grade(student, course):
    # Retrieve the SemesterMarksData for the current student and course
    # Assuming SemesterMarksData has a related_name of 'marks_data' in the ForeignKey field
    marks_data = SemesterMarksData.objects.filter(student=student, course=course).first()
    
    # If marks_data exists, calculate the grade based on conditions
    if marks_data:
        mids_marks = marks_data.mids_marks
        final_marks = marks_data.final_marks

        # Set conditions for each grade
        if mids_marks > 20 and final_marks > 40:
            return 'A'
        elif mids_marks > 15 and final_marks > 35:
            return 'B'
        elif mids_marks > 10 and final_marks > 30:
            return 'C'
        else:
            return 'D'
    
    # If marks_data does not exist, return a default grade
    return 'N/A'

class SemesterCourseGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    semester_number = models.IntegerField(blank=True, null=True)
    course_grade = models.CharField(max_length=5, default='N/A', blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.first_name} - {self.student.user.last_name} - {self.course} - Semester {self.semester_number}: {self.course_grade}"

    class Meta:
        verbose_name_plural = "Semester Courses Grades"


class Feedback(models.Model):
    feedback_from = models.CharField(max_length=100, blank=True, null=True)
    feedback_for = models.CharField(max_length=100, blank=True, null=True)
    feedback_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Feedback from {self.feedback_from} to {self.feedback_for}"
    
class Complaint(models.Model):
    complaint_from = models.CharField(max_length=100, blank=True, null=True)
    complaint_for = models.CharField(max_length=100, blank=True, null=True)
    complaint_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Complaint from {self.complaint_from} to {self.complaint_for}"    