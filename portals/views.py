import csv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
import requests
import re
from bs4 import BeautifulSoup
from django.http import JsonResponse
from .models import Program
from django.db.models import Count
from portals.models import Course, Department, Student, Teacher, User


def home(request):
    return render(request, "portals/Faculty_Profile.html")


def faculty_class_info_view(request):
    return render(request, "portals/Faculty_ClassInfo.html")


def faculty_dashboard_view(request):
    return render(request, "portals/Faculty_Dashboard.html")


def faculty_display_classes_view(request):
    return render(request, "portals/Faculty_DisplayClasses.html")


def faculty_feedback_view(request):
    return render(request, "portals/Faculty_Feedbacks.html")


def faculty_generate_exam_view(request):
    return render(request, "portals/Faculty_GenerateExam.html")


def faculty_grading_view(request):
    return render(request, "portals/Faculty_Grading.html")


def faculty_marks_entry_view(request):
    return render(request, "portals/Faculty_MarksEntry.html")


def faculty_profile_view(request):
    return render(request, "portals/Faculty_Profile.html")


def faculty_student_info_view(request):
    return render(request, "portals/Faculty_StudentInfo.html")


def faculty_student_marks_entry_view(request):
    return render(request, "portals/Faculty_StudentsMarksEntry.html")


def student_dashboard_view(request):
    return render(request, "portals/Student_Dashboard.html")


def student_registeredcourses_view(request):
    return render(request, "portals/Student_RegisteredCourses.html")


def student_timetable_view(request):
    return render(request, "portals/Student_TimeTable.html")


def student_report_view(request):
    return render(request, "portals/Student_Report.html")


def student_feedback_view(request):
    return render(request, "portals/Student_Feedback.html")


def student_profile_view(request):
    return render(request, "portals/Student_Profile.html")


def student_subjectwisereport_view(request):
    return render(request, "portals/Student_SubjectWiseReport.html")

def read_csv(request):
    csv_file_path = 'C:\\Users\\lenovo\\Documents\\smarteval\\smarteval\\courses.csv'
    department = Department.objects.get(
        department_name="Department of Computer Science"
    )

    # Open the CSV file and iterate over its rows
    with open(csv_file_path, 'r', newline='') as csvfile:
        for line in csvfile:
            # Create a new Course object for each row in the CSV file
            course = Course(
                course_name = line.strip(),
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
    department = Department.objects.get(
        department_name="Department of Cyber Security"
    )
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


def get_programs(request):
    department_id = request.GET.get("department_id")
    programs = Program.objects.filter(department_id=department_id).values("id", "program_name")
    return JsonResponse(list(programs), safe=False)

