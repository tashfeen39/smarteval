import csv
from django.core.management.base import BaseCommand
from portals.models import Course 

class Command(BaseCommand):
    help = 'Export all course names to a CSV file'

    def handle(self, *args, **kwargs):
        courses = Course.objects.all()
        filename = 'allcourses.csv'

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Course Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for course in courses:
                writer.writerow({'Course Name': course.course_name})

        self.stdout.write(self.style.SUCCESS(f'Successfully exported all courses to {filename}'))