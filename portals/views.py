import csv
from venv import logger
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
import re
import random
import string
from bs4 import BeautifulSoup
from django.http import JsonResponse
from portals.decorators import student_required, teacher_required
from .models import Degree, Program, Section, SemesterCourses, SemesterDetails, TeacherCoursesTaught
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


# @login_required(login_url='portals:faculty-login')
# @teacher_required()
# def home(request):
#     return render(request, "portals/Faculty_Profile.html")


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_class_info_view(request):
    return render(request, "portals/Faculty_ClassInfo.html")
    

@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_dashboard_view(request):
    return render(request, "portals/Faculty_Dashboard.html")


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_display_classes_view(request):
    return render(request, "portals/Faculty_DisplayClasses.html")


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_feedback_view(request):
    return render(request, "portals/Faculty_Feedbacks.html")



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


@login_required(login_url='portals:faculty-login')
def faculty_marks_entry_view(request):
    return render(request, "portals/Faculty_MarksEntry.html")


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_profile_view(request):
    return render(request, "portals/Faculty_Profile.html")


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_student_info_view(request):
    return render(request, "portals/Faculty_StudentInfo.html")


@login_required(login_url='portals:faculty-login')
@teacher_required()
def faculty_student_marks_entry_view(request):
    return render(request, "portals/Faculty_StudentsMarksEntry.html")


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



# def assign_sections_to_students(request):
#     # Get all degrees
#     degrees = Degree.objects.filter(degree_name__startswith='B')
    
#     for degree in degrees:
#         # Get all semesters of the degree
#         semesters = set(Student.objects.filter(degree=degree).values_list('semester', flat=True))
        
#         for semester in semesters:
#             # Get all students in the current semester of the degree
#             students = Student.objects.filter(degree=degree, semester=semester)
            
#             # Sort students by date of birth or any other criteria you prefer
#             sorted_students = students.order_by('StudentID')
            
#             # Calculate the total number of students
#             total_students = sorted_students.count()
            
#             # Calculate the number of sections needed
#             num_sections = (total_students // 30) + (1 if total_students % 30 != 0 else 0)
            
#             # Create sections and assign students to each section
#             for i in range(num_sections):
#                 section_name = chr(65 + i)  # Convert integer to corresponding alphabet (A, B, C, ...)
#                 section = Section.objects.create(section_name=section_name, degree=degree, semester=semester)
                
#                 # Calculate the range of students to assign to this section
#                 start_index = i * 30
#                 end_index = min((i + 1) * 30, total_students)
                
#                 # Assign students to the section
#                 students_to_assign = sorted_students[start_index:end_index]
#                 for student in students_to_assign:
#                     student.section = section
#                     student.save()

#     return "Students assigned sections successfully"


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
        # Render the signup page for GET requests
        return render(request, "portals/Faculty_Registration.html")


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
        )
        student.save()

        # Redirect to the signin page or any other desired page
        return redirect("portals:student-login")

    # Handle invalid request method
    return redirect("portals:student-login")


def student_login_view(request):
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
    logout(request)
    return redirect('portals:faculty-login')



def get_programs(request):
    department_id = request.GET.get("department_id")
    programs = Program.objects.filter(department_id=department_id).values(
        "id", "program_name"
    )
    return JsonResponse(list(programs), safe=False)


# ---------------------------- GENERATE PAPER ------------------

@csrf_exempt
def generate_paper(request):
    try:
        if request.method == "POST":
            # Extract data from AJAX request
            data = json.loads(request.body)
            subject_id = data.get("subject_id")
            subject_name = subject_id
            select_questions = data.get("selectQuestions")
            question_parts = data.get("questionParts") or []
            question_topics = data.get("questionTopics") or []
            question_complexities = data.get("questionComplexities") or []
            question_keywords = data.get("questionKeywords") or []

            # Check if the question topics, complexities, and keywords have the required length
            if (
                not question_parts
                or not question_topics
                or not question_complexities
                or not question_keywords
            ):
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Incomplete data for question topics, complexities, keywords, or parts",
                    },
                    status=400,
                )

            # Ensure the lists have the same length as select_questions
            required_length = int(select_questions)
            if (
                len(question_parts) != required_length
                or len(question_topics) != required_length
                or len(question_complexities) != required_length
                or len(question_keywords) != required_length
            ):
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Inconsistent data length for question topics, complexities, keywords, or parts",
                    },
                    status=400,
                )

            # Construct the overall prompt
            prompt = f"The question paper is on the topic of {subject_name}. Generate {select_questions} bachelor level exam questions with the following specifications:\n"

            for i in range(required_length):
                prompt += f"\nQuestion {i + 1}:\n"
                prompt += f"Topic: {question_topics[i]}\n"
                prompt += f"Keywords: {question_keywords[i]}\n"
                prompt += f"Complexity: {question_complexities[i].capitalize()}\n"
                prompt += f"Generate a {question_complexities[i]} question with {question_parts[i]} parts.\n"
            
            # Log the generated prompt
            logger.info(f"Generated prompt: {prompt}")

            # Call ChatGPT API to generate response
            api_key = "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"
            endpoint_url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                # Add other parameters as needed
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
                        # Append each question's prompt to the paper_prompts list
                        for question in questions:
                            paper_prompts.append(question)
               

                return JsonResponse({"success": True, "paper_prompts": paper_prompts, "subject_name": subject_name})
            else:
                logger.error(
                    f"Failed to generate paper: {response.status_code} - {response.text}"
                )
                return JsonResponse(
                    {"success": False, "error": "Failed to generate paper"}, status=500
                )

        # Return error if request method is not POST
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    except Exception as e:
        logger.error(f"Error in generate_paper view: {e}")
        return JsonResponse(
            {"success": False, "error": "An error occurred while generating the paper"},
            status=500,
        )


@csrf_exempt
def generate_chatgpt_response(request):
    # This view is not needed anymore since the response is already generated in the generate_paper view
    pass


# views.py
@csrf_exempt
def regenerate_question(request):
    if request.method == "POST":
        # Extract question data from AJAX request
        question_data = json.loads(request.body)
        topic = question_data.get("topic")
        keywords = question_data.get("keywords")
        complexity = question_data.get("complexity")
        parts = question_data.get("parts")
        question_index = question_data.get("questionIndex")

        # Construct the prompt based on the received question data
        prompt = f"Regenerate the question based on the following points.\n Topic: {topic}\nKeywords: {', '.join(keywords)}\nComplexity: {complexity.capitalize()}\nGenerate a {complexity} question with {parts} parts.\n Clearly mention all parts like Part 1, Part 2 and each part should begin at new line."

        # Log the generated prompt
        logger.info(f"Generated prompt: {prompt}")

        # Call ChatGPT API to generate response
        api_key = "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"
        endpoint_url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            # Add other parameters as needed
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        response = requests.post(endpoint_url, json=payload, headers=headers)

        # Log the ChatGPT API response
        logger.info(f"ChatGPT API response: {response.text}")

        # Return the new question prompt as JSON response
        if response.status_code == 200:
            response_data = response.json()
            question_prompt = (
                response_data.get("choices", [])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            print("Question Prompt")
            print(question_prompt)
            return JsonResponse(
                {
                    "success": True,
                    "question_prompt": question_prompt,
                    "questionIndex": question_index,
                }
            )
        else:
            logger.error(
                f"Failed to regenerate question: {response.status_code} - {response.text}"
            )
            return JsonResponse(
                {"success": False, "error": "Failed to regenerate question"}, status=500
            )

    # Return error if request method is not POST
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)