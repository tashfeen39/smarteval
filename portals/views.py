import csv
from venv import logger
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
import re
import random
from datetime import time, timedelta
import string
from bs4 import BeautifulSoup
from django.http import JsonResponse
from portals.decorators import student_required, teacher_required
from .models import AssignmentMarks, ClassRoom, ClassTiming, Complaint, Degree, Feedback, PresentationMarks, Program, QuizMarks, Section, SemesterCourseGrade, SemesterCourses, SemesterDetails, SemesterMarksData, TeacherCoursesTaught, Class, TeacherSectionsTaught
from django.db.models import Count
from portals.models import Course, Department, Student, Teacher, User
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from .models import Course
from itertools import cycle
import itertools
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Sum, Max, Min
from datetime import timedelta




@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_class_info_view(request, sectioncourse_pk):
    # Get the section instance
    sectioncourse = get_object_or_404(TeacherSectionsTaught, pk=sectioncourse_pk)
    

    # Get all students in the section
    students = Student.objects.filter(section=sectioncourse.section)

    context = {
        'sectioncourse':sectioncourse,
        'course': sectioncourse.course,
        'students': students,
    }

    return render(request, "portals/Faculty_ClassInfo.html", context)
    

@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_dashboard_view(request):
    # Get the current date
    current_date = timezone.now().date()
    
    # Get the logged-in teacher
    teacher = request.user.teacher
    teacher_name = f"{request.user.first_name}"
    
    # Retrieve the upcoming classes for the teacher on the current day
    upcoming_classes = Class.objects.filter(teacher=teacher, class_timing__weekday=current_date.strftime('%A'))
    # Convert time format to display "12 pm" instead of "noon"
    for class_obj in upcoming_classes:
        class_obj.class_timing.start_time = class_obj.class_timing.start_time.strftime('%I:%M %p').lstrip('0')
        class_obj.class_timing.end_time = class_obj.class_timing.end_time.strftime('%I:%M %p').lstrip('0')

    context = {
        'teacher': teacher,
        'teacher_name': teacher_name,
        'upcoming_classes': upcoming_classes,
        'current_date': current_date,
    }

    return render(request, "portals/Faculty_Dashboard.html", context)



@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_display_classes_view(request):
    # teacher = request.user.teacher
    sections_taught = TeacherSectionsTaught.objects.filter(teacher=request.user.teacher)

    # print("Teacher: ", teacher)
    # print("\nSection: ", sections_taught)

    context = {
        'sections_taught': sections_taught
    }
    return render(request, "portals/Faculty_DisplayClasses.html", context)


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_feedback_view(request):
    teacher = request.user.teacher
    sections_taught = TeacherSectionsTaught.objects.filter(teacher=teacher)
    # Get the Section instances for the sections taught
    section_instances = [get_object_or_404(Section, pk=section_taught.section.pk) for section_taught in sections_taught]
    if request.method == 'POST':
            # Extract data from the form
            feedback_type = request.POST.get('feedbackType')
            feedback_from = request.POST.get('name')
            feedback_for = request.POST.get('classSelect')
            message = request.POST.get('message')

            print("Feedback Type: " , feedback_type)

            if feedback_type == "Feedback":
                # Create a new instance of Feedback model
                feedback = Feedback(
                    feedback_from=feedback_from,
                    feedback_for=feedback_for,
                    feedback_details=message,
                    created_at=timezone.now()
                )

                # Save the instance to the database
                feedback.save()

            elif feedback_type == "Complaint":
                complaint = Complaint(
                    complaint_from=feedback_from,
                    complaint_for=feedback_for,
                    complaint_details=message,
                    created_at=timezone.now()
                )
                complaint.save()

            # Redirect to the same page after successful submission
            return redirect('portals:feedbacks')
    context = {
        'teacher': teacher,
        'sections_taught': sections_taught,
        'section_instances': section_instances,
    }
    return render(request, "portals/Faculty_Feedbacks.html", context)    



@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_generate_exam_view(request):
    subjects = Course.objects.all()

    if request.method == "POST":
        subject_id = request.POST.get("subject")
    return render(request, "portals/Faculty_GenerateExam.html", {"subjects": subjects})
    


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_grading_view(request):
    return render(request, "portals/Faculty_Grading.html")

# StudentReports
@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_studentsreports_view(request):
    return render(request, "portals/Faculty_StudentsReports.html")


# Display the list of classes that the teacher teaches before marks entry page
@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_marks_entry_view(request):
    teacher = request.user.teacher
    sections_taught = TeacherSectionsTaught.objects.filter(teacher=teacher)
    

    # Get the Section instances for the sections taught
    section_instances = [get_object_or_404(Section, pk=section_taught.section.pk) for section_taught in sections_taught]

    context = {

        'sections_taught': sections_taught,
        'section_instances': section_instances,
    }
    return render(request, "portals/Faculty_MarksEntry.html", context)


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_profile_view(request):
    teacher = request.user.teacher
    context = {
        'teacher': teacher
    }

    return render(request, "portals/Faculty_Profile.html", context)


from datetime import datetime, timedelta

def find_available_time_slots(request):
     # Mapping of weekday numbers to weekday names
    weekday_names = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
    }

    # Assuming one teacher and section for demonstration
    teacher_section_taught = TeacherSectionsTaught.objects.first()

    if not teacher_section_taught:
        return HttpResponse("No teacher section taught found.")

    teacher = teacher_section_taught.teacher
    section = teacher_section_taught.section

    # Initialize teacher_free_slots with all possible classes and weekdays
    teacher_free_slots = {(time(hour=h, minute=0), weekday_names[wd]) for h in range(8, 17) for wd in range(5)}
    # Fetch teacher's class timings with weekday
    teacher_class_timings = [(timing.start_time, timing.weekday) for timing in ClassTiming.objects.filter(class__teacher=teacher)]

   # Convert teacher_class_timings to a set
    teacher_class_timings_set = set(teacher_class_timings)

    # Remove teacher's class timings from teacher_free_slots
    teacher_free_slots -= teacher_class_timings_set


    # Initialize student_free_slots with all possible classes and weekdays
    student_free_slots = {(time(hour=h, minute=0), weekday_names[wd]) for h in range(8, 17) for wd in range(5)}
    # Fetch student's class timings (for the same section) with weekday
    student_class_timings = [(timing.start_time, timing.weekday) for timing in ClassTiming.objects.filter(class__section=section)]

    student_class_timings_set = set(student_class_timings)
    student_free_slots -= student_class_timings_set


    # Extract start times and weekdays of teacher's and student's class timings
    teacher_start_times = [timing[0] for timing in teacher_free_slots]
    teacher_weekdays = [timing[1] for timing in teacher_free_slots]
    student_start_times = [timing[0] for timing in student_free_slots]
    student_weekdays = [timing[1] for timing in student_free_slots]


     # Find overlapping start times and weekdays
    available_slots = [(start_time, weekday) for start_time, weekday in zip(teacher_start_times, teacher_weekdays) if start_time in student_start_times]

    # Print available time slots in the terminal
    if available_slots:
        print("Available time slots for scheduling a class:")
        for start_time, weekday in available_slots:
            start_datetime = datetime.combine(datetime.today(), start_time)  # Convert to datetime object
            end_datetime = start_datetime + timedelta(hours=1)  # Add timedelta
            print(f"{start_time.strftime('%H:%M')} - {end_datetime.strftime('%H:%M')} (Weekday: {weekday})")  # Print formatted time strings
    else:
        print("No available time slots found for scheduling a class.")

    return HttpResponse("Available time slots printed in the terminal.")

