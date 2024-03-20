from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from portals.models import Student, User


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

def student_registration(request):
    if request.method == 'POST':
        # Handle the form submission
        return saveStudent(request)
    else:
        # Render the signup page for GET requests
        return render(request, "portals/Student_Registration.html")
    
def saveStudent(request):
    if request.method == 'POST':
        # Get form input values
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        profile_picture = request.FILES.get('profile_picture')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        username = request.POST.get('username')
        is_student = True

        # Check if the phone, email, or username already exists in the database
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already exists')
            return render(request, 'portals/Student_Registration.html', {'phone_error': 'Phone number already exists', 'email_error': '', 'username_error': ''})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'portals/Student_Registration.html', {'email_error': 'Email already exists', 'phone_error': '', 'username_error': ''})


        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'portals/Student_Registration.html', {'username_error': 'Username already exists', 'phone_error': '', 'email_error': ''})


        # Perform other validations and save the user if all validations pass
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'portals/Student_Registration.html', {'password_error': 'Passwords do not match', 'phone_error': '', 'email_error': '', 'username_error': ''})

        # Create the user object
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            profile_picture=profile_picture,
            password=password,
            username=username,
            is_student=is_student
        )
        # user.save()
        student = Student(
            user=user,
           
        )
        student.save()

        # Redirect to the signin page or any other desired page
        return redirect('portals:student-login')

    # Handle invalid request method
    return redirect('portals:student-login')


def student_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Attempting login for username: {username}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"Authentication successful for user: {username}")
            if user.is_student:
                print(f"User {username} is a student.")
                login(request, user)
                messages.success(request, 'Login successful!')
                print(f"Login successful for user: {username}")
                return redirect('portals:student-dashboard')
            else:
                print(f"User {username} is not a student.")
                messages.error(request, 'Invalid username or password.')
                print(f"Login failed for user: {username}")
                return render(request, 'portals/Student_login.html', {'error': 'Invalid username or password.'})

        else:
            print(f"Authentication failed for user: {username}")
            messages.error(request, 'Invalid username or password.')
            print(f"Login failed for user: {username}")
            return render(request, 'portals/Student_login.html', {'error': 'Invalid username or password.'})


    return render(request, 'portals/Student_login.html')


def faculty_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Attempting login for username: {username}")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_teacher:
            login(request, user)
            messages.success(request, 'Login successful!')
            print(f"Login successful for user: {username}")
            return redirect('portals:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            print(f"Login failed for user: {username}")

    return render(request, 'portals/faculty_login.html')