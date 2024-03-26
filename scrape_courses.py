import sys
from portals.models import Course
import os
import django
import requests
from bs4 import BeautifulSoup


# Add the Django project's root directory to the Python path
sys.path.append('/Users/tashfeen/Developer/smarteval')

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarteval.settings")
django.setup()


# URL to scrape
url = "https://www.au.edu.pk/Pages/Faculties/SocialSciences/Departments/Humanities/dept_humanities_course_desc.aspx"

# Send a GET request to the URL
response = requests.get(url)

# Parse HTML content
soup = BeautifulSoup(response.content, "html.parser")

# Find all panel-body elements
panel_bodies = soup.find_all("div", class_="panel-body")

# Create a list to store course names
course_names = []

# Iterate over panel-body elements
for panel_body in panel_bodies:
    # Find all h4 elements within panel-body
    h4_elements = panel_body.find_all("h4")

    # Extract course names
    for h4 in h4_elements:
        # Remove everything before the "-" and the space after it
        course_name = h4.text.strip().split("-")[-1].strip()
        course_names.append(course_name)

# Create Course objects and save them in the database
for name in course_names:
    # You can set credit hours accordingly
    course = Course(course_name=name, theory_credit_hours=0,
                    lab_credit_hours=0)
    course.save()

print("Courses added to the database.")