def update_class_taken(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        class_taken = request.POST.get('class_taken')
        
        # Update the class_taken field in the Class model
        try:
            class_obj = Class.objects.get(pk=class_id)
            class_obj.class_taken = bool(class_taken)
            class_obj.save()
            return redirect('portals:dashboard')
        except Class.DoesNotExist:
            return HttpResponse('Class not found.', status=404)

    return render(request, "portals/Faculty_Dashboard.html")



def calculate_average_marks(queryset, total_students):
    """
    Helper function to calculate the overall average marks for each assessment type.
    """
    avg_marks = {}
    for item in queryset:
        avg_marks[item] = round(queryset[item] / total_students, 1)
    return avg_marks


# Display student marks and also generate data for reports to send over to the frontend
def faculty_student_info_view(request, student_id, teachersectioncourse_id):
    student = get_object_or_404(Student, StudentID=student_id)
    teachersectioncourse = get_object_or_404(TeacherSectionsTaught, pk=teachersectioncourse_id)
    course = teachersectioncourse.course
    section_students = Student.objects.filter(section=teachersectioncourse.section)

    # Get the relevant marks data for the student and course
    semester_marks_data = SemesterMarksData.objects.get(student=student, course=course)

    # Filter quiz marks by student and course
    quiz_marks = QuizMarks.objects.filter(semester_marks_data__student=student, semester_marks_data__course=course)
    # Filter assignment marks by student and course
    assignment_marks = AssignmentMarks.objects.filter(semester_marks_data__student=student, semester_marks_data__course=course)
    # Filter presentation marks by student and course
    presentation_marks = PresentationMarks.objects.filter(semester_marks_data__student=student, semester_marks_data__course=course)

    # Get unique assessment numbers
    unique_quiz_nums = quiz_marks.values_list('quiz_num', flat=True).distinct()
    unique_assignment_nums = assignment_marks.values_list('assignment_num', flat=True).distinct()
    unique_presentation_nums = presentation_marks.values_list('presentation_num', flat=True).distinct()
    

    # Calculate the maximum marks for each assessment type
    max_quiz_marks = {}
    max_assignment_marks = {}
    max_presentation_marks = {}


    # Calculate the minimum marks for each assessment type for the entire class
    min_quiz_marks = {}
    min_assignment_marks = {}
    min_presentation_marks = {}

    # Create dictionaries to accumulate average marks
    avg_quiz_marks = {f'Quiz {i}': 0 for i in unique_quiz_nums}
    avg_assignment_marks = {f'Assignment {i}': 0 for i in unique_assignment_nums}
    avg_presentation_marks = {f'Presentation {i}': 0 for i in unique_presentation_nums}

    # Get the relevant semester marks data for all students in the section
    section_semester_marks_data = SemesterMarksData.objects.filter(student__in=section_students, course=course)

    # Calculate the total mids marks, final marks, and project marks
    total_mids_marks = section_semester_marks_data.aggregate(Sum('mids_marks'))['mids_marks__sum'] or 0
    total_final_marks = section_semester_marks_data.aggregate(Sum('final_marks'))['final_marks__sum'] or 0
    total_project_marks = section_semester_marks_data.aggregate(Sum('semester_project_marks'))['semester_project_marks__sum'] or 0

    max_semester_project_marks = section_semester_marks_data.aggregate(Max('semester_project_marks'))['semester_project_marks__max'] or 0
    min_semester_project_marks = section_semester_marks_data.aggregate(Min('semester_project_marks'))['semester_project_marks__min'] or 0

    max_mids_marks = section_semester_marks_data.aggregate(Max('mids_marks'))['mids_marks__max'] or 0
    min_mids_marks = section_semester_marks_data.aggregate(Min('mids_marks'))['mids_marks__min'] or 0

    max_final_marks = section_semester_marks_data.aggregate(Max('final_marks'))['final_marks__max'] or 0
    min_final_marks = section_semester_marks_data.aggregate(Min('final_marks'))['final_marks__min'] or 0





    total_students = len(section_students)

    for section_student in section_students:
        avg_semester_marks_data = SemesterMarksData.objects.filter(student=section_student, course=course).first()
        if avg_semester_marks_data:
            avg_quiz_marks_student = QuizMarks.objects.filter(semester_marks_data=avg_semester_marks_data)
            avg_assignment_marks_student = AssignmentMarks.objects.filter(semester_marks_data=avg_semester_marks_data)
            avg_presentation_marks_student = PresentationMarks.objects.filter(semester_marks_data=avg_semester_marks_data)

            for i in unique_quiz_nums:
                # max_quiz_marks[f'Quiz {i}'] = avg_quiz_marks_student.filter(quiz_num=i).aggregate(Max('quiz_marks'))['quiz_marks__max'] or 0
                quiz_avg = avg_quiz_marks_student.filter(quiz_num=i).aggregate(Avg('quiz_marks'))['quiz_marks__avg']
                if quiz_avg is not None:
                    avg_quiz_marks[f'Quiz {i}'] += quiz_avg

            for i in unique_assignment_nums:
                assignment_avg = avg_assignment_marks_student.filter(assignment_num=i).aggregate(Avg('assignment_marks'))['assignment_marks__avg']
                if assignment_avg is not None:
                    avg_assignment_marks[f'Assignment {i}'] += assignment_avg

            for i in unique_presentation_nums:
                presentation_avg = avg_presentation_marks_student.filter(presentation_num=i).aggregate(Avg('presentation_marks'))['presentation_marks__avg']
                if presentation_avg is not None:
                    avg_presentation_marks[f'Presentation {i}'] += presentation_avg

    # Calculate overall average marks for each assessment type
    avg_quiz_marks = calculate_average_marks(avg_quiz_marks, total_students)
    avg_assignment_marks = calculate_average_marks(avg_assignment_marks, total_students)
    avg_presentation_marks = calculate_average_marks(avg_presentation_marks, total_students)

    avg_mids_marks = round(total_mids_marks / total_students, 1)
    avg_final_marks = round(total_final_marks / total_students, 1)
    avg_project_marks = round(total_project_marks / total_students, 1)

    # Assuming you have retrieved and processed the necessary data
    quiz_percentage_data = [float((quiz_mark.quiz_marks * 100) / quiz_mark.total_quiz_marks) for quiz_mark in quiz_marks]
    assignment_percentage_data = [float((assignment_mark.assignment_marks * 100) / assignment_mark.total_assignment_marks) for assignment_mark in assignment_marks]
    presentation_percentage_data = [float((presentation_mark.presentation_marks * 100) / presentation_mark.total_presentation_marks) for presentation_mark in presentation_marks]
    semester_project_percentage_data = (semester_marks_data.semester_project_marks * 100) / semester_marks_data.total_project_marks 
    mids_percentage_data = (semester_marks_data.mids_marks * 100) / semester_marks_data.total_mids_marks
    final_percentage_data = (semester_marks_data.final_marks * 100) / semester_marks_data.total_final_marks






    # Query all marks for the corresponding assessment types for all students in the class
    all_quiz_marks = QuizMarks.objects.filter(semester_marks_data__student__in=section_students, semester_marks_data__course=course)
    all_assignment_marks = AssignmentMarks.objects.filter(semester_marks_data__student__in=section_students, semester_marks_data__course=course)
    all_presentation_marks = PresentationMarks.objects.filter(semester_marks_data__student__in=section_students, semester_marks_data__course=course)

    # Calculate max marks for quizzes
    for quiz_num in unique_quiz_nums:
        max_quiz_marks[f'Quiz {quiz_num}'] = all_quiz_marks.filter(quiz_num=quiz_num).aggregate(Max('quiz_marks'))['quiz_marks__max'] or 0
        min_quiz_marks[f'Quiz {quiz_num}'] = all_quiz_marks.filter(quiz_num=quiz_num).aggregate(Min('quiz_marks'))['quiz_marks__min'] or 0


    # Calculate max marks for assignments
    for assignment_num in unique_assignment_nums:
        max_assignment_marks[f'Assignment {assignment_num}'] = all_assignment_marks.filter(assignment_num=assignment_num).aggregate(Max('assignment_marks'))['assignment_marks__max'] or 0
        min_assignment_marks[f'Assignment {assignment_num}'] = all_assignment_marks.filter(assignment_num=assignment_num).aggregate(Min('assignment_marks'))['assignment_marks__min'] or 0

    # Calculate max marks for presentations
    for presentation_num in unique_presentation_nums:
        max_presentation_marks[f'Presentation {presentation_num}'] = all_presentation_marks.filter(presentation_num=presentation_num).aggregate(Max('presentation_marks'))['presentation_marks__max'] or 0
        min_presentation_marks[f'Presentation {presentation_num}'] = all_presentation_marks.filter(presentation_num=presentation_num).aggregate(Min('presentation_marks'))['presentation_marks__min'] or 0


    # Pass the data to the template context
    context = {
        'student': student,
        'course': course,
        'semester_marks_data': semester_marks_data,
        'quiz_marks': list(quiz_marks),
        'assignment_marks': list(assignment_marks),
        'presentation_marks': list(presentation_marks),
        'avg_quiz_marks': avg_quiz_marks,
        'avg_assignment_marks': avg_assignment_marks,
        'avg_presentation_marks': avg_presentation_marks,
        'avg_semester_project_marks': avg_project_marks,
        'avg_mids_marks': avg_mids_marks,
        'avg_final_marks': avg_final_marks,
        'max_quiz_marks': max_quiz_marks,
        'max_assignment_marks': max_assignment_marks,
        'max_presentation_marks': max_presentation_marks,
        'min_quiz_marks': min_quiz_marks,
        'min_assignment_marks': min_assignment_marks,
        'min_presentation_marks': min_presentation_marks,
        'max_semester_project_marks': max_semester_project_marks,
        'min_semester_project_marks': min_semester_project_marks,
        'max_mids_marks': max_mids_marks,
        'min_mids_marks': min_mids_marks,
        'max_final_marks': max_final_marks,
        'min_final_marks': min_final_marks,
        'quiz_percentage_data': quiz_percentage_data,
        'assignment_percentage_data': assignment_percentage_data,
        'presentation_percentage_data': presentation_percentage_data,
        'semester_project_percentage_data': semester_project_percentage_data,
        'mids_percentage_data': mids_percentage_data,
        'final_percentage_data': final_percentage_data,

    }

    return render(request, "portals/Faculty_StudentInfo.html", context)


# View to save the marks of the student when the teacher edits them in marks entry page
@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_save_marks_view(request, teachersectioncourse_id):
    if request.method == 'POST':
        teachersectioncourse = get_object_or_404(TeacherSectionsTaught, pk=teachersectioncourse_id)
        # Iterate through the submitted form data and update the corresponding database records
        for key, value in request.POST.items():
            if key.startswith('quiz_'):
                key_parts = key.split('_')
                if len(key_parts) >= 3:
                    student_id, quiz_num = key_parts[2], key_parts[1]
                    semester_marks_data=SemesterMarksData.objects.get(student__StudentID=student_id, course=teachersectioncourse.course)
                    # Update the QuizMarks object for the student with the new marks
                    quiz_mark = QuizMarks.objects.get(semester_marks_data=semester_marks_data, quiz_num=quiz_num)
                    quiz_mark.quiz_marks = value
                    quiz_mark.save()
            elif key.startswith('assignment_'):
                key_parts = key.split('_')
                if len(key_parts) >= 3:
                    student_id, assignment_num = key_parts[2], key_parts[1]
                    semester_marks_data = SemesterMarksData.objects.get(student__StudentID=student_id, course=teachersectioncourse.course)
                    # Update the AssignmentMarks object for the student with the new marks
                    assignment_mark = AssignmentMarks.objects.get(semester_marks_data=semester_marks_data, assignment_num=assignment_num)
                    assignment_mark.assignment_marks = value
                    assignment_mark.save()

            elif key.startswith('presentation_'):
                key_parts = key.split('_')
                if len(key_parts) >= 3:
                    student_id, presentation_num = key_parts[2], key_parts[1]
                    semester_marks_data = SemesterMarksData.objects.get(student__StudentID=student_id, course=teachersectioncourse.course)
                    # Update the PresentationMarks object for the student with the new marks
                    presentation_mark = PresentationMarks.objects.get(semester_marks_data=semester_marks_data, presentation_num=presentation_num)
                    presentation_mark.presentation_marks = value
                    presentation_mark.save()

            elif key.startswith('project_marks_'):
                key_parts = key.split('_')
                if len(key_parts) >= 3:
                    student_id = key_parts[2]
                    semester_marks_data = SemesterMarksData.objects.get(student__StudentID=student_id, course=teachersectioncourse.course)
                    # Update the PresentationMarks object for the student with the new marks
                    semester_marks_data.semester_project_marks = value
                    semester_marks_data.save()

            elif key.startswith('midterm_marks_'):
                key_parts = key.split('_')
                if len(key_parts) >= 3:
                    student_id = key_parts[2]
                    semester_marks_data = SemesterMarksData.objects.get(student__StudentID=student_id, course=teachersectioncourse.course)
                    # Update the PresentationMarks object for the student with the new marks
                    semester_marks_data.mids_marks = value
                    semester_marks_data.save()

            elif key.startswith('final_marks_'):
                key_parts = key.split('_')
                if len(key_parts) >= 3:
                    student_id = key_parts[2]
                    semester_marks_data = SemesterMarksData.objects.get(student__StudentID=student_id, course=teachersectioncourse.course)
                    # Update the PresentationMarks object for the student with the new marks
                    semester_marks_data.final_marks = value
                    semester_marks_data.save()

        
        # Redirect back to the same page after saving the changes
        return redirect('portals:student-marksentry', teachersectioncourse_id=teachersectioncourse_id)
    return render(request, 'portals/Faculty_StudentMarksEntry.html')


# Display marks of all students in marks entry page and teacher can also edit them 
@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_student_marks_entry_view(request, teachersectioncourse_id):
    # Get the teacher's section taught course
    teachersectioncourse = get_object_or_404(TeacherSectionsTaught, pk=teachersectioncourse_id)
    course = teachersectioncourse.course

    # Get all students in the section
    students = Student.objects.filter(section=teachersectioncourse.section)

    # Get marks data for all students in the section
    students_marks_data = []
    for student in students:
        # Get the relevant marks data for each student and course
        semester_marks_data = SemesterMarksData.objects.filter(student=student, course=course).first()
        quiz_marks = list(QuizMarks.objects.filter(semester_marks_data__student=student, semester_marks_data__course=course))
        # print(len(quiz_marks))
        assignment_marks = AssignmentMarks.objects.filter(semester_marks_data__student=student, semester_marks_data__course=course)
        presentation_marks = PresentationMarks.objects.filter(semester_marks_data__student=student, semester_marks_data__course=course)

        # Append marks data to the list
        students_marks_data.append({
            'student': student,
            'semester_marks_data': semester_marks_data,
            'quiz_marks': quiz_marks,
            'assignment_marks': assignment_marks,
            'presentation_marks': presentation_marks
        })
        # print(students_marks_data[0])

    # Pass the list of students marks data and course to the template context
    context = {
        'teachersectioncourse':teachersectioncourse,
        'single_student': students_marks_data[0],
        'students_marks_data': students_marks_data,
        'course': course
    }

    return render(request, "portals/Faculty_StudentsMarksEntry.html", context)


@login_required(login_url='portals:student-login') 
@student_required()
def student_dashboard_view(request):
    return render(request, "portals/Student_Dashboard.html")


@login_required(login_url='portals:student-login') 
@student_required()
def student_registeredcourses_view(request):
    return render(request, "portals/Student_RegisteredCourses.html")


@login_required(login_url='portals:student-login') 
@student_required()
def student_timetable_view(request):
    return render(request, "portals/Student_TimeTable.html")


@login_required(login_url='portals:student-login') 
@student_required()
def student_report_view(request):
    return render(request, "portals/Student_Report.html")


@login_required(login_url='portals:student-login') 
@student_required()
def student_feedback_view(request):
    return render(request, "portals/Student_Feedback.html")


@login_required(login_url='portals:student-login') 
@student_required()
def student_profile_view(request):
    return render(request, "portals/Student_Profile.html")


@login_required(login_url='portals:student-login') 
@student_required()
def student_subjectwisereport_view(request):
    return render(request, "portals/Student_SubjectWiseReport.html")




def populate_semester_course_grades(request):
    # Step 1: Filter out all students
    students = Student.objects.all()

    # Step 2: Iterate over each student
    for student in students:
        # Get the SemesterDetails for the student's degree and semester number
        semester_details = SemesterDetails.objects.filter(degree=student.degree, semester_number=student.semester).first()


        # Get the SemesterCourses for the SemesterDetails
        semester_courses = SemesterCourses.objects.filter(semester_details=semester_details)

        # Iterate over each SemesterCourses
        for semester_course in semester_courses:
            # Get the courses for the SemesterCourses
            courses = semester_course.courses.all()

            # Iterate over each course
            for course in courses:
                # Create a new SemesterCourseGrade object
                semester_course_grade = SemesterCourseGrade.objects.create(
                    student=student,
                    course=course,
                    semester_number=student.semester,
                    # Default grade will be calculated automatically in the save method
                )

    # You can render a success page or redirect to another URL after populating the grades
    print("Students sucessfully assigned grades")

def generate_marks_view(request):
    # Step 1: Retrieve all students
    students = Student.objects.all()

    for student in students:
        # Step 2: Get student's section
        section = student.section

        # Step 3: Get relevant courses based on semester number and degree
        semester_courses_instance = SemesterCourses.objects.filter(semester_details__semester_number=section.semester, semester_details__degree=section.degree).first()
        print(semester_courses_instance)

        courses = semester_courses_instance.courses.all()

        for course in courses:
            # Step 4: Generate random marks
            mids_marks = random.randint(10, 25)
            final_marks = random.randint(20, 45)
            semester_project_marks = random.randint(2, 10)

            # Step 5: Create SemesterMarksData object
            semester_marks_data = SemesterMarksData.objects.create(
                student=student,
                course=course,  
                mids_marks=mids_marks,
                final_marks=final_marks,
                semester_project_marks=semester_project_marks,
                semester_number=section.semester
            )
            print(semester_marks_data)
            for assignment_num in range(1, 5):
                assignment_marks = AssignmentMarks.objects.create(
                    semester_marks_data=semester_marks_data,
                    assignment_num=assignment_num,
                    assignment_marks=random.randint(2, 10)
                )
            for quiz_num in range(1, 5):
                quiz_marks = QuizMarks.objects.create(
                    semester_marks_data=semester_marks_data,
                    quiz_num=quiz_num,
                    quiz_marks=random.randint(1, 10)
                )
            for presentation_num in range(1, 3):
                presentation_marks = PresentationMarks.objects.create(
                    semester_marks_data=semester_marks_data,
                    presentation_num=presentation_num,
                    presentation_marks=random.randint(1, 10)
                )


    print("Successfully generated marks for students.")



def test_mapping():
    ClassTiming.objects.all().delete()


def assign_classes_to_sections(request):
    # Get all teacher-section mappings
    teacher_section_mappings = TeacherSectionsTaught.objects.all()
    print(teacher_section_mappings)

    # Create a dictionary to track the availability of each classroom
    classroom_availability = {classroom.class_room_number: {} for classroom in ClassRoom.objects.all()}

    # Initialize teacher availability dictionary
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    teacher_availability = {teacher: {weekday: set() for weekday in weekdays} for teacher in Teacher.objects.all()}
        
    # Iterate over each teacher-section mapping
    for teacher_section_mapping in teacher_section_mappings:
        teacher = teacher_section_mapping.teacher
        sections = teacher_section_mapping.section
        
        # Generate random class timing for each course in each section
        courses_taught = TeacherSectionsTaught.objects.filter(teacher=teacher, section=sections).values_list('course', flat=True)
        for course_id in courses_taught:
            course = Course.objects.get(pk=course_id)
            print("Teacher: ", teacher)
            print("Course: ", course)
            
            # Generate random weekdays for two classes
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            random.shuffle(weekdays)  # Shuffle to randomize the selection
            class_weekdays = weekdays[:2]  # Select two random weekdays

            # Iterate over each selected weekday
            for weekday in class_weekdays:
                # Check classroom availability
                available_classrooms = [classroom for classroom, availability in classroom_availability.items() if weekday not in availability or not availability[weekday]]
                
                if not available_classrooms:
                    print(f"No available classrooms for {course} in section {sections} on {weekday}")
                    continue
                
                # Randomly select a classroom
                classroom_number = random.choice(available_classrooms)

                # Initialize flag to check if the class is assigned
                class_assigned = False

                # Initialize start time
                start_time = None

                # Keep trying until a class is assigned
                for start_hour in range(8, 17):
                    # Generate random start time between 8:00 AM and 4:00 PM
                    # start_hour = random.randint(8, 16) 
                    start_minute = 0
                    start_time = time(hour=start_hour, minute=start_minute)

                    # Calculate end time (1 hour duration)
                    end_time = (start_time.hour + 1) % 24
                    end_time = time(hour=end_time, minute=start_minute)

                    # Check if the teacher is available at the specified time slot
                    if start_time not in teacher_availability[teacher][weekday]:
                        # Create class
                        new_class = Class.objects.create(
                            course=course,
                            teacher=teacher,
                            section=sections,
                            classroom=ClassRoom.objects.filter(class_room_number=classroom_number).first(),
                            class_timing=ClassTiming.objects.create(
                                start_time=start_time,
                                end_time=end_time,
                                weekday=weekday
                            )
                        )
                        # Update classroom availability
                        if weekday not in classroom_availability[classroom_number]:
                            classroom_availability[classroom_number][weekday] = []
                        classroom_availability[classroom_number][weekday].append(start_time)

                        # Update teacher availability
                        teacher_availability[teacher][weekday].add(start_time)

                        print(f"Assigned class: {new_class}")
                        break
                        class_assigned = True  # Set flag to True to exit loop
                    else:
                        # Teacher is not available at the specified time slot, try again
                        print(f"Teacher {teacher} is not available on {weekday} at {start_time}. Trying again...")
                    
    print("Classes assigned successfully")



def create_course_teacher_mapping():
    course_teacher_mapping = {}
    
    # Iterate over each record in TeacherCoursesTaught
    for teacher_course in TeacherCoursesTaught.objects.all():
        teacher = teacher_course.teacher
        courses = teacher_course.courses.all()
        
        # Iterate over each course
        for course in courses:
            if course not in course_teacher_mapping:
                # If the course is not in the dictionary, add it with an empty list
                course_teacher_mapping[course] = []
            
            # Append the teacher to the list of teachers for this course
            course_teacher_mapping[course].append(teacher)
    
    # print(course_teacher_mapping)
    
    return course_teacher_mapping


def create_section_courses_mapping():
    section_courses_mapping = {}
    
    for section in Section.objects.all():
        # print("\nSection: ", section)
        semester_details = SemesterDetails.objects.filter(degree=section.degree, semester_number=section.semester)
        # print("\nSemester Detail All: ", semester_details)
        courses_for_section = []
        for semester_detail in semester_details:
            # print("\nSemester Detail: ", semester_details)
            semester_courses = SemesterCourses.objects.filter(semester_details=semester_detail)
            # print("\nSemester Courses all: ", semester_courses)
            for semester_course in semester_courses:
                # print("\nSemester Courses: ", semester_course)
                courses_for_section.extend(list(semester_course.courses.all()))
        section_courses_mapping[section] = courses_for_section

    # print(section_courses_mapping)
    return section_courses_mapping

def populate_teacher_sections_taught():
    course_teacher_mapping = create_course_teacher_mapping()

    section_courses_mapping = create_section_courses_mapping()
    
    
    # Iterate over each semester course
    for semester_course in SemesterCourses.objects.all():
        semester_details = semester_course.semester_details
        courses = semester_course.courses.all()
        
        # Iterate over each course in the semester
        for course in courses:
            # Get the teachers who teach this course
            teachers = course_teacher_mapping.get(course, [])
            
            # If there are teachers for this course
            if teachers:
                # Iterate over each section and assign a teacher to it
                for section, section_courses in section_courses_mapping.items():
                    # If the section still needs to take this course
                    if course in section_courses:
                        # Choose a random teacher for this course
                        random_teacher = random.choice(teachers)
                        
                        # Create a TeacherSectionsTaught entry with the random teacher and section
                        teacher_section_taught, created = TeacherSectionsTaught.objects.get_or_create(
                            teacher=random_teacher,
                            course=course,
                            section=section
                        )
                        
                        # Remove the course from the section's list of courses
                        section_courses.remove(course)




def assign_courses_to_semesters(request):
    # Get all SemesterDetails
    semester_details = SemesterDetails.objects.all()

    # Get all courses
    courses = list(Course.objects.all())

    # Calculate the number of courses each SemesterDetails should receive
    num_courses_per_semester = 6

    # Use itertools cycle to keep reusing the courses list
    courses_cycle = cycle(courses)

    # Iterate over each SemesterDetails
    for semester_detail in semester_details:
        # Assign courses to the current SemesterDetails
        semester_courses = SemesterCourses.objects.create(semester_details=semester_detail)

        # Get the next set of courses from the cycle
        next_courses = [next(courses_cycle) for _ in range(num_courses_per_semester)]
        semester_courses.courses.set(next_courses)



    print("Semester Courses for Semester Details generated successfully")




def create_class_rooms(request):
    # Get all departments
    departments = Department.objects.all()
    
    # Define the number of class rooms per department
    class_rooms_per_department = 30
    
    # Initialize the starting room number
    starting_room_number = 1
    
    # Iterate over each department
    for department in departments:
        # Iterate over each class room for the department
        for floor in range(starting_room_number, starting_room_number+1):
            for room_number in range(1, class_rooms_per_department + 1):
                # Generate the class room number
                class_room_number = f"{floor}{room_number:02}"
                
                # Create the class room for the department
                ClassRoom.objects.create(class_room_number=class_room_number, department=department)
                
                # Increment the room number
            starting_room_number += 1
    
    print("Class rooms created successfully")




def assign_sections_to_students(request):
    # Get all degrees
    degrees = Degree.objects.filter(degree_name__startswith='B')
    
    for degree in degrees:
        # Get all semesters of the degree
        semesters = set(Student.objects.filter(degree=degree).values_list('semester', flat=True))
        
        for semester in semesters:
            # Get all students in the current semester of the degree
            students = Student.objects.filter(degree=degree, semester=semester)
            
            # Sort students by date of birth or any other criteria you prefer
            sorted_students = students.order_by('StudentID')
            
            # Calculate the total number of students
            total_students = sorted_students.count()
            
            # Calculate the number of sections needed
            num_sections = (total_students // 30) + (1 if total_students % 30 > 15  else 0)
            
            # Create sections
            sections = []
            for i in range(num_sections):
                # Create a new section
                section_name = chr(65 + i)  # Convert integer to corresponding alphabet (A, B, C, ...)
                section = Section.objects.create(section_name=section_name, degree=degree, semester=semester)
                sections.append(section)
            
            # Distribute students to sections
            section_index = 0
            for index, student in enumerate(sorted_students):
                section = sections[section_index]
                student.section = section
                student.save()
                
                # Move to the next section
                section_index = (section_index + 1) % num_sections
                
                # # If the remaining students are less than 15, distribute them to existing sections
                # if index + 1 == total_students - (total_students % 30):
                #     break

    return "Students assigned sections successfully"





def distribute_students_semesters():
    # Get all degrees
    degrees = Degree.objects.filter(degree_name__startswith='B')

    # Iterate over each degree
    for degree in degrees:
        # Get all students in the current degree
        students = Student.objects.filter(degree=degree)
        
        # Calculate students per semester and remaining students
        students_per_semester = len(students) // 8
        remaining_students = len(students) % 8
        
        # Distribute students across 8 semesters
        semester_count = 1
        student_index = 0
        for semester in range(1, 9):
            # Assign students_per_semester to this semester
            for _ in range(students_per_semester):
                student = students[student_index]
                student.semester = semester_count
                student.save()
                student_index += 1

            # Distribute remaining students
            if remaining_students > 0:
                student = students[student_index]
                student.semester = semester_count
                student.save()
                student_index += 1
                remaining_students -= 1

            # Increment semester count
            semester_count += 1

    return "Students distributed across 8 semesters for each degree"


def distribute_students_evenly():
    degrees = Degree.objects.filter(degree_name__startswith='B')
    students = list(Student.objects.all())

    # Calculate students per degree
    students_per_degree = len(students) // len(degrees)
    remaining_students = len(students) % len(degrees)

    # Distribute students evenly among degrees
    student_index = 0
    for degree in degrees:
        # Assign students_per_degree to this degree
        for _ in range(students_per_degree):
            student = students[student_index]
            student.degree = degree
            student.save()
            student_index += 1

        # Distribute remaining students
        if remaining_students > 0:
            student = students[student_index]
            student.degree = degree
            student.save()
            student_index += 1
            remaining_students -= 1

    return "Students distributed evenly among degrees"



def assign_courses_to_teachers(request):
    # Fetch all teachers and their departments
    teachers = Teacher.objects.select_related('department').all()
    
    # Fetch all departments and their courses
    departments = Department.objects.prefetch_related('course_set').all()
    
    # Initialize a dictionary to hold courses for each department
    department_courses = {department.DepartmentID: list(department.course_set.all()) for department in departments}
    
    # Iterate over each department
    for department_id, courses in department_courses.items():
        # Fetch all teachers in the department
        department_teachers = teachers.filter(department_id=department_id)
        
        # If there are no teachers in the department or no courses, continue to the next department
        if not department_teachers or not courses:
            continue
        
        # Calculate the number of courses each teacher should get and handle uneven division
        num_teachers = len(department_teachers)
        num_courses = len(courses)
        courses_per_teacher = num_courses // num_teachers
        extra_courses = num_courses % num_teachers
        
        # Create an iterator to cycle through the courses
        course_iterator = cycle(courses)
        
        # Iterate over each teacher and assign courses
        for teacher in department_teachers:
            teacher_courses_taught, _ = TeacherCoursesTaught.objects.get_or_create(teacher=teacher)
            
            # Assign courses to the teacher
            assigned_courses = []
            for _ in range(courses_per_teacher):
                assigned_courses.append(next(course_iterator))
                
            # If there are extra courses, assign them to teachers one by one
            if extra_courses > 0:
                assigned_courses.append(next(course_iterator))
                extra_courses -= 1
            
            teacher_courses_taught.courses.set(assigned_courses)
            teacher_courses_taught.save()
    print("Courses assigned to teachers successfully.")

def assign_departments_to_teachers():
    # Fetch all teachers and departments
    teachers = Teacher.objects.all()
    departments = Department.objects.all()

    # Calculate the number of teachers and departments
    num_teachers = len(teachers)
    num_departments = len(departments)

    # Calculate how many teachers each department should ideally have
    ideal_teachers_per_department = num_teachers // num_departments
    remainder = num_teachers % num_departments

    # Create an iterator to cycle through departments
    department_iterator = cycle(departments)

    # Assign departments to teachers
    for teacher in teachers:
        # Get the next department from the iterator
        department = next(department_iterator)

        # Assign the department to the teacher
        teacher.department = department
        teacher.save()

        # If there are remaining teachers, distribute them
        if remainder > 0:
            remainder -= 1
            # Move to the next department in the iterator
            department = next(department_iterator)

    print("Departments assigned to teachers successfully.")



def update_departments(request):
    # Fetch all departments and courses
    departments = Department.objects.all()
    courses = Course.objects.all()

    # Calculate the number of courses per department
    num_courses_per_department = len(courses) // len(departments)
    remainder = len(courses) % len(departments)

    # Initialize counters
    course_count = 0

    # Iterate over departments
    for department in departments:
        # Determine the number of courses for this department
        if remainder > 0:
            num_courses = num_courses_per_department + 1
            remainder -= 1
        else:
            num_courses = num_courses_per_department
        
        # Assign courses to this department
        for _ in range(num_courses):
            course = courses[course_count]
            course.department = department
            course.save()
            course_count += 1


def add_random_digit_to_username(request):
    input_file_path = 'moreusers.csv'  # Replace '/path/to/allusers.csv' with the actual path to your input file
    output_file_path = 'morenewusers.csv'  # Replace '/path/to/allnewusers.csv' with the desired path for the output file

    with open(input_file_path, 'r') as input_file:
        reader = csv.DictReader(input_file)
        modified_data = []
        for row in reader:
            username = row['Username']
            random_digit = random.randint(0, 9)
            username_with_random_digit = f'{username}{random_digit}'
            row['Username'] = username_with_random_digit
            modified_data.append(row)

    with open(output_file_path, 'w', newline='') as output_file:
        fieldnames = ['First Name', 'Last Name', 'Phone Number', 'Email', 'Password', 'Username']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(modified_data)

    
def add_random_digits_to_email(request):
    input_file_path = 'moreusers.csv'  # Replace '/path/to/allusers.csv' with the actual path to your input file
    output_file_path = 'morenewusers.csv'  # Replace '/path/to/allnewusers.csv' with the desired path for the output file

    with open(input_file_path, 'r') as input_file:
        reader = csv.DictReader(input_file)
        modified_data = []
        for row in reader:
            email = row['Email']
            if email.endswith('@gmail.com'):
                random_digits = ''.join(str(random.randint(0, 9)) for _ in range(1))
                email_with_random_digits = email.replace('@gmail.com', f'{random_digits}@gmail.com')
                row['Email'] = email_with_random_digits
            modified_data.append(row)

    with open(output_file_path, 'w', newline='') as output_file:
        fieldnames = ['First Name', 'Last Name', 'Phone Number', 'Email', 'Password', 'Username']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(modified_data)
    


def read_users_from_csv(request):
    # File path for allusers.csv
    csv_file_path = "moreusers.csv"

    # Open the CSV file and iterate over its rows
    with open(csv_file_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Create a new User object for each row in the CSV file
            user = User.objects.create_user(
                first_name=row['First Name'],
                last_name=row['Last Name'],
                phone_number=row['Phone Number'],
                email=row['Email'],
                password=(row['Password']),  
                username=row['Username'],
                is_student=True,
                # is_student=True if reader.line_num < 9025 else False,  
                # is_teacher=False if reader.line_num < 9025 else True,
            )
           
    print("Users saved to the database.")



def add_teachers_from_csv(request):
   
    csv_file_path = "allteachers.csv"

    # Open the CSV file and iterate over its rows
    with open(csv_file_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users = User.objects.filter(is_teacher=True, teacher__isnull=True)
            # Randomly select a user object
            random_user = random.choice(users)
            # Create a new Student object for each row in the CSV file
            teacher =  Teacher.objects.create(
                user=random_user,
                date_of_birth=row['date_of_birth'],
                gender=row['gender'],
                marital_status=row['marital_status'],
                religion=row['religion'],
                nationality=row['nationality'],
                cnic=row['cnic'],
                office_number=row['office_number'],
                address=row['address'],
            )

    print("Teachers linked to users and saved to the database.")


def add_students_from_csv(request):

    # File path for allstudents.csv
    csv_file_path = "morestudents.csv"

    # Open the CSV file and iterate over its rows
    with open(csv_file_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users = User.objects.filter(is_student=True, student__isnull=True)
            # Randomly select a user object
            random_user = random.choice(users)
            # Create a new Student object for each row in the CSV file
            student = Student.objects.create(
                user=random_user,
                date_of_birth=row["date_of_birth"],
                gender=row["gender"],
                marital_status=row["marital_status"],
                religion=row["religion"],
                nationality=row["nationality"],
                cnic=row["cnic"],
                father_name=row["father_name"],
                father_occupation=row["father_occupation"],
                semester=row["semester"],
                address=row["address"],
            )

    print("Students linked to users and saved to the database.")


def generate_random_date_of_birth():
    # Generate a random year between 1995 and 2004
    year = random.randint(1994, 2004)
    # Generate a random month between 1 and 12
    month = random.randint(1, 12)
    # Generate a random day between 1 and the maximum number of days in the month
    max_day = (
        31
        if month in [1, 3, 5, 7, 8, 10, 12]
        else (
            30
            if month != 2
            else 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
        )
    )
    day = random.randint(1, max_day)
    return datetime(year, month, day).strftime("%Y-%m-%d")


def change_date_of_birth(request):
    # Define the path to your CSV file
    csv_file_path = "allstudents.csv"

    # Read the CSV file and generate random birth years for each entry
    updated_rows = []

    with open(csv_file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Generate a random date of birth
                row["date_of_birth"] = generate_random_date_of_birth()
                updated_rows.append(row)
            except ValueError:
                # Handle invalid date of birth
                pass

    # Write the updated rows to a new CSV file
    output_file_path = "allnewstudents.csv"

    with open(output_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)


def change_phone_numbers(request):
    # Define the path to your CSV file
    csv_file_path = "newmorestudents.csv"

    # Read the CSV file and generate random 11-digit phone numbers for each entry
    updated_rows = []

    with open(csv_file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Generate a random 11-digit phone number
            phone_number =''.join(random.choices(string.digits, k=13))
            # phone_number = 000
            row['cnic'] = phone_number
            updated_rows.append(row)

    # Write the updated rows to a new CSV file
    output_file_path = "morestudents.csv"

    with open(output_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)


def remove_duplicate_users(request):
    # Define the path to your CSV file
    csv_file_path = "morestudents.csv"

    # Read the CSV file and remove duplicates based on username
    unique_usernames = set()
    unique_rows = []

    with open(csv_file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row['cnic']
            if username not in unique_usernames:
                unique_usernames.add(username)
                unique_rows.append(row)

    # Write the unique rows to a new CSV file
    output_file_path = "newmorestudents.csv"

    with open(output_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)

    # # Return a response with a download link for the new CSV file
    # with open(output_file_path, mode='rb') as file:
    #     response = HttpResponse(file.read(), content_type='text/csv')
    #     response['Content-Disposition'] = 'attachment; filename="unique_users.csv"'
    #     return response


def import_semester_courses(request):
    # Path to CSV files
    semester_details_file = "semester_details.csv"
    all_courses_file = "allcourses.csv"

    # Read all courses from CSV
    all_courses_data = []
    with open(all_courses_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            all_courses_data.append(row["Course Name"])

    # Read semester details from CSV and create SemesterCourses instances
    with open(semester_details_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            semester_number = row["Semester Number"]
            degree_name = row["Degree"]

            # Fetch the corresponding degree
            degree = Degree.objects.get(degree_name=degree_name)

            # Create SemesterDetails instance if not already exists
            semester_details, created = SemesterDetails.objects.get_or_create(
                degree=degree, semester_number=semester_number
            )

            # Randomly select 6 courses from all courses
            selected_courses = random.sample(all_courses_data, 6)

            # Link selected courses with SemesterCourses
            semester_courses = SemesterCourses.objects.create(
                semester_details=semester_details
            )
            for course_name in selected_courses:
                course = Course.objects.get(course_name=course_name)
                semester_courses.courses.add(course)

    return HttpResponse("Semester courses imported successfully!")


def create_semester_details(request):
    # Define the file name for degrees
    degrees_file = "alldegrees.csv"

    # Open the CSV file containing degrees
    with open(degrees_file, mode="r", newline="") as file:
        # Create a CSV reader object
        reader = csv.reader(file)

        # Skip the header row if it exists
        next(reader, None)

        # Read the degrees from the file
        degrees = [row[0] for row in reader]

    # Define semester numbers
    semester_numbers = list(range(1, 9))

    # Define the file name for semester details
    file_name = "semester_details.csv"

    # Open the CSV file in write mode
    with open(file_name, mode="w", newline="") as file:
        # Create a CSV writer object
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(["Semester Number", "Degree"])

        # Write data for each degree and semester combination
        for degree in degrees:
            for semester_number in semester_numbers:
                writer.writerow([semester_number, degree])

    print(f"CSV data has been generated and saved to {file_name}.")


def import_semester_details_from_csv(request):
    file_path = "semester_details.csv"
    # Open the CSV file in read mode
    with open(file_path, mode="r") as file:
        # Create a CSV reader object
        reader = csv.reader(file)

        # Skip the header row
        next(reader)

        # Iterate over each row in the CSV file
        for row in reader:
            semester_number, degree_name = row

            # Get the Degree object from the database
            degree = Degree.objects.get(degree_name=degree_name)

            # Create the SemesterDetails object
            SemesterDetails.objects.create(
                semester_number=int(semester_number), degree=degree
            )


def read_csv(request):
    # File path for Maryam
    csv_file_path = "C:\\Users\\lenovo\\Documents\\smarteval\\smarteval\\courses.csv"
    department = Department.objects.get(
        department_name="Department of Strategic Studies (DSS)"
    )

    # Open the CSV file and iterate over its rows
    with open(csv_file_path, "r", newline="") as csvfile:
        for line in csvfile:
            # Create a new Course object for each row in the CSV file
            course = Course(
                course_name=line.strip(),
                department=department,
                theory_credit_hours=0,
                lab_credit_hours=0,
            )
            # Save the Course object to the database
            course.save()

    print("Courses saved to the database.")


def remove_duplicates(request):
    # Get a list of duplicate course names
    duplicate_course_names = (
        Course.objects.values("course_name")
        .annotate(count=Count("course_name"))
        .filter(count__gt=1)
    )
    # Iterate over duplicate course names
    for duplicate in duplicate_course_names:
        # Get all instances of the duplicate course
        duplicate_instances = Course.objects.filter(
            course_name=duplicate["course_name"]
        )
        # Keep the first instance and delete the rest
        for instance in duplicate_instances[1:]:
            instance.delete()
    print("Duplicates removed successfully.")


def scrape_data(request):
    # Set all department values to "Department of Humanities"
    department = Department.objects.get(department_name="Department of Cyber Security")
    # URL to scrape
    url = "https://www.au.edu.pk/Pages/Faculties/Computing_AI/Cyber_Security/dept_cyber_programdesc.aspx"

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # # Find all panel-body elements
    # panel_bodies = soup.find_all("div", class_="panel-body")
    # # table = soup.find("table", id="Table2")  # Replace "your_table_id_here" with the actual ID of the table

    # # Create a list to store course names
    # # course_names = []
    # course_names = set()

    # # Iterate over panel-body elements
    # for panel_body in panel_bodies:
    #     # Find all h4 elements within panel-body
    #     h4_elements = panel_body.find_all("h4")

    #     # Extract course names
    #     for h4 in h4_elements:
    #         # Remove everything before the "-" and the space after it
    #         course_name = re.sub(r"^[A-Z]+-\d+\s", "", h4.text.strip())
    #         course_names.add(course_name)

    # # Find all rows in the table
    # rows = table.find_all("tr")

    # # Iterate over rows and extract data from the second column
    # for row in rows:
    #     # Find all cells in the row
    #     cells = row.find_all("td")
    #     # Check if the row has at least two cells (for safety)
    #     if len(cells) >= 2:
    #         # Extract data from the second cell and append it to the list
    #         course_names.add(cells[1].text.strip())

    # Create Course objects and save them in the database
    # Find the div with class 'table-responsive'
    table_div = soup.find("div", class_="table-responsive")

    # Initialize an empty list to store course titles from the specified column
    course_titles = []

    # Find the table element within the div
    table = table_div.find("table")

    # Find all rows in the table
    rows = table.find_all("tr")

    # Iterate over rows and extract data from the third column (index 2)
    for row in rows:
        # Find all cells in the row
        cells = row.find_all("td")
        # Check if the row has at least three cells (for safety) and extract data from the third cell
        if len(cells) >= 3:
            # Assuming the course titles are in the third column, extract and append to the list
            course_title = cells[2].text.strip()
            course_titles.append(course_title)

    # Find all subsequent tables
    subsequent_tables = soup.find_all("table")[1:]

    # Iterate through subsequent tables and extract data from the specified column
    for table in subsequent_tables:
        # Find all rows in the table
        rows = table.find_all("tr")
        # Iterate over rows and extract data from the third column (index 2)
        for row in rows:
            # Find all cells in the row
            cells = row.find_all("td")
            # Check if the row has at least three cells (for safety) and extract data from the third cell
            if len(cells) >= 3:
                # Assuming the course titles are in the third column, extract and append to the list
                course_title = cells[2].text.strip()
                course_titles.append(course_title)

    for name in course_titles:
        # You can set credit hours accordingly
        course = Course(
            course_name=name,
            theory_credit_hours=0,
            lab_credit_hours=0,
            department=department,
        )
        course.save()

    print("Courses added to the database.")


def faculty_registration(request):
    if request.method == "POST":
        # Handle the form submission
        return saveFaculty(request)
    else:
        departments = Department.objects.all()
        # print(departments)
        # Render the signup page for GET requests
        return render(request, "portals/Faculty_Registration.html",{'departments': departments})


def saveFaculty(request):
    if request.method == "POST":
        # Get form input values
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        profile_picture = request.FILES.get("profile_picture")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        username = request.POST.get("username")
        birthday = request.POST.get("birthday")
        gender = request.POST.get("gender")
        marital_status = request.POST.get("marital_status")
        religion = request.POST.get("religion")
        Nationality = request.POST.get("Nationality")
        CNIC = request.POST.get("CNIC")
        Departmentt = request.POST.get("Department")
        Address = request.POST.get("Address")

        department=Department.objects.filter(department_name=Departmentt).first()




        is_teacher = True

        # Check if the phone, email, or username already exists in the database
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists")
            return render(
                request,
                "portals/Faculty_Registration.html",
                {
                    "phone_error": "Phone number already exists",
                    "email_error": "",
                    "username_error": "",
                },
            )

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(
                request,
                "portals/Faculty_Registration.html",
                {
                    "email_error": "Email already exists",
                    "phone_error": "",
                    "username_error": "",
                },
            )

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(
                request,
                "portals/Faculty_Registration.html",
                {
                    "username_error": "Username already exists",
                    "phone_error": "",
                    "email_error": "",
                },
            )

        # Perform other validations and save the user if all validations pass
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(
                request,
                "portals/Faculty_Registration.html",
                {
                    "password_error": "Passwords do not match",
                    "phone_error": "",
                    "email_error": "",
                    "username_error": "",
                },
            )

        # Create the user object
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            profile_picture=profile_picture,
            password=password,
            username=username,
            is_teacher=is_teacher,
        )
        # user.save()
        teacher = Teacher(
            user=user,
            department=department,
            date_of_birth=birthday,
            gender=gender,
            marital_status=marital_status,
            religion=religion,
            nationality=Nationality,
            cnic=CNIC,
            address=Address,
        )
        teacher.save()

        # Redirect to the signin page or any other desired page
        return redirect("portals:faculty-login")

    # Handle invalid request method
    return redirect("portals:faculty-login")


def student_registration(request):
    if request.method == "POST":
        # Handle the form submission
        return saveStudent(request)
    else:
        # Render the signup page for GET requests
        return render(request, "portals/Student_Registration.html")


def saveStudent(request):
    if request.method == "POST":
        # Get form input values
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        profile_picture = request.FILES.get("profile_picture")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        username = request.POST.get("username")
        birthday = request.POST.get("birthday")
        gender = request.POST.get("gender")
        marital_status = request.POST.get("marital_status")
        religion = request.POST.get("religion")
        Nationality = request.POST.get("Nationality")
        CNIC = request.POST.get("CNIC")
        Father_Name = request.POST.get("Father Name")
        Father_Occupation = request.POST.get("Father_Occupation")
        Semester = request.POST.get("Semester")
        Degree = request.POST.get("Degree")
        Address = request.POST.get("Address")







        is_student = True
        is_teacher = False

        # Check if the phone, email, or username already exists in the database
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists")
            return render(
                request,
                "portals/Student_Registration.html",
                {
                    "phone_error": "Phone number already exists",
                    "email_error": "",
                    "username_error": "",
                },
            )

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(
                request,
                "portals/Student_Registration.html",
                {
                    "email_error": "Email already exists",
                    "phone_error": "",
                    "username_error": "",
                },
            )

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(
                request,
                "portals/Student_Registration.html",
                {
                    "username_error": "Username already exists",
                    "phone_error": "",
                    "email_error": "",
                },
            )

        # Perform other validations and save the user if all validations pass
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(
                request,
                "portals/Student_Registration.html",
                {
                    "password_error": "Passwords do not match",
                    "phone_error": "",
                    "email_error": "",
                    "username_error": "",
                },
            )

        # Create the user object
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            profile_picture=profile_picture,
            password=password,
            username=username,
            is_student=is_student,
            is_teacher=is_teacher,
        )
        # user.save()
        student = Student(
            user=user,
            date_of_birth=birthday,
            gender=gender,
            marital_status=marital_status,
            religion=religion,
            nationality=Nationality,
            cnic=CNIC,
            father_name=Father_Name,
            father_occupation=Father_Occupation,
            semester=Semester,



        )
        student.save()

        # Redirect to the signin page or any other desired page
        return redirect("portals:student-login")

    # Handle invalid request method
    return redirect("portals:student-login")


def student_login_view(request):
    find_available_time_slots(request)
    # populate_semester_course_grades(request)
    # generate_marks_view(request)
    # test_mapping()
    # assign_classes_to_sections(request)
    # create_section_courses_mapping()
    # create_course_teacher_mapping()
    # populate_teacher_sections_taught()
    # assign_teachers_to_sections(request)
    # assign_courses_to_semesters(request)
    # generate_classes(request)
    # create_class_rooms(request)
    # assign_sections_to_students(request)
    # distribute_students_semesters()
    # distribute_students_evenly()
    # assign_courses_to_teachers(request)
    # assign_departments_to_teachers()
    # update_departments(request)
    # add_teachers_from_csv(request)
    # add_students_from_csv(request)
    # read_users_from_csv(request)
    # change_date_of_birth(request)
    # change_phone_numbers(request)
    # remove_duplicate_users(request)
    # generate_unique_data(100, 'student_data.csv')
    # import_semester_courses(request)
    # create_semester_details(request)
    # import_semester_details_from_csv(request)
    # scrape_data(request)
    # remove_duplicates(request)
    # read_csv(request)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        print(f"Attempting login for username: {username}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"Authentication successful for user: {username}")
            if user.is_student:
                print(f"User {username} is a student.")
                login(request, user)
                messages.success(request, "Login successful!")
                print(f"Login successful for user: {username}")
                return redirect("portals:student-dashboard")
            else:
                print(f"User {username} is not a student.")
                messages.error(request, "Invalid username or password.")
                print(f"Login failed for user: {username}")
                return render(
                    request,
                    "portals/Student_login.html",
                    {"error": "Invalid username or password."},
                )

        else:
            print(f"Authentication failed for user: {username}")
            messages.error(request, "Invalid username or password.")
            print(f"Login failed for user: {username}")
            return render(
                request,
                "portals/Student_login.html",
                {"error": "Invalid username or password."},
            )

    return render(request, "portals/Student_login.html")


def faculty_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        print(f"Attempting login for username: {username}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"Authentication successful for user: {username}")
            if user.is_teacher:
                print(f"User {username} is a teacher.")
                login(request, user)
                messages.success(request, "Login successful!")
                print(f"Login successful for user: {username}")
                return redirect("portals:dashboard")
            else:
                print(f"User {username} is not a teacher.")
                messages.error(request, "Invalid username or password.")
                print(f"Login failed for user: {username}")
                return render(
                    request,
                    "portals/Faculty_login.html",
                    {"error": "Invalid username or password."},
                )
        else:
            print(f"Authentication failed for user: {username}")
            messages.error(request, "Invalid username or password.")
            print(f"Login failed for user: {username}")
            return render(
                request,
                "portals/Faculty_login.html",
                {"error": "Invalid username or password."},
            )

    return render(request, "portals/Faculty_login.html")


def log_out(request):
    user = request.user
    logout(request)
    if user.is_student:
        return redirect('portals:student-login')  
    elif user.is_teacher:
        return redirect('portals:faculty-login')  
    else: 
        return redirect('portals:student-login') 



def get_programs(request):
    department_id = request.GET.get("department_id")
    programs = Program.objects.filter(department_id=department_id).values(
        "id", "program_name"
    )
    return JsonResponse(list(programs), safe=False)


# ---------------------------- GENERATE PAPER ------------------
# Define keywords for Bloom's Taxonomy levels
# bt_keywords = {
#     "remember": ["define", "list", "recall", "identify", "name", "state", "describe"],
#     "understand": ["explain", "describe", "summarize", "paraphrase", "interpret"],
#     "apply": ["solve", "use", "apply", "demonstrate", "implement", "execute"],
#     "analyze": ["analyze", "compare", "contrast", "differentiate", "examine"],
#     "evaluate": ["evaluate", "justify", "assess", "critique", "recommend"],
#     "create": ["create", "design", "construct", "develop", "formulate"]
# }
@csrf_exempt
def generate_paper(request):
    try:
        if request.method == "POST":
            print(request.body)  # Print raw data received to check if CLOs are present
            data = json.loads(request.body)
            print("Processed Data:", data)  # Check structured data
            print("Received CLOs:", data.get('questionCLOs'))
            print("Received GAs:", data.get('questionGAs'))

            data = json.loads(request.body)
            subject_id = data.get("subject_id")
            subject_name = subject_id
            select_questions = int(data.get("selectQuestions"))
            question_parts = data.get("questionParts") or ['N/A'] * select_questions
            question_topics = data.get("questionTopics") or [''] * select_questions
            # Check if all topics are provided
            if any(not topic.strip() for topic in question_topics):
                return JsonResponse({"success": False, "error": "All question topics are mandatory."}, status=400)
            question_bt_levels = data.get("questionBTLevels") or ['N/A'] * select_questions
            question_complexities = data.get("questionComplexities") or ['N/A'] * select_questions
            question_keywords = data.get("questionKeywords") or [[''] * select_questions]
            

            prompts = []
            subject_name = data.get("subject_id", "the subject")  # Assuming you fetch subject_name from data
            select_questions = int(data.get("selectQuestions", 0))

            prompt = f"The question paper is on the topic of {subject_name}. Generate {select_questions} questions with the following specifications:\n"

            prompts.append(prompt)

            for i in range(select_questions):
                question_prompt = f"Question {i + 1}:\n"
                question_prompt += f"Topic: {question_topics[i]}\n"
                question_prompt += f"Instructions: {', '.join(question_keywords[i])}\n"
                question_prompt += f"BT Level: {question_bt_levels[i].capitalize()}\n"
                question_prompt += f"Complexity Level: {question_complexities[i].capitalize()}\n"
                question_prompt += f"Number of parts: {question_parts[i]} parts.\n"
                question_prompt += "Each part should be distinct and clearly numbered. The question must meet the selected BT Level.\n"
                prompts.append(question_prompt)

            prompt = "\n".join(prompts)

            prompt2 = []

            for i in range(select_questions):
                question_prompt = f"Question {i + 1}:\n"
                question_prompt += f"Topic: {question_topics[i]}\n"
                question_prompt += f"Instructions: {', '.join(question_keywords[i])}\n"
                question_prompt += f"BT Level: {question_bt_levels[i].capitalize()}\n"
                question_prompt += f"Complexity Level: {question_complexities[i].capitalize()}\n"
                question_prompt += f"Number of parts: {question_parts[i]} parts.\n"
                question_prompt += "Each part should be distinct and clearly numbered.\n"
                prompts.append(question_prompt)
            print("Generated Prompt: ", prompt)

            # Make API call to ChatGPT or any other service to generate the questions
            api_key = "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"
            endpoint_url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            response = requests.post(endpoint_url, json=payload, headers=headers)

            # Log the ChatGPT API response
            logger.info(f"ChatGPT API response: {response.text}")

            # Process response from ChatGPT API
            if response.status_code == 200:
                response_data = response.json()
                paper_prompts = []
                for choice in response_data.get("choices", []):
                    content = choice.get("message", {}).get("content", "").strip()
                    if content:
                        # Split content into individual questions based on "Question X:" pattern
                        questions = re.split(r'\n(?=Question \d+:)', content)
                        for question in questions:
                            paper_prompts.append(question)

                return JsonResponse({
                        "success": True,
                        "paper_prompts": paper_prompts,
                        "questionBTLevels": question_bt_levels,
                        "questionComplexities": question_complexities,
                        "subject_name": subject_id
                    })            
            else:
                logger.error(f"Failed to generate paper: {response.status_code} - {response.text}")
                return JsonResponse({"success": False, "error": "Failed to generate paper"}, status=500)

        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    except Exception as e:
        logger.error(f"Error in generate_paper view: {e}")
        return JsonResponse({"success": False, "error": "An error occurred while generating the paper"}, status=500)



@csrf_exempt
def generate_chatgpt_response(request):
    pass


# views.py
@csrf_exempt
def regenerate_question(request):
    try:
        if request.method == "POST":
            question_data = json.loads(request.body)
            topic = question_data.get("topic")
            keywords = question_data.get("keywords")
            complexity = question_data.get("complexity")
            parts = question_data.get("parts")
            question_index = question_data.get("questionIndex")
            bt_level = question_data.get("bt_level", "N/A").capitalize()

            # Construct the prompt for regenerating the specific question
            prompt = f"Question {question_index}:\n"
            prompt += f"Topic: {topic}\n"
            prompt += f"Instructions: {', '.join(keywords)}\n"
            prompt += "BT Level (Choose one):\n"
            bt_levels = ["N/A", "Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
            for level in bt_levels:
                prompt += f"- {level}\n"
            prompt += f"Selected BT Level: {bt_level}\n"
            prompt += f"Complexity Level: {complexity.capitalize()}\n"
            prompt += f"Generate a {complexity} question with {parts} parts.\n"
            prompt += "Each part should be distinct and clearly numbered.\n"

            logger.info(f"Generated prompt: {prompt}")

            # Call the API to regenerate only this specific question
            api_key = "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"
            endpoint_url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            response = requests.post(endpoint_url, json=payload, headers=headers)

            logger.info(f"ChatGPT API response: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                question_prompt = response_data.get("choices", [])[0].get("message", {}).get("content", "").strip()

                return JsonResponse(
                    {"success": True, "question_prompt": question_prompt, "questionIndex": question_index}
                )
            else:
                logger.error(f"Failed to regenerate question: {response.status_code} - {response.text}")
                return JsonResponse({"success": False, "error": "Failed to regenerate question"}, status=500)

        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    except Exception as e:
        logger.error(f"Error in regenerate_question view: {e}")
        return JsonResponse({"success": False, "error": "An error occurred while regenerating the question"}, status=500)




def student_marks_api_view(request, student_id, course_id):
    # Retrieve student object
    student = get_object_or_404(Student, StudentID=student_id)

    # Retrieve semester marks data for the student
    semester_marks_data = SemesterMarksData.objects.filter(student=student)

    # Initialize data lists
    labels = []
    quiz_marks_data = []
    assignment_marks_data = []
    presentation_marks_data = []
    semester_project_marks_data = []
    mids_marks_data = []
    final_marks_data = []

    for marks_data in semester_marks_data:
        labels.append(f"Semester {marks_data.semester_number}")
        # print(labels)

        # Retrieve marks data for each category
        quiz_marks = list(QuizMarks.objects.filter(semester_marks_data=marks_data).values_list('quiz_marks', flat=True))
        assignment_marks = list(AssignmentMarks.objects.filter(semester_marks_data=marks_data).values_list('assignment_marks', flat=True))
        presentation_marks = list(PresentationMarks.objects.filter(semester_marks_data=marks_data).values_list('presentation_marks', flat=True))
        # Append data to respective lists
        quiz_marks_data.append(sum(quiz_marks) if quiz_marks else 0)
        assignment_marks_data.append(sum(assignment_marks) if assignment_marks else 0)
        presentation_marks_data.append(sum(presentation_marks) if presentation_marks else 0)
        semester_project_marks_data.append(marks_data.semester_project_marks)
        mids_marks_data.append(marks_data.mids_marks)
        final_marks_data.append(marks_data.final_marks)

    # Construct response data
    response_data = {
        'labels': labels,
        'quiz_marks': quiz_marks_data,
        'assignment_marks': assignment_marks_data,
        'presentation_marks': presentation_marks_data,
        'semester_project_marks': semester_project_marks_data,
        'mids_marks': mids_marks_data,
        'final_marks': final_marks_data,
    }
    print(quiz_marks)

    return JsonResponse(response_data)

