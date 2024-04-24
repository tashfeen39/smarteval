import csv
from django.core.management.base import BaseCommand
from portals.models import Degree 

class Command(BaseCommand):
    help = 'Export all degrees to a CSV file'

    def handle(self, *args, **kwargs):
        degrees = Degree.objects.all()
        filename = 'alldegrees.csv'

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Degree Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for degree in degrees:
                writer.writerow({'Degree Name': degree.degree_name})

        self.stdout.write(self.style.SUCCESS(f'Successfully exported all degrees to {filename}'))